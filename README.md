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
- wariant 1 — warcaby angielskie — uproszczone zasady, plansza 8x8, po promocji piony ruszają się o 1 ruch
- wariant 2 — warcaby polskie — bardziej złożone zasady, plansza 10x10, po promocji dowolna liczba ruchów
- brak dostępu do internetu
- 2 mecze — każde 2 drużyny grają z sobą 2 mecze, raz pierwszy ruch ma jedna drużyna, raz druga
- jeżeli po 2 meczach jest 1-1, przechodzimy do dogrywki, w dogrywce zespoły tracą po losowej figurze i znowu rozgrywają 2 mecze
- wprowadzamy limit czasu (będzie on skalowany dla konkretnego komputera na, jako x*czas wykonania jakiegoś obliczeia), pradopodobnie około 1 minuty na grę na średnim sprzęcie
- mecze nie kończą się remisem, w sytuacji 'remisowej' przegrywa algorytm któremy zostało mniej czasu
- maksymaly rozmiar kodu: 4 MiB
- maksymalny rozmiar pamięci RAM: 1 GiB — na teście przeciwko botowi z losowymi ruchami (mile widziane nie 'oszukiwanie')


## Format zmiennych
plansza jest podawana dalej jako np.array 4x8 lub 5x10 (usunięte białe pola)
```python
[[2,2,2,2],
 [2,2,2,2],
 [2,2,2,2],
 [0,0,0,0],
 [0,0,0,0],
 [1,1,1,1],
 [1,1,1,1],
 [1,1,1,1]]
```
Gdzie "1" oznacza piony gracza, "2" piony przeciwnika, "3" króla gracza (piona po przemianie), "4" piona przeciwnika.

ruchy jest listą legalnych legalnych ruchów — krotek, z pozycją na początku i po ruchu. Plansza jest zawsze widziana z perspektywy gracza, 1 jest po jego stronie, 8 po stronie przeciwnika itd..
```python
[((3,1)(4,1)), ((3,2)(4,1)), ((3,2)(4,2))]
```

## Dodatkowe informacje
- Bot zostanie udostępniony na Google Colab, do samodzielnego testowania.
- Na co najmniej miesiąc przed turniejem, będą udostępnione testy, by zobaczyć, czy nasz kod zadziała na turnieju
- Najchętniej widziałbym turniej w wersji live
- Będę wrzucać regularnie materiały na GitHub
- Funkcja określająca legalne ruchy będzie dostępna publicznie, zespoły mogą jej używać w swoim kodzie 'as is', lub zoptymalizować.

## Terminarz
- 4.11 GITHUB + Google Colab + Random-Bot (1 dzień opóźnienia)
- 11.11 Bicia i ruchy królem, dziedziczenie klasy (możliwość korzystania z funkcji z głównej klasy)
- 25.11 Więcej botów
- 16.12 Testy
- 20.01 Turniej
Powstanie po wykładzie we wtorek, 28.10