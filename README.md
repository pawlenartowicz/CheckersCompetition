# Algorytmy

Każdy algorytm powinien być klasą w pythonie (wzór klasy zostanie udostępniony), zawierającą funkcję/metodę 'class.move()'.
Pełna dokumentacja takiej klasy, zostanie udostępniony 4 listopada.
Klasa powinna zostać zapisana jako nazwa_zespołu.py.

## Klasa / wrapper w Pythonie
```python
class bot():
    def __init__(self):
        pass

    def move(self, plansza, ruchy):
        '''
        Metoda która wybiera ruch

        Argumenty:
            plansza: aktualna plansza (z perspektywy gracza)
            ruchy: lista legalnych ruchów
        Zwraca:
            wybrany_ruch: jeden z legalnych ruchów
        '''
        wybrany_ruch = ruchy[0] # dowolny algorytm

        return wybrany_ruch
```
Taka klasa może też być wrapperem do c++; mogę pomóc z pybind11 i ctypes

### Jeżeli chcecie skorzystać z c++

```python
import kod_cpp

class bot():
    def __init__(self):
        pass

    def move(self, plansza, ruchy)
        return kod_cpp.funkcja(plansza,ruchy)
```
I kod w C++ (trzeba uważać na argumenty!)
```cpp
#include <pybind11/pybind11.h>
using namespace std;

tuple<tuple<int, int>, tuple<int, int>> funkcja(){} //wasza funckja

PYBIND11_MODULE(kod_cpp, m) {
    m.def("funkcja", &funkcja, "Wybrany ruch");
}
```
I trzeba wpisać odpowiednie parametry w Bashu
```bash
g++ -O3 -Wall -shared -std=c++11 -fPIC \
    $(python3 -m pybind11 --includes) \
    kod_cpp.cpp -o kod_cpp$(python3-config --extension-suffix)
```

Alternatywnie, jeżeli będziecie mieli kod w C++, to pomogę z wrapperem

## Zasady
- **Wariant**: warcaby angielskie — uproszczone zasady, plansza 8x8, po promocji piony (damki) ruszają się o 1 ruch
- **Brak dostępu do internetu** podczas turnieju
- **2 mecze**: każde 2 drużyny grają z sobą 2 mecze, raz pierwszy ruch ma jedna drużyna, raz druga
- **Dogrywka**: jeżeli po 2 meczach jest 1-1, przechodzimy do dogrywki — zespoły tracą po losowej figurze i rozgrywają 2 kolejne mecze
- **Warunki remisu**:
  - 3-krotne powtórzenie pozycji = remis
  - 20 ruchów bez ruchu pionem lub bicia = remis
  - W sytuacji remisowej przegrywa algorytm któremu zostało mniej czasu
- **Limity zasobów**:
  - Maksymalny rozmiar kodu: 4 MiB
  - Maksymalny rozmiar pamięci RAM: 1 GiB

### System limitu czasowego

Przed każdą grą wykonywany jest **benchmark czasowy** (domyślnie: 64³ operacji `np.sum()` na macierzy 8x8), który określa limit czasu na ruch.

**Zasady timeoutu:**
- Każdy bot ma **benchmark_time** sekund na wykonanie ruchu
- Maksymalny czas to **2 × benchmark_time** (po tym następuje przerwanie wątku)
- Każdy bot ma **3 time_flags** (flagi przekroczenia czasu)

**Mechanizm:**
1. Bot wykonuje ruch w czasie ≤ benchmark_time → **OK, bez kary**
2. Bot przekracza benchmark_time ale < 2×benchmark_time:
   - Jeśli ma time_flags > 0 → **ruch akceptowany, -1 flag**
   - Jeśli time_flags = 0 → **losowy ruch zamiast ruchu bota**
3. Bot przekracza 2×benchmark_time → **timeout, losowy ruch**

**Przykład:**
- Benchmark = 0.33s
- Limit normalny: 0.33s
- Limit maksymalny: 0.66s
- Bot wykonuje ruch w 0.40s → przekroczenie, użycie time_flag
- Bot wykonuje ruch w 0.70s → timeout, losowy ruch


## Format zmiennych

