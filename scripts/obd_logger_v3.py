#!/usr/bin/env python3
"""
OBD2 Logger v3 - Seat Toledo 2, 1.9 TDI ASV
Automatyczne łączenie przez Bluetooth + zbieranie wszystkich danych
"""
import socket
import time
import sys
import datetime
import os
import subprocess
import threading

OBD_MAC = "A2:2A:19:04:00:00"
LOG_FILE = "/tmp/obd_dane.txt"

def recv_all(sock, timeout=1.5):
    if not sock: return ""
    sock.settimeout(timeout)
    data = b""
    try:
        while True:
            chunk = sock.recv(4096)
            if not chunk: break
            data += chunk
            if b">" in data: break
    except socket.timeout:
        pass
    except:
        return ""
    return data.decode(errors="replace").strip()

def parse(resp, pid, nbytes=1, scale=1, offset=0):
    if not resp: return None
    resp = resp.replace(" ", "").replace("\r","").replace("\n","").replace(">","")
    idx = resp.find(f"41{pid:02X}")
    if idx < 0: idx = resp.find(f"4{pid:02X}")
    if idx >= 0:
        d = resp[idx+4:]
        if len(d) >= nbytes*2:
            try: return int(d[:nbytes*2], 16) * scale + offset
            except: pass
    for p in resp.split():
        p = p.strip()
        if len(p) >= 2 and all(c in "0123456789ABCDEFabcdef" for c in p):
            if len(p) >= nbytes*2:
                try: return int(p[:nbytes*2], 16) * scale + offset
                except: pass
    return None

def ensure_paired():
    """Sprawdź czy sparowane, jeśli nie - sparuj"""
    r = subprocess.run(["bluetoothctl", "info", OBD_MAC],
                      capture_output=True, text=True, timeout=5)
    if "Paired: no" in r.stdout:
        print("[*] Parowanie z ELM327 (PIN: 1234)...")
        subprocess.run(["bluetoothctl", "trust", OBD_MAC],
                      capture_output=True, timeout=10)
        subprocess.run(["bluetoothctl", "pair", OBD_MAC],
                      capture_output=True, timeout=30)

