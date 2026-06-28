# Wnioski i spostrzeżenia z projektu

## O projekcie
Diagnostyka Seata Toledo 2 (1.9 TDI ASV) z użyciem narzędzi AI (OpenCode) i interfejsu OBD2 Bluetooth.

## Co się udało
- Działający logger OBD2 przez Bluetooth w Pythonie
- Zebranie danych z jazdy (RPM, MAF, MAP, boost, temperatura)
- Wykrycie overboostu (+1.48 bar przy normie ~1.2-1.3)
- Potwierdzenie że MAF jest sprawny
- Stworzenie repozytorium na GitHub z dokumentacją
- Przeprowadzenie diagnostyki w pełni zdalnie (AI + laptop)

## Co nie wyszło
- Odczyt DTC przez ELM327 TDA81 – klon nie obsługuje KWP 2000 poprawnie
- Złapanie momentu utraty mocy przy 120 km/h – brak bezpiecznej drogi
- Niestabilne połączenie Bluetooth – częste page timeout, konieczność power cycle
- Nie sprawdziliśmy fizycznie N75 i wężyków podciśnienia

## Wnioski na przyszłość
1. **Sprzęt ma znaczenie** – chiński klon ELM327 to strata czasu. VAG KKL + VCDS od razu.
2. **AI pomaga ale nie zastąpi** – AI świetnie generuje skrypty i analizuje dane, ale nie posłucha silnika ani nie sprawdzi wężyka.
3. **Diagnostyka OBD2 ma granice** – overboost widzimy w danych, ale przyczynę (N75 / wężyk / VNT) trzeba sprawdzić ręcznie.
4. **GitHub to nie tylko kod** – repozytorium z dokumentacją + danymi to wartość sama w sobie.
5. **Współpraca człowiek + AI** – człowiek daje kontekst (objawy, dotyk, słuch), AI daje szybką analizę i automatyzację.
