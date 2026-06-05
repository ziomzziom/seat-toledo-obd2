#!/usr/bin/env python3
"""
OBD2 Logger v4 - niezawodne łączenie + kompletne dane
Uruchamia bluetoothctl connect w tle i łapie połączenie
"""
import socket
import time
import sys
import datetime
import os
import subprocess

OBD_MAC = "A2:2A:19:04:00:00"
LOG_FILE = "/tmp/obd_dane.txt"

def recv_all(s, t=1.0):
    s.settimeout(t)
    d = b""
    try:
        while True:
            c = s.recv(4096)
            if not c: break
            d += c
            if b">" in c: break
    except socket.timeout: pass
    except: return ""
    return d.decode(errors="replace").strip()

def parse(resp, pid, nb=1, sc=1, off=0):
    if not resp: return None
    resp = resp.replace(" ","").replace("\r","").replace("\n","").replace(">","")
    idx = resp.find(f"41{pid:02X}")
    if idx < 0: idx = resp.find(f"4{pid:02X}")
    if idx >= 0:
        d = resp[idx+4:]
        if len(d) >= nb*2:
            try: return int(d[:nb*2], 16) * sc + off
            except: pass
    for p in resp.split():
        p = p.strip()
        if len(p) >= 2 and all(c in "0123456789ABCDEFabcdef" for c in p):
            if len(p) >= nb*2:
                try: return int(p[:nb*2], 16) * sc + off
                except: pass
    return None

bt_process = None

def find_obd():
    """Próbuj połączyć się z ELM327"""
    global bt_process
    for _ in range(20):
        # Start bluetoothctl in background
        bt_process = subprocess.Popen(["bluetoothctl", "connect", OBD_MAC],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3)

        s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        s.settimeout(3)
        try:
            s.connect((OBD_MAC, 1))
            s.setblocking(False)
            # Quick init + warmup immediately
            s.sendall(b"ATZ\r")
            time.sleep(1)
            s.sendall(b"ATE0\r")
            time.sleep(0.2)
            s.sendall(b"ATS0\r")
            time.sleep(0.2)
            s.sendall(b"ATH0\r")
            time.sleep(0.2)
            s.sendall(b"ATSP0\r")
            time.sleep(0.3)
            for w in range(10):
                s.sendall(b"010C\r")
                time.sleep(0.6)
                try:
                    s.settimeout(0.8)
                    d = b""
                    while True:
                        c = s.recv(4096)
                        if not c: break
                        d += c
                        if b">" in c: break
                except: pass
                if parse(d.decode(errors="replace").strip(), 0x0C, 2, 0.25):
                    return s
            s.close()
        except:
            try: s.close()
            except: pass

        bt_process.kill()
        bt_process.wait()
        time.sleep(1)
        bt_process = None
    return None

print("=" * 70)
print("OBD2 Logger v4 - Seat Toledo 2, 1.9 TDI ASV")
print("=" * 70)

# Init log
if not os.path.exists(LOG_FILE) or os.path.getsize(LOG_FILE) == 0:
    with open(LOG_FILE, "w") as f:
        f.write("time,rpm,maf,map,boost,coolant,intake,speed,timing,fuel_p\n")

print("[*] Szukam ELM327 przez Bluetooth...")
s = find_obd()
if not s:
    print("[-] Nie znaleziono ELM327. Sprawdź czy:")
    print("  1. ELM327 jest wpięty do OBD2")
    print("  2. Silnik jest włączony")
    print(f"  3. Sparuj: bluetoothctl pair {OBD_MAC} (PIN: 1234)")
    sys.exit(1)

print("[+] Połączono! ELM327 gotowy.")

# Flush any remaining data in buffer
time.sleep(0.5)
try:
    s.settimeout(0.3)
    while True:
        c = s.recv(4096)
        if not c: break
except:
    pass
s.setblocking(False)

print()
print(f"{'Czas':>8} {'RPM':>5} {'MAF':>5} {'MAP':>3} {'Boost':>5} {'°C':>3} {'km/h':>3} {'Zap':>4}")
print("-" * 55)

try:
    while True:
        # Read RPM (with retry)
        rpm = None
        for _ in range(3):
            s.sendall(b"010C\r")
            time.sleep(0.3)
            resp = recv_all(s, 0.7)
            rpm = parse(resp, 0x0C, 2, 0.25)
            if rpm: break
        if not rpm:
            continue

        # Rest of PIDs
        s.sendall(b"0110\r")
        time.sleep(0.2)
        maf = parse(recv_all(s, 0.5), 0x10, 2, 0.01)

        s.sendall(b"010B\r")
        time.sleep(0.2)
        map_v = parse(recv_all(s, 0.5), 0x0B, 1)

        s.sendall(b"0105\r")
        time.sleep(0.2)
        cool = parse(recv_all(s, 0.5), 0x05, 1, 1, -40)

        s.sendall(b"010F\r")
        time.sleep(0.2)
        intake = parse(recv_all(s, 0.5), 0x0F, 1, 1, -40)

        s.sendall(b"010D\r")
        time.sleep(0.2)
        speed = parse(recv_all(s, 0.5), 0x0D, 1)

        s.sendall(b"010E\r")
        time.sleep(0.2)
        timing = parse(recv_all(s, 0.5), 0x0E, 1, 0.5, -64)

        s.sendall(b"010A\r")
        time.sleep(0.2)
        fuel_p = parse(recv_all(s, 0.5), 0x0A, 1, 3)

        boost = (map_v-100)/100.0 if map_v else None
        now = datetime.datetime.now()
        ts = now.strftime("%H:%M:%S")

        r = f"{rpm:>5.0f}" if rpm else "N/A"
        m = f"{maf:>4.1f}" if maf else "N/A"
        mp = f"{map_v:>3.0f}" if map_v else "N/A"
        b = f"{boost:>+5.2f}" if boost else "N/A"
        c = f"{cool:>2.0f}" if cool else "N/A"
        sp = f"{speed:>2.0f}" if speed else "N/A"
        ti = f"{timing:>+3.1f}" if timing else "N/A"

        sys.stdout.write(f"\r{ts:>8} {r} {m}g/s {mp}kPa {b}bar {c}°C {sp}km/h {ti}°")
        sys.stdout.flush()

        with open(LOG_FILE, "a") as f:
            f.write(f"{now.isoformat()},{rpm:.0f},{maf or ''},{map_v or ''},{boost or ''},{cool or ''},{intake or ''},{speed or ''},{timing or ''},{fuel_p or ''}\n")

        time.sleep(0.4)

except KeyboardInterrupt:
    print("\n[+] Zatrzymano")
except (BrokenPipeError, ConnectionError, OSError) as e:
    print(f"\n[!] Błąd: {e}")
finally:
    try: s.close()
    except: pass
    if bt_process:
        try: bt_process.kill()
        except: pass

print(f"\nDane: {LOG_FILE}")
if os.path.exists(LOG_FILE):
    with open(LOG_FILE) as f:
        lines = f.readlines()
    print(f"Zebrano {len(lines)-1} odczytów")
