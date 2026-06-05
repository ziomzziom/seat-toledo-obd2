# Seat Toledo 2 OBD2 Diagnostyka

## Opis
Narzędzia do diagnostyki OBD2 przez Bluetooth dla Seata Toledo 2 z silnikiem 1.9 TDI ASV (110 KM).
Zbiera i analizuje dane z ECU przez interfejs ELM327.

## Problem
Samochód traci moc i nie rozpędza się powyżej 120 km/h.

## Zebrane dane

### Jałowy (~900 RPM)
- MAF: 8.3-8.7 g/s (norma 4-10)
- MAP: 100-101 kPa (atmosferyczne)
- Boost: +0.01 bar
- Temp płynu: 83-91°C

### Pod obciążeniem
- MAF max: 71.1 g/s przy 2238 RPM
- MAP max: 248 kPa przy 2238 RPM
- Boost max: **+1.48 bar** 🔴 (norma ASV: 1.2-1.3 bar)

## Wnioski
- **MAF sprawny** – wartości w normie
- **Turbina doładowuje za mocno** – overboost do +1.48 bar
- **Prawdopodobna przyczyna**: uszkodzony N75 / nieszczelne podciśnienie / cieknący EGR
- ECuwchodzi w limp mode przy overboost → utrata mocy >120 km/h

## Użycie

### Zależności
- Python 3
- BlueZ (bluetoothctl)
- `bluetoothctl pair <MAC> 1234` – sparuj ELM327

### Uruchomienie
```bash
./scripts/run_obd.sh
```
lub ręcznie:
```bash
bluetoothctl connect A2:2A:19:04:00:00 &
sleep 4
python3 scripts/obd_logger.py
```

## Pliki

| Plik | Opis |
|------|------|
| `scripts/obd_logger.py` | Główny logger OBD2 (v4 – najbardziej stabilny) |
| `scripts/obd_logger_simple.py` | Prosty logger (jednokrotne połączenie) |
| `scripts/run_obd.sh` | Wrapper bash uruchamiający Bluetooth + logger |
| `scripts/bt_pair.py` | Parowanie ELM327 przez D-Bus |
| `data/obd_dane.txt` | Zebrane dane z jazdy próbnej |
