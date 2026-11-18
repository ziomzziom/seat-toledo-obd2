#!/bin/bash
# KKL: odczyt błędów z Seata (KW1281, 9600 baud, adres ECU=1)
set -e
export PATH="$HOME/.dotnet:$PATH"
export DOTNET_ROOT="$HOME/.dotnet"

echo "=== 1. Ustawiam latency timer FTDI na 1ms ==="
python3 /tmp/kkl_latency.py

echo ""
echo "=== 2. Odczyt kodów błędów (kw1281test, 9600 baud) ==="
cd /tmp/kw1281test
timeout 45 dotnet bin/Debug/net10.0/linux-x64/kw1281test.dll /dev/ttyUSB0 9600 1 ReadFaultCodes

echo ""
echo "=== Gotowe ==="
