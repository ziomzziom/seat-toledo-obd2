# Lista zakupów – serwis rozrządu + EGR (1.9 TDI ASV)

> Status: **2026-06** – zakupione w sklepie stacjonarnym.
> **Całkowity koszt: 728,66 zł brutto**

## Paragon – wszystkie pozycje (728,66 zł)

| # | Nr kat. | Część | Marka | Cena brutto |
|---|---------|-------|-------|------------|
| 1 | 1121290010 | Filtr powietrza | MEY | 30,97 zł |
| 2 | 36-0076 | Płyn do chłodnicy | MAX | 27,50 zł |
| 3 | 530008230 | Zestaw rozrządu (INA/Schaeffler) | INA | 408,83 zł |
| 4 | — | Olej TOTAL Quartz INEO ECS 5W-30 (5L) – **do zamiany na 5W-40** | TOTAL | 196,73 zł |
| 5 | 71-28781-10 | Uszczelka kolektora ssącego | REINZ | 7,98 zł |
| 6 | AJU01089900 | Uszczelka zaworu EGR | AJUSA | 7,05 zł |
| 7 | HU726/2X | Filtr oleju | MANN | 23,09 zł |
| 8 | KF-6109C | Filtr kabiny | MAXGEAR | 26,51 zł |

**Razem: 728,66 zł brutto**

## Zawory – ✅ N75 ZAMÓWIONY / ⏳ N18
| Część | Nr kat. | Cena | Status |
|-------|---------|------|--------|
| **Zawór N75** | 1J0 906 627 A | 99,00 zł | ✅ **Zamówiony** (Allegro) |
| Zawór N18 | — | — | ⏳ Nie potrzebny (brak związku z overboostem) |

**Link do N75 (zamówiony):** allegro.pl – "ZAWÓR TURBINY N75 1.9TDI 1J0906627A AUDI VW SEAT"

### Uwaga do diagnozy N75
- Multimetr: **N75 (biały) = 16,8 Ω** → elektrycznie sprawny, ale **mechanicznie może być zapchany nagarem** (overboost).
- N18 (czarny) niedostępny – **nie ma znaczenia**, bo nie steruje turbiną.
- Wymiana N75 = naprawa + test w jednym. Jeśli po wymianie overboost zostanie → to **VNT/wężyki**.

---

## Uwagi
- **Test zaworu N75** – zamienić miejscami z zaworem N18, aby sprawdzić
  czy overboost (utrata mocy >120 km/h) ustępuje.
- **Sprawdzić wężyki podciśnienia** (sparciałe / spękane).
- **Filtr kabinowy** to faktycznie **MAXGEAR** (nie Elemfil) – potwierdzone na paragonie.
- **Olej** – kupiony TOTAL Quartz INEO ECS 5W-30, ale **NIE wlany**. **NIEODPOWIEDNI**
  do tego silnika (ACEA C2, pod PSA/Peugeot-Citroën, **brak aprobat VW**). Wg VIN
  (VSSZZZ1MZ2B014443) to Seat Toledo 2, 1.9 TDI ASV 2001 → norma **VW 505.00 (5W-40)**.
  **Konieczna zamiana na 5W-40 z aprobatą VW 505.00/505.01** (ACEA B4):
  np. Total Quartz 9000 5W-40 / Castrol Edge 5W-40 / Motul 8100 5W-40.

Wstępnie pominięte: wężyki podciśnienia, uszczelka pod korek zaworów – decyzja w toku.

---

## Diagnostyka VAG – ✅ KABEL KKL ZAMÓWIONY

| Sprzęt | Cena | Status |
|--------|------|--------|
| **VAG COM KKL 409.1 USB (FTDI FT232RL)** | ~80 zł | ✅ **Zamówiony** (Allegro) |

**Po co:** odczyt błędów z aut VAG, których ELM327 (klon TDA81) nie obsługuje.

| Auto | Silnik | Protokół | ELM327 | KKL+VCDS |
|------|--------|----------|--------|----------|
| Seat Toledo 2 (2001) | 1.9 TDI ASV | OBD-II / KWP2000 | ✅ | ✅ |
| Skoda Octavia 1 (1999) | 1.6 benzyna | **KW1281** (brak OBD-II!) | ❌ | ✅ |

**Kluczowy wniosek:** Octavia 1.6 benzyna 1999 **nie obsługuje OBD-II** (EOBD dla benzyn obowiązkowe dopiero od 2001). Mówi tylko zastrzeżonym protokołem VAG **KW1281**, który czyta wyłącznie VCDS/VWTool. Dlatego ELM327 jej nie odczyta – potrzebny KKL + VCDS Lite (darmowy z ross-tech.com).
