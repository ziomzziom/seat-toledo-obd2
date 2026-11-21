#!/bin/bash
# VCDS-Lite pod Wine - kabel KKL (COM1 -> /dev/ttyUSB0)
export WINEPREFIX=/home/saffron/.wine-vcds
export WINEARCH=win32

# Upewnij się, że port jest zmapowany
ln -sf /dev/ttyUSB0 "$WINEPREFIX/dosdevices/com1" 2>/dev/null

# Uruchom VCDS-Lite
cd "$WINEPREFIX/drive_c/Ross-Tech/VCDS-Lite"
wine VCDSLite.exe
