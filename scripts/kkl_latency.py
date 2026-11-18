#!/usr/bin/env python3
"""
Set FTDI latency timer to 1ms (kabel KKL) - wymagane dla KW1281
"""
from pyftdi.ftdi import Ftdi
import sys

URL = 'ftdi://ftdi:232:AM6KP9MU/1'

def main():
    f = Ftdi()
    f.open_from_url(URL)
    before = f.get_latency_timer()
    f.set_latency_timer(1)
    after = f.get_latency_timer()
    print(f"latency: {before} -> {after} ms")
    f.close()

if __name__ == "__main__":
    main()
