# Seat Toledo 2 (1.9 TDI ASV) – Raport diagnostyczny

## 1. Opis problemu
Samochód traci moc i nie rozpędza się powyżej **120 km/h** – niezależnie od wciśnięcia pedału gazu. Dodatkowo występuje:
- **Świst** przy ok. **1800 obr/min**
- **Kliknięcie** przy ok. **1500 obr/min** (słyszalne po zdjęciu obudowy silnika)

---

## 2. Przeprowadzone testy i wyniki

### 2.1. MAF (przepływomierz) – ✅ SPRAWNY
| Stan | RPM | MAF (g/s) | Norma | Werdykt |
|------|-----|-----------|-------|---------|
| Jałowy (zimny) | ~900 | 13,8 | 4–10 | ⚠️ Podwyższony (zimny silnik + EGR) |
| Jałowy (ciepły) | ~900 | 8,3–8,7 | 4–10 | ✅ Prawidłowy |
| Pełne obciążenie | 2238 | 71,1 | 45–55 | ✅ Wysoki, ale zdrowy |

**Wniosek:** MAF działa poprawnie – **nie wymieniać**.

---

### 2.2. MAP / doładowanie – 🔴 OVERBOOST
| RPM | MAP (kPa) | Boost (bar) | Norma | Werdykt |
|-----|-----------|-------------|-------|---------|
| 1634 | 180 | **+0,80** | +0,5–0,6 | ⚠️ Zbyt wysoki jak na te obroty |
| 1846 | 178 | **+0,78** | +0,5–0,6 | ⚠️ **Źródło świstu** |
| 2238 | **248** | **+1,48** | +1,2–1,3 | 🔴 **OVERBOOST – odcięcie mocy** |

**Wniosek:** Overboost jest realny i powoduje odcięcie paliwa przez ECU → brak mocy powyżej 120 km/h.

---

### 2.3. EGR – 🔴 NIESZCZELNOŚĆ WIZUALNA
- Uszczelka EGR **ewidentnie do wymiany** – stwierdzona nieszczelność przez mechanika.

---

### 2.4. Dodatkowe objawy
| Objaw | Przyczyna (prawdopodobna) |
|-------|----------------------------|
| Kliknięcie przy 1500 obr/min | Uszkodzony N75 (zawór sterujący turbiną) – charakterystyczne klikanie przy modulacji PWM |
| Świst przy 1800 obr/min | Nadmiar ciśnienia + nieszczelność (EGR lub węże) |

---

### 2.5. Kody błędów – ✅ BRAK
- Brak kodów DTC (stored, pending, permanent) – overboost nie jest rejestrowany jako trwały błąd, tylko chwilowe odcięcie paliwa.

---

## 3. Przyczyny (ranking prawdopodobieństwa)

| Priorytet | Przyczyna | Opis |
|-----------|-----------|------|
| **1** | **N75** (zawór sterujący turbiną) | Uszkodzony lub zabrudzony – nie odcina podciśnienia, geometria turbiny w pozycji max doładowania → overboost. Kliknięcie przy 1500 RPM to typowy objaw. |
| **2** | **Wężyki podciśnieniowe** (N75 → siłownik VNT) | Pęknięte, sparciałe lub zatkane olejem – nie przenoszą sygnału do siłownika. |
| **3** | **Siłownik VNT** (zapieczona geometria) | Zablokowane łopatki turbiny w pozycji "full boost" – wymaga czyszczenia lub regeneracji. |
| **4** | **Uszczelka EGR** | Nieszczelność w układzie dolotowym – pogłębia problem, ale nie jest główną przyczyną overboostu. |

---

## 4. Rekomendowane czynności (kolejność)

### ✅ Krok 1: Zamień N75 z N18 (EGR) – TEST ZA 0 ZŁ
- Oba zawory są **identyczne**.
- Jeśli overboost zniknie → **wymień N75**.
- Jeśli overboost pozostanie → problem w mechanice turbiny lub wężykach.

### ✅ Krok 2: Wymień uszczelkę EGR
- **Numer części:** 028 131 547 A lub zamiennik ELRING 815.187
- **Koszt:** ok. 20–40 zł za zestaw

### ✅ Krok 3: Sprawdź wężyki podciśnienia
- Wymień wszystkie spękane lub miękkie (śr. wewn. 3–4 mm).

### ✅ Krok 4: Sprawdź siłownik VNT
- Przy wyłączonym silniku – ręcznie pociągnij drążek. Powinien chodzić płynnie na całym skoku (10–15 mm).

---

## 5. Podsumowanie

| Element | Stan | Decyzja |
|---------|------|---------|
| MAF | ✅ Sprawny | Nie wymieniać |
| MAP | ✅ Sprawny | Nie wymieniać |
| N75 | 🔴 Podejrzany | Test zamiany z N18 |
| Wężyki podciśnienia | ❓ Nie sprawdzone | Sprawdzić i wymienić |
| Siłownik VNT | ❓ Nie sprawdzony | Sprawdzić ręcznie |
| Uszczelka EGR | 🔴 Do wymiany | Kupić zestaw (20–40 zł) |

