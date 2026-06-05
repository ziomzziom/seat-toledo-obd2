#!/bin/bash
# OBD2 Logger wrapper - uruchamia bluetoothctl w tle + skrypt Pythona
echo "=== OBD2 Logger - Seat Toledo 2 ==="
echo "Uruchamiam połączenie Bluetooth..."

# Uruchom bluetoothctl connect w tle
bluetoothctl connect A2:2A:19:04:00:00 &
BT_PID=$!

# Poczekaj na połączenie
sleep 4

# Uruchom skrypt Pythona
python3 /tmp/obd_logger_v3.py

# Po zakończeniu zabij bluetoothctl
kill $BT_PID 2>/dev/null
wait $BT_PID 2>/dev/null
