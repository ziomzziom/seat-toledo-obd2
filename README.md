# Seat Toledo 2 OBD2 Diagnostyka

Diagnostyka OBD2 dla Seata Toledo 2 z silnikiem **1.9 TDI ASV (110 KM)** przez interfejs **ELM327 Bluetooth**.

## Opis problemu

Samochód traci moc i nie rozpędza się powyżej 120 km/h – niezależnie od wciśnięcia pedału gazu.

## Przeprowadzone testy

### 1. MAF (przepływomierz) – ✅ SPRAWNY

| Stan silnika | RPM | MAF (g/s) | Norma | Werdykt |
|---|---|---|---|---|
| Zimny (56°C) | ~900 | **13.8 g/s** | 4-10 | ⚠️ Podwyższony – zimny silnik + EGR |
| Ciepły (83-91°C) | ~900 | **8.3-8.7 g/s** | 4-10 | ✅ Normalny |
| Pod obciążeniem (~2300 RPM) | 2238 | **71.1 g/s** | 45-55 | ✅ Wysoki, ale zdrowy |

**Wniosek:** MAF działa poprawnie. Wartość 13 g/s na zimnym silniku jest normalna – wyższe dawkowanie paliwa = więcej powietrza.

### 2. Turbina / Boost – ⚠️ NADMIERNE DOŁADOWANIE

| Moment | RPM | MAP (kPa) | Boost (bar) |
|---|---|---|---|
| Jałowy | ~900 | 100 | +0.01 |
| Lekkie przyspieszenie | 1634 | 180 | **+0.80** |
| Mocne przyspieszenie | 2306 | 217 | **+1.17** |
| **MAX** | **2238** | **248** | **+1.48 🔴** |

**Norma fabryczna dla ASV: 220-230 kPa / +1.2-1.3 bar**

**+1.48 bar to overboost!** Turbina dostarcza za dużo ciśnienia. Prawdopodobnie N75 nie odcina boosta prawidłowo.

### 3. Kody błędów (DTC) – ✅ BRAK

| Metoda | Wynik | Znaczenie |
|--------|-------|-----------|
| `03` (stored) | NO DATA | Brak zapisanych kodów |
| `0101` (status) | MIL off, 0 DTC | Brak usterek w ECU |
| `07` (pending) | NO DATA | Brak oczekujących kodów |
| `0A` (permanent) | NO DATA | Brak permanentnych kodów |

**Wniosek:** ECU nie widzi błędów. Overboost nie jest rejestrowany jako usterka (krótkotrwały).
Uwaga: potwierdzone kody DTC nie znikają same – trzeba je kasować narzędziem diagnostycznym.

### 4. Dodatkowe obserwacje

| Parametr | Wartość | Ocena |
|----------|---------|-------|
| Temp płynu | 83-91°C | ✅ Normalna |
| Temp dolotu | 42-50°C | ✅ Normalna |
| Kąt wyprzedzenia | -2° do +8° | ✅ Normalny dla TDI |
| Napięcie | 14.1V | ✅ Alternator ładuje |
| **EGR** | **cieknie** | 🔴 Nieszczelność wizualna |

## Wnioski końcowe

### Co jest sprawne:
- MAF (przepływomierz) – ✅
- Temperatura silnika – ✅
- Temperatura dolotu – ✅
- Kąty wyprzedzenia – ✅
- Brak kodów błędów – ✅

### Co podejrzane:
1. **Overboost (+1.48 bar)** – turbina daje za dużo ciśnienia (norma ~1.2-1.3 bar)
2. **Cieknący EGR** – nieszczelność w układzie dolotowym
3. **N75 lub wężyki podciśnienia** – prawdopodobna przyczyna overboost

### Teoria: dlaczego auto nie jedzie >120 km/h

```
Przyspieszasz → boost rośnie → +1.48 bar (overboost) →
ECU wyczuwa nadmiar → wchodzi LIMP MODE (odcina paliwo) →
moc spada → nie możesz jechać szybciej

LUB:
Cieknący EGR → nieszczelny dolot → zaburzone dawkowanie →
spadek mocy przy wysokich obrotach
```

### Rekomendowane czynności (kolejność):

1. **Sprawdź wężyki podciśnienia** – szczególnie przy N75 i siłowniku turbiny (często pękają)
2. **Sprawdź N75 multimetrem** – oporność powinna być 15-20 Ω
3. **Sprawdź siłownik VNT** – czy drążek rusza się ręcznie (przy wyłączonym silniku)
4. **Wymień uszczelkę EGR** – skoro cieknie
5. **Kolejna jazda testowa** – pełny gaz 3. bieg 60→120 km/h z logerem

## Struktura repozytorium

```
seat-toledo-obd2/
├── README.md                  ← niniejszy plik
├── .gitignore
├── archive/                   ← stare wersje skryptów
├── data/
│   └── obd_dane.txt           ← zebrane dane z jazdy próbnej
└── scripts/
    ├── obd_logger.py          ← główny logger OBD2 (zalecany)
    ├── read_dtc.py            ← odczyt kodów błędów DTC
    ├── bt_pair.py             ← parowanie ELM327 przez D-Bus
    └── run_obd.sh             ← wrapper startowy
```

## Instrukcja użycia

### Wymagania
- Python 3
- BlueZ (bluetoothctl)
- ELM327 v2.1 lub compatible (sparowany PIN 1234)
- Konto GitHub (do publikacji)

### Parowanie ELM327
```bash
bluetoothctl trust A2:2A:19:04:00:00
bluetoothctl pair A2:2A:19:04:00:00  # PIN: 1234
```

### Odczyt kodów błędów
```bash
python3 scripts/read_dtc.py
```

### Logger danych (jazda testowa)
```bash
./scripts/run_obd.sh
```
lub ręcznie:
```bash
bluetoothctl connect A2:2A:19:04:00:00 &
sleep 4
python3 scripts/obd_logger.py
```

### Zbieranie danych podczas jazdy
1. Odpal silnik, podłącz ELM327
2. Uruchom `./scripts/run_obd.sh`
3. Poczekaj na komunikat "RPM OK" (~5-10s)
4. Jedź – dane zapisują się do `data/obd_dane.txt`
5. Ctrl+C by zatrzymać

### Publikacja na GitHub
```bash
gh auth login        # jednorazowo – logowanie przez przeglądarkę
gh repo create seat-toledo-obd2 --public --source=. --remote=origin --push
```

## Uwagi techniczne

### ELM327
Adapter użyty w diagnostyce to chiński klon oparty na chipie **TDA81** (identyfikujący się jako ELM327 v2.1).
Działa z protokołem ISO 9141-2 (K-line) dla VAG, ale ma ograniczenia:
- ❌ Nie czyta DTC z niektórych ECU VAG przez KWP
- ⚠️ Niestabilne połączenie – wymaga czasem power-cyklu
- ✅ Działa dla live data (RPM, MAF, MAP itp.)

### Protokół
Dla 1.9 TDI ASV: **ISO 9141-2** (wykrywany automatycznie jako protokół A3).
Ustawienie ręczne: `ATSP3` lub `ATSP4` (KWP 5BAUD).

### Plik danych
Format CSV: `czas,rpm,maf,map,boost,coolant,intake,speed,timing`

## Autor

Diagnostyka przeprowadzona przez OpenCode AI.
Dane zebrane na żywo z pojazdu przez interfejs ELM327 Bluetooth.