---

## 6. Rekomendacja zakupu VAG KKL 409.1

Używany w projekcie **ELM327 Bluetooth (TDA81)** okazał się niewystarczający:
- Klon na chipie TDA81 nie obsługuje poprawnie KWP 2000 dla VAG – DTC zwraca "NO DATA"
- Niestabilne połączenie Bluetooth – częste page timeout, wymagany power cycle
- Działa tylko dla live data (RPM, MAF, MAP) ale nie do pełnej diagnostyki

**Rekomendacja:** zakup kabla **VAG KKL 409.1 z FT232RL** (ok. 80 zł) + **VCDS Lite** (darmowy):
- Stabilna komunikacja przez USB
- Pełny odczyt/kasowanie DTC wszystkich modułów
- Live data, adaptacje, podstawowe konfiguracje
- Współpraca z KWP2000 Flasher do backupu softu ECU

---

## 7. Spostrzeżenia z projektu

### Co dała AI
- Szybkie generowanie skryptów Python do komunikacji OBD2
- Promptowanie przyspieszyło diagnostykę – analiza danych w czasie rzeczywistym
- Automatyzacja zbierania danych do CSV
- Pomoc w interpretacji wyników (overboost, normy MAF)

### Ograniczenia
- AI nie widzi fizycznych usterek – klikający N75, cieknący EGR, pęknięte wężyki
- Nie zastąpi dotknięcia / obejrzenia / posłuchania silnika
- Jakość diagnostyki ograniczona sprzętem – słaby ELM327 = słabe dane = gorsze wnioski

### Co byśmy zrobili inaczej
- Zaczęli od VAG KKL + VCDS, nie tracąc czasu na klon ELM327
- Sprawdzili N75 i wężyki w pierwszej kolejności (fizycznie, nie przez OBD2)

---

## 8. Galeria zdjęć

Zdjęcia dokumentujące proces diagnostyki znajdują się w katalogu `photo/`:

| Zdjęcie | Opis |
|---------|------|
| `photo/elm327.jpg` | Interfejs ELM327 Bluetooth użyty w projekcie (klon TDA81) |
| `photo/toledo_incar.jpeg` | Wnętrze pojazdu z laptopem podczas diagnostyki |
| `photo/komora_silnika.jpg` | Komora silnika 1.9 TDI ASV – lokalizacja EGR, N75 |
| `photo/urywek_diagnostyki.jpeg` | Fragment sesji diagnostycznej z AI (OpenCode) |

## 9. Struktura repozytorium

```
seat-toledo-obd2/
├── README.md                  ← niniejszy raport
├── WNIOSKI.md                 ← luźne podsumowanie projektu
├── PROMPT_DIAGNOSTYKI.md      ← prompt do powtórzenia diagnostyki
├── raport.pdf                 ← praca zaliczeniowa (PDF)
├── raport.tex                 ← źródło LaTeX
├── .gitignore
├── archive/                   ← stare wersje skryptów
├── data/
│   ├── obd_dane.txt           ← zebrane dane z jazdy próbnej
│   └── obd_dane.csv           ← dane w formacie CSV
├── photo/
│   ├── elm327.jpg             ← zdjęcie interfejsu ELM327
│   ├── toledo_incar.jpeg      ← wnętrze z laptopem
│   ├── komora_silnika.jpg     ← komora silnika
│   └── urywek_diagnostyki.jpeg ← sesja z AI
└── scripts/
    ├── obd_logger_v4.py       ← główny logger OBD2 (zalecany)
    ├── read_dtc.py            ← odczyt kodów błędów DTC
    ├── bt_pair.py             ← parowanie ELM327 przez D-Bus
    └── run_obd.sh             ← wrapper startowy
```

## 9. Instrukcja użycia

### Wymagania
- Python 3, BlueZ (bluetoothctl)
- ELM327 v2.1 (sparowany PIN 1234) lub VAG KKL 409.1

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
python3 scripts/obd_logger_v4.py
```

### Publikacja na GitHub
```bash
gh auth login        # jednorazowo
gh repo create seat-toledo-obd2 --public --source=. --remote=origin --push
```

---

## 11. Uwagi techniczne

### ELM327
Adapter użyty w diagnostyce to chiński klon na chipie **TDA81** (identyfikuje się jako ELM327 v2.1).
- Protokół ASV: **ISO 9141-2** (wykrywany jako A3)
- Ręczne ustawienie: `ATSP3` lub `ATSP4` (KWP 5BAUD)
- DTC przez KWP nie działa na tym klonie

### Plik danych
Format CSV: `czas,rpm,maf,map,boost,coolant,intake,speed,timing`

---

## Autor  
**Kacper Szafram**  

Dane zebrane na żywo z pojazdu przez interfejs ELM327 Bluetooth.  
Raport przygotowany przy użyciu narzędzi AI (OpenCode), Python, BlueZ, git/GitHub.