### Plansza (8x8)

Plansza jest podawana jako **numpy array 8x8** reprezentujący pełną szachownicę:

```python
# Przykład: pozycja początkowa (z perspektywy gracza 1)
[[None,  2,  None,  2,  None,  2,  None,  2],   # Wiersz 0 - przeciwnik
 [  2, None,  2,  None,  2,  None,  2,  None],  # Wiersz 1
 [None,  2,  None,  2,  None,  2,  None,  2],   # Wiersz 2
 [  0, None,  0,  None,  0,  None,  0,  None],  # Wiersz 3 - puste
 [None,  0,  None,  0,  None,  0,  None,  0],   # Wiersz 4 - puste
 [  1, None,  1,  None,  1,  None,  1,  None],  # Wiersz 5 - gracz
 [None,  1,  None,  1,  None,  1,  None,  1],   # Wiersz 6
 [  1, None,  1,  None,  1,  None,  1,  None]]  # Wiersz 7
```

**Kodowanie pól:**
- `None` = białe pole (niedostępne do gry)
- `0` = puste ciemne pole
- `1` = pion gracza
- `2` = pion przeciwnika
- `3` = damka gracza (król)
- `4` = damka przeciwnika (król)

**Ciemne pola** (dostępne do gry): te gdzie `(wiersz + kolumna) % 2 == 1`

**Perspektywa**: Plansza jest **zawsze widziana z perspektywy aktualnego gracza**. Po każdym ruchu następuje obrót o 180° i zamiana pionków (1↔2, 3↔4).

### Ruchy

Ruchy to **lista krotek** w formacie: `((start_wiersz, start_kolumna), (koniec_wiersz, koniec_kolumna))`

```python
# Przykład legalnych ruchów:
[((5, 0), (4, 1)),   # Pion z (5,0) na (4,1)
 ((5, 2), (4, 1)),   # Pion z (5,2) na (4,1)
 ((5, 2), (4, 3))]   # Pion z (5,2) na (4,3)
```

**Ruchy zwykłe**: ±1 w wierszach i kolumnach (ruch diagonalny)
**Bicia**: ±2 w wierszach i kolumnach (przeskok przez pionka przeciwnika)

### Tryb debug

Tryb debug zapisuje przebieg gry do pliku `debug_gra.txt`:

```python
gra = GRA("bot1", "bot2", debug=True)
zwyciezca = gra.start()
```

**Zawartość debug_gra.txt:**
- Wynik benchmarku czasowego i limity
- Dla każdego ruchu:
  - Numer ruchu i grający bot
  - Dostępne ruchy (wszystkie legalne możliwości)
  - Czas wykonania ruchu
  - Status (w limicie / przekroczono benchmark / timeout)
  - Wybrany ruch
- Informacje o wielobiciach i zmianach perspektywy

**Przykład wpisu w debug:**
```
======================================================================
RUCH #1
======================================================================
Bot1
Dostępne ruchy (7): [((5, 0), (4, 1)), ((5, 2), (4, 1)), ...]
Czas wykonania: 0.000493s (limit: 0.331530s, max: 0.663061s)
Status: W limicie czasu
Wybrany ruch: ((5, 0), (4, 1))
```

### Konfiguracja time_flags

```python
# Ustaw liczbę dozwolonych przekroczeń czasu (domyślnie 3)
gra = GRA("bot1", "bot2", debug=True, time_flags=99)
```

## Dodatkowe informacje
- Bot zostanie udostępniony na Google Colab, do samodzielnego testowania
- Na co najmniej miesiąc przed turniejem, będą udostępnione testy, by zobaczyć, czy kod zadziała na turnieju
- Najchętniej widziałbym turniej w wersji live
- Będę wrzucać regularnie materiały na GitHub
- Funkcja określająca legalne ruchy będzie dostępna publicznie, zespoły mogą jej używać w swoim kodzie 'as is', lub zoptymalizować

## Terminarz
- 4.11 GITHUB + Google Colab + Random-Bot (1 dzień opóźnienia)
- 22.12 pełna mechanika
- 26.12 
- 20.01 Turniej
Powstanie po wykładzie we wtorek, 28.10