#!/usr/bin/env python3
"""
DTC catcher - łapie kod błędu W TRAKCIE limp mode
Seat Toledo 2, 1.9 TDI ASV
"""
import socket
import time
import sys
import datetime
import subprocess

OBD_MAC = "A2:2A:19:04:00:00"
LOG_FILE = "/tmp/dtc_catch_log.txt"

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
    return None

def trigger_bt():
    subprocess.Popen(["bluetoothctl","connect",OBD_MAC],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3)

def connect_and_init():
    trigger_bt()
    s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    s.settimeout(5)
    try:
        s.connect((OBD_MAC, 1))
        s.setblocking(False)
        s.sendall(b"ATZ\r"); time.sleep(1.2); recv_all(s,1.0)
        s.sendall(b"ATE0\r"); time.sleep(0.15); recv_all(s,0.4)
        s.sendall(b"ATS0\r"); time.sleep(0.15); recv_all(s,0.4)
        s.sendall(b"ATH0\r"); time.sleep(0.15); recv_all(s,0.4)
        s.sendall(b"ATSP0\r"); time.sleep(0.25); recv_all(s,0.5)
        for i in range(8):
            s.sendall(b"010C\r"); time.sleep(0.5)
            if parse(recv_all(s,0.6), 0x0C, 2, 0.25):
                return s
        s.close()
    except:
        try: s.close()
        except: pass
    return None

def read_dtc(s):
    """Czyta DTC i zwraca dict"""
    out = {}
    for cmd, name in [("03","stored"),("07","pending"),("0A","permanent"),("0101","status")]:
        s.sendall((cmd+"\r").encode()); time.sleep(0.8)
        r = recv_all(s,1.0).replace(">","").replace("\r","").replace("\n","").strip()
        out[name] = r if r else ""
    return out

def main():
    print("=== DTC catcher (łapie kod w trakcie limp mode) ===")
    with open(LOG_FILE, "a") as f:
        f.write("time,rpm,map,boost,speed,event,dtc_stored,dtc_pending,dtc_permanent,dtc_status\n")

    s = None
    for attempt in range(20):
        s = connect_and_init()
        if s:
            print(f"[+] Połączono (próba {attempt+1})")
            break
        sys.stdout.write(f"\r[*] Próba {attempt+1}/20...")
        sys.stdout.flush()
    if not s:
        print("\n[-] Brak połączenia")
        return

    print("\n=== BASELINE DTC (przed) ===")
    base = read_dtc(s)
    for k,v in base.items():
        print(f"  {k}: '{v[:60]}'" if v else f"  {k}: (pusto)")

    print("\n[*] Łapanie... (dodaj gazu do limp mode, NIE gaś silnika)")
    print(f"{'Czas':>8} {'RPM':>5} {'Boost':>7}  EVENT")
    print("-"*50)

    overboost_seen = False
    prev_boost = None
    fail_count = 0
    limp_caught = False

    try:
        while True:
            try:
                s.sendall(b"010C\r"); time.sleep(0.25)
                rpm = parse(recv_all(s,0.5), 0x0C, 2, 0.25)
                s.sendall(b"010B\r"); time.sleep(0.25)
                map_v = parse(recv_all(s,0.5), 0x0B, 1)
                s.sendall(b"010D\r"); time.sleep(0.25)
                speed = parse(recv_all(s,0.5), 0x0D, 1)

                if rpm is None or map_v is None:
                    fail_count += 1
                    if fail_count > 10:
                        raise OSError("brak danych")
                    continue
                fail_count = 0

                boost = (map_v - 100)/100.0
                now = datetime.datetime.now().strftime("%H:%M:%S")

                event = ""
                if boost >= 1.3:
                    event = "OVERBOOST"
                    overboost_seen = True
                elif overboost_seen and boost < 0.5 and prev_boost and prev_boost >= 1.0:
                    event = "LIMP MODE!"
                    overboost_seen = False
                    limp_caught = True
                prev_boost = boost

                # Gdy limp mode złapany - natychmiast czytaj DTC
                dtc = {"stored":"","pending":"","permanent":"","status":""}
                if limp_caught:
                    print(f"\n>>> LIMP MODE wykryty! Odczyt DTC...")
                    dtc = read_dtc(s)
                    for k,v in dtc.items():
                        print(f"    {k}: '{v[:80]}'" if v else f"    {k}: (pusto)")
                    limp_caught = False

                line = f"{now:>8} {rpm:>5.0f} {boost:>+6.2f}  {event}"
                print("\r" + line + "    ", end="")
                sys.stdout.flush()

                with open(LOG_FILE, "a") as f:
                    f.write(f"{now},{rpm:.0f},{map_v:.0f},{boost:.2f},{speed or 0},{event},{dtc['stored']},{dtc['pending']},{dtc['permanent']},{dtc['status']}\n")

                time.sleep(0.15)

            except (OSError, BrokenPipeError):
                print("\n[!] Połączenie padło - reconnect...")
                try: s.close()
                except: pass
                s = None
                while s is None:
                    s = connect_and_init()
                    if s:
                        print("[+] Połączono ponownie")
                    else:
                        sys.stdout.write("\r[*] reconnect...")
                        sys.stdout.flush()

    except KeyboardInterrupt:
        print("\n\n[+] Zatrzymano")
    try: s.close()
    except: pass
    print(f"\nLog: {LOG_FILE}")

if __name__ == "__main__":
    main()