def trigger_bt_connect():
    """Uruchom bluetoothctl connect w tle na chwilę"""
    p = subprocess.Popen(["bluetoothctl", "connect", OBD_MAC],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(4)
    p.kill()
    p.wait()

def main():
    print("=" * 75)
    print("OBD2 Logger v3 - Seat Toledo 2, 1.9 TDI ASV")
    print("=" * 75)

    # Init log file
    if not os.path.exists(LOG_FILE) or os.path.getsize(LOG_FILE) == 0:
        with open(LOG_FILE, "w") as f:
            f.write("time,rpm,maf,map,boost,coolant,intake,speed,timing,fuel_p\n")

    # Ensure paired
    ensure_paired()

    print("[*] Łączenie z ELM327 przez Bluetooth...")
    print("[*] (jeśli to pierwsze połączenie, odłącz i podłącz ELM327)")
    print()

    s = None
    for attempt in range(60):  # 5 minutes max
        # Trigger Bluetooth connection
        trigger_bt_connect()

        # Try socket
        try:
            s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
            s.settimeout(5)
            s.connect((OBD_MAC, 1))
            break
        except Exception as e:
            s = None
            sys.stdout.write(f"\r[*] Próba {attempt+1}/60 - {str(e)[:30]}  ")
            sys.stdout.flush()
            time.sleep(3)

    if not s:
        print("\n[-] Nie można połączyć. Spróbuj ręcznie:")
        print(f"  bluetoothctl connect {OBD_MAC}")
        print("a potem uruchom skrypt ponownie.")
        return

    print("\n[+] Połączono przez Bluetooth!")

    # Init ELM327
    s.setblocking(False)
    for cmd_str, wait in [("ATZ", 1.5), ("ATE0", 0.3), ("ATS0", 0.2), ("ATH0", 0.2)]:
        s.sendall((cmd_str + "\r").encode())
        time.sleep(wait)
    recv_all(s, 1.5)
    print("[+] ELM327 zainicjalizowany")

    # Warmup - find protocol
    print("[*] Szukanie protokołu OBD2...", end=" ", flush=True)
    rpm = None
    for i in range(20):
        s.sendall(b"010C\r")
        time.sleep(0.8)
        resp = recv_all(s, 1.0)
        rpm = parse(resp, 0x0C, 2, 0.25)
        if rpm:
            print(f"OK! RPM={rpm:.0f}")
            break
    if not rpm:
        print("FAIL - ECU nie odpowiada")
        return

    print(f"\n{'Czas':>8} | {'RPM':>5} | {'MAF':>5} | {'MAP':>3} | {'Boost':>5} | {'°C':>3} | {'km/h':>3} | {'Zapł':>4}")
    print("-" * 65)

    last_reconnect = time.time()
    reconnect_interval = 30  # reconnect every 30s to prevent clone hang

    try:
        while True:
            # Reconnect periodically to prevent clone hang
            if time.time() - last_reconnect > reconnect_interval:
                print("\n[*] Reconnect...")
                s.close()
                trigger_bt_connect()
                time.sleep(2)
                s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
                s.settimeout(5)
                s.connect((OBD_MAC, 1))
                s.setblocking(False)
                for cmd_str, wait in [("ATZ", 1.5), ("ATE0", 0.3), ("ATS0", 0.2), ("ATH0", 0.2)]:
                    s.sendall((cmd_str + "\r").encode())
                    time.sleep(wait)
                recv_all(s, 1.5)
                # Warmup again
                for i in range(10):
                    s.sendall(b"010C\r")
                    time.sleep(0.5)
                    resp = recv_all(s, 1.0)
                    rpm = parse(resp, 0x0C, 2, 0.25)
                    if rpm: break
                last_reconnect = time.time()

            # Read RPM
            s.sendall(b"010C\r")
            time.sleep(0.4)
            resp = recv_all(s, 0.8)
            rpm = parse(resp, 0x0C, 2, 0.25)
            if not rpm:
                time.sleep(1)
                continue

            # Read remaining PIDs quickly
            s.sendall(b"0110\r")
            time.sleep(0.25)
            maf = parse(recv_all(s, 0.6), 0x10, 2, 0.01)

            s.sendall(b"010B\r")
            time.sleep(0.25)
            map_v = parse(recv_all(s, 0.6), 0x0B, 1)

            s.sendall(b"0105\r")
            time.sleep(0.25)
            coolant = parse(recv_all(s, 0.6), 0x05, 1, 1, -40)

            s.sendall(b"010F\r")
            time.sleep(0.25)
            intake = parse(recv_all(s, 0.6), 0x0F, 1, 1, -40)

            s.sendall(b"010D\r")
            time.sleep(0.25)
            speed = parse(recv_all(s, 0.6), 0x0D, 1)

            s.sendall(b"010E\r")
            time.sleep(0.25)
            timing = parse(recv_all(s, 0.6), 0x0E, 1, 0.5, -64)

            s.sendall(b"010A\r")
            time.sleep(0.25)
            fuel_p = parse(recv_all(s, 0.6), 0x0A, 1, 3)

            boost = (map_v - 100)/100.0 if map_v else None
            now = datetime.datetime.now()
            ts = now.strftime("%H:%M:%S")

            rpm_s = f"{rpm:>5.0f}" if rpm else "  N/A"
            maf_s = f"{maf:>4.1f}" if maf else " N/A"
            map_s = f"{map_v:>3.0f}" if map_v else "N/A"
            boost_s = f"{boost:>+5.2f}" if boost is not None else " N/A"
            cool_s = f"{coolant:>2.0f}" if coolant is not None else "N/A"
            speed_s = f"{speed:>2.0f}" if speed is not None else "N/A"
            timing_s = f"{timing:>+3.1f}" if timing is not None else "N/A"

            line = f"{ts:>8} | {rpm_s} | {maf_s} | {map_s} | {boost_s} | {cool_s}°C | {speed_s} | {timing_s}°"
            sys.stdout.write("\r" + line + " " * 20)
            sys.stdout.flush()

            # Log
            with open(LOG_FILE, "a") as f:
                f.write(f"{now.isoformat()},{rpm:.0f},{maf or ''},{map_v or ''},{boost or ''},{coolant or ''},{intake or ''},{speed or ''},{timing or ''},{fuel_p or ''}\n")

            time.sleep(0.5)

    except (BrokenPipeError, ConnectionError, OSError) as e:
        print(f"\n[!] Rozłączono: {e}")
    except KeyboardInterrupt:
        print("\n[+] Zatrzymano")
    finally:
        try: s.close()
        except: pass

    print(f"\nDane zapisane w: {LOG_FILE}")
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            lines = f.readlines()
        print(f"Zebrano {len(lines)-1} odczytów")

if __name__ == "__main__":
    main()
