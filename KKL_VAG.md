# Diagnostyka VAG kablem KKL (VCDS)

> Status: kabel KKL 409.1 FTDI **zakupiony**, narzędzie `kw1281test` **zbudowane i działa**.
> Zweryfikowane na Seacie Toledo 2 (1.9 TDI ASV): protokół **KW1281**, **9600 baud**, adres ECU **1**.

## Sprzęt i soft

| Element | Szczegóły |
|---------|-----------|
| Kabel | VAG COM KKL 409.1 USB (FTDI FT232R) |
| Port | `/dev/ttyUSB0` |
| Narzędzie | `kw1281test` (github.com/gmenounos/kw1281test) |
| Wymagane | .NET 10 SDK (zainstalowane w `~/.dotnet`) |

## Kluczowe ustawienia (ustalone eksperymentalnie)

| Parametr | Wartość |
|----------|---------|
| **Baud rate** | **9600** (nie 10400!) |
| Adres ECU | 1 (silnik) |
| Protokół | KW1281 |
| **Latency timer FTDI** | **1 ms** (domyślnie 255 → powoduje timeout!) |

## Uruchomienie (po podpięciu kabla + zapłon/silnik)

```bash
bash scripts/kkl_seat.sh
```

Skrypt robi: ustawia latency 1ms → odczytuje kody błędów.

## Pełny potencjał kabla (do zbudowania później)

`kw1281test` obsługuje mnóstwo funkcji poza odczytem błędów:

### Odczyt / kasowanie
- `ReadFaultCodes` / `ClearFaultCodes` – kody błędów

### Dane na żywo (measuring blocks)
- `GroupRead GROUP` – bloki pomiarowe (RPM, MAF, boost, temperatury)
- `ReadGroup GROUP` – pojedynczy odczyt grupy
- `ReadSoftwareCoding` / `SaveSoftwareCoding` – kodowanie

### Adaptacje
- `AdaptationRead CHANNEL` / `AdaptationSave` / `AdaptationTest`
- np. regulacja obrotów jałowych, dawki

### EEPROM (ostrożnie!)
- `DumpEeprom FILENAME` – zrzut EEPROM (backup!)
- `ReadEeprom ADDRESS COUNT` / `WriteEeprom` – odczyt/zapis

### Identyfikacja
- `GetIdent` / `ReadIdent` – numer sterownika, wersja softu

### Inne
- `ActuatorTest` – test siłowników (np. N75!)
- `AutoScan` – skan wszystkich modułów
- `BasicSetting GROUP` – ustawienia podstawowe

## Adresy modułów (VAG)

| Adres | Moduł |
|-------|-------|
| 1 | Silnik |
| 2 | Skrzynia biegów |
| 3 | ABS |
| 15 | Airbag |
| 17 | Licznik (zegary) |
| 25 | Immobilizer |
| 46 | Komfort |

## Uwagi

- **Latency 1ms jest krytyczne** – bez tego "Sync repeated" i timeout.
- Octavia 1.6 benzyna 1999 też używa KW1281 → to samo narzędzie, może inny baud/adres.
- Backup EEPROM **zawsze przed zapisem** – to świętość.
- Do flashowania mapy (EGR-off / Stage 1) to NIE wystarczy – potrzeba MPPS v13 + prostownik.
