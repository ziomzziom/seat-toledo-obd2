#!/bin/bash
# KKL: diagnostyka Seata (KW1281, 9600 baud, adres ECU=1)
# Użycie:
#   bash scripts/kkl_seat.sh read     - odczyt kodów błędów
#   bash scripts/kkl_seat.sh clear    - kasowanie kodów błędów
#   bash scripts/kkl_seat.sh readclear- odczyt + kasowanie
set -e
export PATH="$HOME/.dotnet:$PATH"
export DOTNET_ROOT="$HOME/.dotnet"

CMD="${1:-read}"

echo "=== 1. Ustawiam latency timer FTDI na 1ms ==="
python3 scripts/kkl_latency.py

cd /tmp/kw1281test

case "$CMD" in
  read)
    echo ""
    echo "=== ODCZYT kodów błędów ==="
    timeout 45 dotnet bin/Debug/net10.0/linux-x64/kw1281test.dll /dev/ttyUSB0 9600 1 ReadFaultCodes
    ;;
  clear)
    echo ""
    echo "=== KASOWANIE kodów błędów ==="
    timeout 45 dotnet bin/Debug/net10.0/linux-x64/kw1281test.dll /dev/ttyUSB0 9600 1 ClearFaultCodes
    ;;
  readclear)
    echo ""
    echo "=== ODCZYT kodów błędów (przed) ==="
    timeout 45 dotnet bin/Debug/net10.0/linux-x64/kw1281test.dll /dev/ttyUSB0 9600 1 ReadFaultCodes
    echo ""
    echo "=== KASOWANIE kodów błędów ==="
    timeout 45 dotnet bin/Debug/net10.0/linux-x64/kw1281test.dll /dev/ttyUSB0 9600 1 ClearFaultCodes
    echo ""
    echo "=== ODCZYT kodów błędów (po) ==="
    timeout 45 dotnet bin/Debug/net10.0/linux-x64/kw1281test.dll /dev/ttyUSB0 9600 1 ReadFaultCodes
    ;;
  *)
    echo "Użycie: bash scripts/kkl_seat.sh [read|clear|readclear]"
    exit 1
    ;;
esac

echo ""
echo "=== Gotowe ==="
