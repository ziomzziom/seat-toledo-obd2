#!/usr/bin/env python3
"""
OBD2 Logger - persistent connection
"""
import socket
import time
import sys
import datetime
import os

OBD_MAC = "A2:2A:19:04:00:00"
LOG_FILE = "/tmp/obd_dane.txt"

def recv_all(sock, timeout=1.5):
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
        pass
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
    return None

print("=== OBD2 Logger ===")
print(f"Log: {LOG_FILE}")
print()

if not os.path.exists(LOG_FILE) or os.path.getsize(LOG_FILE) == 0:
    with open(LOG_FILE, "w") as f:
        f.write("time,rpm,maf,map,boost,coolant,intake,speed\n")

# Connect once
s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
s.settimeout(10)
print("[*] Łączenie...")
s.connect((OBD_MAC, 1))
s.setblocking(False)
print("[+] Połączono")

# Init
for cmd_str, wait in [("ATZ", 2), ("ATE0", 0.3), ("ATS0", 0.2), ("ATH0", 0.2)]:
    time.sleep(wait)
    s.sendall((cmd_str + "\r").encode())
time.sleep(0.5)
recv_all(s, 2)

print("[+] ELM327 gotowy")
print("=" * 70)

# Warmup
print("[*] Szukanie protokołu...", end=" ", flush=True)
for i in range(20):
    s.sendall(b"010C\r")
    time.sleep(1.0)
    resp = recv_all(s, 1.5)
    rpm = parse(resp, 0x0C, 2, 0.25)
    if rpm:
        print(f"OK! RPM={rpm:.0f} (próba {i+1})")
        break
else:
    print("FAIL - brak odpowiedzi ECU")
    sys.exit(1)

print()
print(f"{'Czas':>8} {'RPM':>6} {'MAF':>8} {'MAP':>4} {'Boost':>7} {'°C':>4} {'km/h':>4}")
print("-"*50)

try:
    while True:
        # Read RPM
        s.sendall(b"010C\r")
        time.sleep(0.5)
        resp = recv_all(s, 1.0)
        rpm = parse(resp, 0x0C, 2, 0.25)
        if not rpm:
            s.sendall(b"010C\r")
            time.sleep(0.8)
            resp = recv_all(s, 1.2)
            rpm = parse(resp, 0x0C, 2, 0.25)
            if not rpm:
                print("\n[!] Utracono połączenie z ECU")
                break

        # Sequential reads
        s.sendall(b"0110\r")
        time.sleep(0.3)
        maf = parse(recv_all(s, 0.8), 0x10, 2, 0.01)

        s.sendall(b"010B\r")
        time.sleep(0.3)
        map_v = parse(recv_all(s, 0.8), 0x0B, 1)

        s.sendall(b"0105\r")
        time.sleep(0.3)
        coolant = parse(recv_all(s, 0.8), 0x05, 1, 1, -40)

        s.sendall(b"010F\r")
        time.sleep(0.3)
        intake = parse(recv_all(s, 0.8), 0x0F, 1, 1, -40)

        s.sendall(b"010D\r")
        time.sleep(0.3)
        speed = parse(recv_all(s, 0.8), 0x0D, 1)

        boost = (map_v - 100)/100.0 if map_v else None

        now = datetime.datetime.now()
        ts = now.strftime("%H:%M:%S")

        rpm_s = f"{rpm:>6.0f}" if rpm else "   N/A"
        maf_s = f"{maf:>7.1f}" if maf else "    N/A"
        map_s = f"{map_v:>3.0f}" if map_v else "N/A"
        boost_s = f"{boost:>+6.2f}" if boost is not None else "  N/A"
        cool_s = f"{coolant:>2.0f}" if coolant is not None else " N/A"
        speed_s = f"{speed:>2.0f}" if speed is not None else "N/A"

        sys.stdout.write(f"\r{ts:>8} {rpm_s} {maf_s}g/s {map_s}kPa {boost_s}bar {cool_s}°C {speed_s}km/h  ")
        sys.stdout.flush()

        with open(LOG_FILE, "a") as f:
            f.write(f"{now.isoformat()},{rpm or ''},{maf or ''},{map_v or ''},{boost or ''},{coolant or ''},{intake or ''},{speed or ''}\n")

        time.sleep(0.3)

except KeyboardInterrupt:
    print("\n[+] Zatrzymano")

s.close()
print(f"\nDane: {LOG_FILE}")
