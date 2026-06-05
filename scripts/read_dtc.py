#!/usr/bin/env python3
"""
OBD2 DTC Reader - Seat Toledo 2, 1.9 TDI ASV
Odczytuje kody błędów z ECU przez ELM327 Bluetooth
"""
import socket
import time
import subprocess
import sys

OBD_MAC = "A2:2A:19:04:00:00"

def recv_all(s, t=1.0):
    s.settimeout(t)
    d = b""
    try:
        while True:
            c = s.recv(4096)
            if not c: break
            d += c
            if b">" in c: break
    except: pass
    return d.decode(errors="replace").strip()

def parse_val(resp, pid, nb=1, sc=1, off=0):
    if not resp: return None
    resp = resp.replace(" ","").replace("\r","").replace("\n","").replace(">","")
    idx = resp.find(f"41{pid:02X}")
    if idx < 0: idx = resp.find(f"4{pid:02X}")
    if idx >= 0:
        d = resp[idx+4:]
        if len(d) >= nb*2:
            try: return int(d[:nb*2], 16) * sc + off
            except: pass
    return None

def connect():
    p = subprocess.Popen(["bluetoothctl", "connect", OBD_MAC],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(4)
    s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    s.settimeout(5)
    try:
        s.connect((OBD_MAC, 1))
        s.setblocking(False)
        return s, p
    except:
        try: s.close()
        except: pass
        p.kill()
        return None, None

def main():
    print("=" * 60)
    print("OBD2 DTC Reader - Seat Toledo 2, 1.9 TDI ASV")
    print("=" * 60)
    print()

    s, bt_proc = connect()
    if not s:
        print("[-] Nie można połączyć z ELM327")
        print("  Sprawdź: ELM327 w OBD2, zapłon ON, sparuj: bluetoothctl pair A2:2A:19:04:00:00 1234")
        sys.exit(1)

    # Init
    for c, w in [("ATZ", 1.5), ("ATE0", 0.2), ("ATS0", 0.2), ("ATH0", 0.2)]:
        s.sendall((c + "\r").encode())
        time.sleep(w)
    recv_all(s, 0.5)

    # Warmup
    print("[*] Szukanie protokołu...", end=" ", flush=True)
    for i in range(10):
        s.sendall(b"010C\r")
        time.sleep(0.4)
        r = recv_all(s, 0.6)
        if parse_val(r, 0x0C, 2, 0.25):
            print(f"RPM OK ({i+1})")
            break
    else:
        print("FAIL - ECU nie odpowiada")
        s.close()
        if bt_proc: bt_proc.kill()
        sys.exit(1)

    print("\n=== KODY BŁĘDÓW ===")

    tests = [
        ("03  - Stored DTC", "03"),
        ("0101 - Status (MIL/DTC count)", "0101"),
        ("07  - Pending DTC", "07"),
        ("0A  - Permanent DTC", "0A"),
        ("02  - Freeze frame", "02"),
    ]

    for name, cmd in tests:
        s.sendall((cmd + "\r").encode())
        time.sleep(0.8)
        resp = recv_all(s, 1.0).replace(">", "").strip()
        if resp:
            print(f"  {name:<25} {resp[:100]}")
        else:
            print(f"  {name:<25} [brak odpowiedzi]")

    # Parse 0101 for DTC count
    print("\n=== PODSUMOWANIE ===")
    s.sendall(b"0101\r")
    time.sleep(0.5)
    r = recv_all(s, 0.8).replace(">", "").strip()
    dtc_count = parse_val(r, 1, 1)
    if dtc_count is not None and dtc_count > 0:
        print(f"  Zapisane DTC: {dtc_count}")
    else:
        print("  Zapisane DTC: 0 (brak kodów błędów)")

    s.close()
    if bt_proc: bt_proc.kill()

if __name__ == "__main__":
    main()
