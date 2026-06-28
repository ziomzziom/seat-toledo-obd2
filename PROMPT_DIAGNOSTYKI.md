# Prompt do powtórzenia diagnostyki

Poniższy prompt można użyć z dowolnym modelem AI (OpenCode, ChatGPT, Claude itp.)
do przeprowadzenia diagnostyki OBD2 Seata Toledo 2 z silnikiem 1.9 TDI ASV.

## Prompt

```
Przeprowadź pełną diagnostykę OBD2 samochodu Seat Toledo 2, 1.9 TDI ASV (110 KM)
przez interfejs ELM327 Bluetooth (MAC: A2:2A:19:04:00:00).

Problem: Samochód traci moc przy ~120 km/h, nie rozpędza się szybciej.
Objawy dodatkowe: świst przy 1800 obr/min, kliknięcie przy 1500 obr/min,
cieknąca uszczelka EGR.

Sprzęt: ELM327 Bluetooth (chiński klon TDA81, PIN 1234)
System: Linux (Kali) z BlueZ (bluetoothctl)
Język: Python 3

Wymagane kroki:

1. Sparuj ELM327 (bluetoothctl trust + pair, PIN 1234)
2. Połącz: bluetoothctl connect w tle, po 4s otwórz gniazdo Bluetooth
   (AF_BLUETOOTH, SOCK_STREAM, BTPROTO_RFCOMM) na MAC, channel 1
3. Init: ATZ, ATE0, ATS0, ATH0, ATSP0
4. Warmup: wysyłaj 010C (RPM) do 10 razy aż do odpowiedzi
5. Odczytaj DTC: 03, 07, 0A, 0101
6. Uruchom logger ciągły: RPM, MAF, MAP, temp, speed, timing co ~0.8s

Uwagi techniczne:
- ATSP0 wykrywa protokół A3 (ISO 9141-2) dla ASV
- Warmup wymaga 3-5 prób zanim ECU odpowie
- ELM327 może gubić połączenie – power cycle co kilka prób
- Przy "UNABLE TO CONNECT" – reset BT: bluetoothctl power off/on
- Jeśli DTC nie działa – potrzebny VAG KKL 409.1 + VCDS Lite

Normy dla ASV:
- MAF idle (ciepły): 4-10 g/s
- MAF idle (zimny): ~13 g/s (wyższe dawkowanie)
- MAF full load: 45-55 g/s
- MAP idle: ~100 kPa
- Boost max: 1.2-1.3 bar (~220-230 kPa)
- Overboost > 1.3 bar = potencjalny problem N75

Wyniki poprzedniej diagnostyki (dla porównania):
- MAF idle (zimny): 13.8 g/s
- MAF idle (ciepły): 8.3-8.7 g/s
- MAF pełne obciążenie: 71.1 g/s przy 2238 RPM
- MAP max: 248 kPa (+1.48 bar) – overboost
- DTC: brak (0 kodów)
- Temp płynu: 83-91°C
- Napięcie: 14.1V

Na podstawie zebranych danych:
1. Określ czy problem to overboost, uszkodzony MAF, czy coś innego
2. Zaproponuj kolejność czynności naprawczych
3. Wskaż które części zamówić (z numerami)
```
