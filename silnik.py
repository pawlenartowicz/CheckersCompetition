import numpy as np
import importlib.util
import os
import time
import threading
import random
import time

def time_benchmark(iterations = (64,3)):
    # Inicjalizacja macierzy 8x8
    matrix = np.random.randint(0, 5, size=(8, 8), dtype=np.int8)

    itt = iterations[0] ** iterations[1]

    start = time.time()
    for i in range(itt):
        np.sum(matrix)

    end = time.time()
    elapsed = end - start

    return elapsed



class GRA:
    def __init__(self, bot1, bot2, debug=False, time_flags=3):
        """
        Inicjalizacja gry w warcaby.

        Plansza 8x8 gdzie:
        - None = białe pole (niedostępne)
        - 0 = puste ciemne pole
        - 1 = pion gracza
        - 2 = pion przeciwnika
        - 3 = król gracza
        - 4 = król przeciwnika

        Args:
            bot1: pierwszy bot (instance lub string)
            bot2: drugi bot (instance lub string)
            debug: jeśli True, zapisuje każdą planszę do pliku debug_gra.txt
        """
        self.debug = debug
        self.debug_file = None
        self.move_number = 0

        if self.debug:
            self.debug_file = open("debug_gra.txt", "w", encoding="utf-8")
            self.debug_file.write("="*70 + "\n")
            self.debug_file.write("DEBUG GRY W WARCABY\n")
            self.debug_file.write("="*70 + "\n\n")

        # Inicjalizacja planszy 8x8
        self.plansza = np.full((8, 8), None, dtype=object)

        # Wypełnij ciemne pola
        for row in range(8):
            for col in range(8):
                # Ciemne pola: (row + col) % 2 == 1
                if (row + col) % 2 == 1:
                    if row < 3:
                        self.plansza[row, col] = 2  # Przeciwnik
                    elif row > 4:
                        self.plansza[row, col] = 1  # Gracz
                    else:
                        self.plansza[row, col] = 0  # Puste

        # Załaduj botów
        if type(bot1) == str:
            self.bot1 = self._zaladuj_bota(bot1)
        else:
            self.bot1 = bot1

        if type(bot2) == str:
            self.bot2 = self._zaladuj_bota(bot2)
        else:
            self.bot2 = bot2

        self.bot1_time_flags = time_flags
        self.bot2_time_flags = time_flags

        # Śledzenie pozycji i ruchów dla remisu
        self.pozycje_planszy = {}  # hash -> liczba wystąpień
        self.ruchy_bez_bicia_promocji = 0  # licznik ruchów bez bicia/promocji

    def _zaladuj_bota(self, nazwa_bota):
        """Ładuje klasę bota z pliku w folderze boty."""
        sciezka_bota = os.path.join(os.path.dirname(__file__), 'boty', f'{nazwa_bota}.py')
        spec = importlib.util.spec_from_file_location(nazwa_bota, sciezka_bota)
        modul = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modul)
        return modul.bot()

    def _wywolaj_bota_z_timeoutem(self, bot, plansza, ruchy, timeout, bot_number):
        """
        Wywołuje bota z timeoutem.

        Args:
            bot: instancja bota
            plansza: aktualna plansza
            ruchy: legalne ruchy
            timeout: maksymalny czas w sekundach
            bot_number: numer bota (1 lub 2)

        Returns:
            (wybrany_ruch, czas_wykonania, przekroczono_limit)
        """
        result = [None]

        def bot_wrapper():
            try:
                result[0] = bot.move(plansza, ruchy)
            except Exception as e:
                if self.debug:
                    self.debug_file.write(f"\n!!! BŁĄD w bocie: {e}\n")
                result[0] = None

        start_time = time.time()
        thread = threading.Thread(target=bot_wrapper)
        thread.daemon = True
        thread.start()
        thread.join(timeout=timeout)
        elapsed_time = time.time() - start_time

        if thread.is_alive():
            # Bot nie skończył w czasie - zwróć losowy ruch
            if self.debug:
                self.debug_file.write(f"\n!!! TIMEOUT! Bot{bot_number} przekroczył limit {timeout:.6f}s\n")
            return random.choice(ruchy), elapsed_time, True

        # Bot skończył w czasie
        if result[0] is None or result[0] not in ruchy:
            # Bot zwrócił niepoprawny ruch
            if self.debug:
                self.debug_file.write(f"\n!!! NIEPOPRAWNY RUCH od Bot{bot_number}: {result[0]}\n")
            return random.choice(ruchy), elapsed_time, False

        return result[0], elapsed_time, False

    def _jest_ciemne_pole(self, row, col):
        """Sprawdza czy pole jest ciemne (dostępne do gry)."""
        return (row + col) % 2 == 1

    def znajdz_legalne_ruchy(self, plansza, tylko_dla_pozycji=None):
        """
        Znajduje legalne ruchy dla gracza.

        Args:
            plansza: numpy array 8x8
            tylko_dla_pozycji: tuple (row, col) - jeśli podane, zwraca ruchy tylko dla tego pionka

        Returns:
            lista krotek ((start_row, start_col), (end_row, end_col))
        """
        bicia = []
        ruchy = []

        # Określ które pozycje sprawdzać
        if tylko_dla_pozycji is not None:
            pozycje = [tylko_dla_pozycji]
        else:
            pozycje = [(r, c) for r in range(8) for c in range(8)]

        # Znajdź wszystkie bicia
        for row, col in pozycje:
            piece = plansza[row, col]
            if piece in [1, 3]:  # Pionki gracza
                bicia.extend(self._znajdz_bicia(plansza, row, col, piece))

        # Jeśli są bicia, zwróć tylko bicia (obowiązkowe)
        if bicia:
            return bicia

        # Jeśli nie ma bić, znajdź zwykłe ruchy
        for row, col in pozycje:
            piece = plansza[row, col]
            if piece in [1, 3]:  # Pionki gracza
                ruchy.extend(self._znajdz_ruchy(plansza, row, col, piece))

        return ruchy

    def _znajdz_bicia(self, plansza, row, col, piece):
        """
        Znajduje bicia dla pionka.
        Bicia: przeskok o ±2, ±2 jeśli na ±1, ±1 jest przeciwnik.
        """
        bicia = []

        kierunki = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for dr, dc in kierunki:
            # Pozycja przeciwnika (sąsiednie pole)
            opp_row, opp_col = row + dr, col + dc

            # Pozycja docelowa (pole za przeciwnikiem)
            target_row, target_col = row + 2*dr, col + 2*dc

            # Sprawdź czy pozycje są w granicach
            if not (0 <= opp_row < 8 and 0 <= opp_col < 8):
                continue
            if not (0 <= target_row < 8 and 0 <= target_col < 8):
                continue

            # Sprawdź czy na sąsiednim polu jest przeciwnik
            opp_piece = plansza[opp_row, opp_col]
            if opp_piece not in [2, 4]:  # Musi być pionek przeciwnika
                continue

            # Sprawdź czy pole docelowe jest puste
            if plansza[target_row, target_col] != 0:
                continue

            # To jest legalne bicie
            bicia.append(((row, col), (target_row, target_col)))

        return bicia

    def _znajdz_ruchy(self, plansza, row, col, piece):
        """
        Znajduje zwykłe ruchy dla pionka.
        Ruchy: przesunięcie o ±1, ±1 na puste pole.
        """
        ruchy = []

        # Określ kierunki na podstawie typu pionka
        if piece == 1:  # Zwykły pion - tylko do przodu
            kierunki = [(-1, -1), (-1, 1)]
        elif piece == 3:  # Król - wszystkie kierunki
            kierunki = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        else:
            return []

        for dr, dc in kierunki:
            target_row, target_col = row + dr, col + dc

            # Sprawdź czy pozycja jest w granicach
            if not (0 <= target_row < 8 and 0 <= target_col < 8):
                continue

            # Sprawdź czy pole docelowe jest puste
            if plansza[target_row, target_col] == 0:
                ruchy.append(((row, col), (target_row, target_col)))

        return ruchy

    def update(self, plansza, ruch):
        """
        Zwraca nową planszę po wykonaniu ruchu (nie modyfikuje wejściowej planszy).

        Args:
            plansza: numpy array 8x8 - plansza wejściowa
            ruch: ((start_row, start_col), (end_row, end_col))

        Returns:
            (nowa_plansza: numpy array, bylo_bicie: bool, pozycja_koncowa: tuple)
        """
        # Stwórz kopię planszy
        nowa_plansza = plansza.copy()

        start, end = ruch
        start_row, start_col = start
        end_row, end_col = end

        # Pobierz pionek
        piece = nowa_plansza[start_row, start_col]

        # Sprawdź czy to bicie
        row_diff = abs(end_row - start_row)
        bylo_bicie = (row_diff == 2)

        if bylo_bicie:
            # Usuń pionek przeciwnika (w środku między startem a końcem)
            captured_row = (start_row + end_row) // 2
            captured_col = (start_col + end_col) // 2
            nowa_plansza[captured_row, captured_col] = 0

        # Przenieś pionek
        nowa_plansza[end_row, end_col] = piece
        nowa_plansza[start_row, start_col] = 0

        # Sprawdź promocję do króla
        if end_row == 0 and piece == 1:
            nowa_plansza[end_row, end_col] = 3

        return nowa_plansza, bylo_bicie, (end_row, end_col)

    def _update(self, ruch):
        """
        Aktualizuje planszę na podstawie ruchu.

        Args:
            ruch: ((start_row, start_col), (end_row, end_col))

        Returns:
            (bylo_bicie: bool, byla_promocja: bool, pozycja_koncowa: tuple)
        """
        start, end = ruch
        start_row, start_col = start
        end_row, end_col = end

        # Pobierz pionek
        piece = self.plansza[start_row, start_col]

        # Sprawdź czy to bicie
        row_diff = abs(end_row - start_row)
        bylo_bicie = (row_diff == 2)

        if bylo_bicie:
            # Usuń pionek przeciwnika (w środku między startem a końcem)
            captured_row = (start_row + end_row) // 2
            captured_col = (start_col + end_col) // 2
            self.plansza[captured_row, captured_col] = 0

        # Przenieś pionek
        self.plansza[end_row, end_col] = piece
        self.plansza[start_row, start_col] = 0

        # Sprawdź promocję do króla
        byla_promocja = False
        if end_row == 0 and piece == 1:
            self.plansza[end_row, end_col] = 3
            byla_promocja = True

        return bylo_bicie, byla_promocja, (end_row, end_col)

    def zamien_perspektywe(self, plansza):
        """
        Zamienia perspektywę - odwraca planszę i zamienia pionki.
        """
        # Mapowanie: 0->0, 1->2, 2->1, 3->4, 4->3, None->None
        def zamien_pionek(p):
            if p is None:
                return None
            elif p == 0:
                return 0
            elif p == 1:
                return 2
            elif p == 2:
                return 1
            elif p == 3:
                return 4
            elif p == 4:
                return 3
            return p

        # Odwróć planszę i zamień pionki
        odwrocona = np.rot90(plansza, 2)  # Obrót o 180 stopni
        zamieniona = np.vectorize(zamien_pionek)(odwrocona)

        return zamieniona

    def _hash_planszy(self, plansza):
        """
        Zwraca hash planszy do wykrywania powtórzeń.
        Konwertuje numpy array na krotkę i liczy hash.
        """
        # Konwertuj None na -1 dla spójności hashowania
        plansza_do_hasha = tuple(
            tuple(-1 if cell is None else cell for cell in row)
            for row in plansza
        )
        return hash(plansza_do_hasha)

    def start(self, show=False, notebook=False, show_time=1.0):
        """Rozpoczyna grę między dwoma botami."""
        runda = 0
        pierwsza_runda = True

        # Wykonaj benchmark czasowy na początku gry
        benchmark_time = time_benchmark()
        if self.debug:
            self.debug_file.write(f"TIME BENCHMARK: {benchmark_time:.6f} sekund na ruch\n")
            self.debug_file.write(f"Limit czasowy: {benchmark_time:.6f}s (normalny), {2*benchmark_time:.6f}s (maksymalny)\n")
            self.debug_file.write(f"Bot1 time_flags: {self.bot1_time_flags}\n")
            self.debug_file.write(f"Bot2 time_flags: {self.bot2_time_flags}\n")
            self.debug_file.write("="*70 + "\n")

        # Wyświetl początkową planszę
        if show:
            if not notebook:
                print(f"\033[KRunda: {runda}")
            else:
                print(f"Runda: {runda}")
                from IPython.display import clear_output, display, HTML
                display(HTML("<style>pre, code {font-family: 'Courier New', monospace !important;}</style>"))
            self.wyswietl_plansze(self.plansza, pokaz_legende=True, notebook=notebook)
            time.sleep(show_time * 2)
            pierwsza_runda = False

        while True:
            # Pętla wielobicia tym samym pionkiem
            pozycja_dla_wielobicia = None

            while True:
                # Znajdź legalne ruchy
                if pozycja_dla_wielobicia is not None:
                    # Podczas wielobicia: sprawdź TYLKO bicia dla tego pionka
                    legalne_ruchy = []
                    piece = self.plansza[pozycja_dla_wielobicia[0], pozycja_dla_wielobicia[1]]
                    if piece in [1, 3]:
                        legalne_ruchy = self._znajdz_bicia(self.plansza,
                                                           pozycja_dla_wielobicia[0],
                                                           pozycja_dla_wielobicia[1],
                                                           piece)
                else:
                    # Normalny ruch: wszystkie legalne ruchy
                    legalne_ruchy = self.znajdz_legalne_ruchy(self.plansza)

                # Sprawdź koniec gry lub wielobicia
                if len(legalne_ruchy) == 0:
                    if pozycja_dla_wielobicia is not None:
                        # Koniec wielobicia - brak kolejnych bić
                        break
                    else:
                        # Koniec gry - brak ruchów
                        poprzedni_gracz = 2 if runda % 2 == 0 else 1

                        if show:
                            if notebook:
                                clear_output(wait=True)
                            else:
                                print("\033[21A", end="")

                            if runda % 2 == 1:
                                plansza_do_wyswietlenia = self.zamien_perspektywe(self.plansza)
                            else:
                                plansza_do_wyswietlenia = self.plansza

                            if notebook:
                                print(f"Runda: {runda} - KONIEC GRY!")
                                display(HTML("<style>pre, code {font-family: 'Courier New', monospace !important;}</style>"))
                                self.wyswietl_plansze(plansza_do_wyswietlenia, pokaz_legende=False, notebook=True)
                                print(f"\n🎉 Gratulacje! Wygrywa Bot {poprzedni_gracz}! 🎉\n")
                            else:
                                print(f"\033[KRunda: {runda} - KONIEC GRY!")
                                self.wyswietl_plansze(plansza_do_wyswietlenia, pokaz_legende=False, notebook=notebook)
                                print(f"\033[K\n🎉 Gratulacje! Wygrywa Bot {poprzedni_gracz}! 🎉\n")

                        # Zamknij plik debug
                        if self.debug and self.debug_file:
                            self.debug_file.write(f"\n\n{'='*70}\n")
                            self.debug_file.write(f"KONIEC GRY - Wygrywa Bot {poprzedni_gracz}\n")
                            self.debug_file.write(f"{'='*70}\n")
                            self.debug_file.close()
                            print(f"\n[DEBUG] Zapisano historię gry do pliku: debug_gra.txt\n")

                        return poprzedni_gracz

                # Wybierz ruch
                if len(legalne_ruchy) == 1:
                    # Ruch automatyczny
                    wybrany_ruch = legalne_ruchy[0]
                    if self.debug:
                        self.move_number += 1
                        self.debug_file.write(f"\n{'='*70}\n")
                        self.debug_file.write(f"RUCH #{self.move_number}\n")
                        self.debug_file.write(f"{'='*70}\n")
                        self.debug_file.write(f"Ruch automatyczny (tylko 1 możliwy)\n")
                        self.debug_file.write(f"Dostępne ruchy: {legalne_ruchy}\n")
                        self.debug_file.write(f"Wybrany ruch: {wybrany_ruch}\n")
                else:
                    # Zapytaj bota z timeoutem
                    aktualny_bot = self.bot1 if runda % 2 == 0 else self.bot2
                    bot_number = 1 if runda % 2 == 0 else 2
                    aktualne_time_flags = self.bot1_time_flags if runda % 2 == 0 else self.bot2_time_flags

                    if self.debug:
                        self.move_number += 1
                        self.debug_file.write(f"\n{'='*70}\n")
                        self.debug_file.write(f"RUCH #{self.move_number}\n")
                        self.debug_file.write(f"{'='*70}\n")
                        self.debug_file.write(f"Bot{bot_number}\n")
                        self.debug_file.write(f"Dostępne ruchy ({len(legalne_ruchy)}): {legalne_ruchy}\n")

                    # Wywołaj bota z timeoutem 2x benchmark_time
                    wybrany_ruch, elapsed_time, timeout_exceeded = self._wywolaj_bota_z_timeoutem(
                        aktualny_bot, self.plansza, legalne_ruchy, 2 * benchmark_time, bot_number
                    )

                    # Sprawdź czy przekroczono normalny limit benchmark_time
                    przekroczono_benchmark = elapsed_time > benchmark_time

                    if self.debug:
                        self.debug_file.write(f"Czas wykonania: {elapsed_time:.6f}s (limit: {benchmark_time:.6f}s, max: {2*benchmark_time:.6f}s)\n")

                    if timeout_exceeded:
                        # Przekroczono 2x benchmark - losowy ruch
                        if self.debug:
                            self.debug_file.write(f"Status: PRZEKROCZONO 2x LIMIT! Użyto losowego ruchu.\n")
                    elif przekroczono_benchmark:
                        # Przekroczono benchmark ale nie 2x
                        if aktualne_time_flags > 0:
                            # Ma flagi - akceptuj ruch, pomniejsz flagę
                            if runda % 2 == 0:
                                self.bot1_time_flags -= 1
                            else:
                                self.bot2_time_flags -= 1
                            if self.debug:
                                self.debug_file.write(f"Status: PRZEKROCZONO BENCHMARK! Użyto time_flag (pozostało: {aktualne_time_flags - 1})\n")
                        else:
                            # Brak flag - użyj losowego ruchu
                            wybrany_ruch = random.choice(legalne_ruchy)
                            if self.debug:
                                self.debug_file.write(f"Status: PRZEKROCZONO BENCHMARK bez flag! Użyto losowego ruchu.\n")
                    else:
                        # W limicie
                        if self.debug:
                            self.debug_file.write(f"Status: W limicie czasu\n")

                    if self.debug:
                        self.debug_file.write(f"Wybrany ruch: {wybrany_ruch}\n")

                # Wykonaj ruch
                bylo_bicie, byla_promocja, pozycja_koncowa = self._update(wybrany_ruch)

                # Sprawdź czy można kontynuować wielobicie
                if bylo_bicie:
                    # Podczas wielobicia sprawdzaj TYLKO bicia, nie zwykłe ruchy
                    piece = self.plansza[pozycja_koncowa[0], pozycja_koncowa[1]]
                    kolejne_bicia = self._znajdz_bicia(self.plansza, pozycja_koncowa[0], pozycja_koncowa[1], piece)
                    if len(kolejne_bicia) > 0:
                        if self.debug:
                            self.debug_file.write(f">>> Wielobicie - kontynuacja dla pionka na {pozycja_koncowa}\n")
                        pozycja_dla_wielobicia = pozycja_koncowa
                        continue

                # Koniec tury
                break

            # Aktualizuj licznik ruchów bez bicia/promocji
            if bylo_bicie or byla_promocja:
                self.ruchy_bez_bicia_promocji = 0
                if self.debug:
                    self.debug_file.write(f">>> Reset licznika (bicie={bylo_bicie}, promocja={byla_promocja})\n")
            else:
                self.ruchy_bez_bicia_promocji += 1
                if self.debug:
                    self.debug_file.write(f">>> Licznik ruchów bez bicia/promocji: {self.ruchy_bez_bicia_promocji}\n")

            # Sprawdź remis przez 20 ruchów bez bicia/promocji
            if self.ruchy_bez_bicia_promocji >= 20:
                if show:
                    if notebook:
                        clear_output(wait=True)
                    else:
                        print("\033[21A", end="")

                    if runda % 2 == 1:
                        plansza_do_wyswietlenia = self.zamien_perspektywe(self.plansza)
                    else:
                        plansza_do_wyswietlenia = self.plansza

                    if notebook:
                        print(f"Runda: {runda} - REMIS!")
                        display(HTML("<style>pre, code {font-family: 'Courier New', monospace !important;}</style>"))
                        self.wyswietl_plansze(plansza_do_wyswietlenia, pokaz_legende=False, notebook=True)
                        print(f"\n🤝 Remis! 20 ruchów bez bicia lub promocji 🤝\n")
                    else:
                        print(f"\033[KRunda: {runda} - REMIS!")
                        self.wyswietl_plansze(plansza_do_wyswietlenia, pokaz_legende=False, notebook=notebook)
                        print(f"\033[K\n🤝 Remis! 20 ruchów bez bicia lub promocji 🤝\n")

                if self.debug and self.debug_file:
                    self.debug_file.write(f"\n\n{'='*70}\n")
                    self.debug_file.write(f"REMIS - 20 ruchów bez bicia lub promocji\n")
                    self.debug_file.write(f"{'='*70}\n")
                    self.debug_file.close()
                    print(f"\n[DEBUG] Zapisano historię gry do pliku: debug_gra.txt\n")

                return 0  # Remis

            # Zamień perspektywę
            if self.debug:
                self.debug_file.write(f"\n{'='*70}\n>>> Zamiana perspektywy\n{'='*70}\n")
            self.plansza = self.zamien_perspektywe(self.plansza)
            runda += 1

            # Sprawdź remis przez 3-krotne powtórzenie pozycji
            hash_planszy = self._hash_planszy(self.plansza)
            if hash_planszy in self.pozycje_planszy:
                self.pozycje_planszy[hash_planszy] += 1
            else:
                self.pozycje_planszy[hash_planszy] = 1

            if self.pozycje_planszy[hash_planszy] >= 3:
                if show:
                    if notebook:
                        clear_output(wait=True)
                    else:
                        print("\033[21A", end="")

                    if runda % 2 == 1:
                        plansza_do_wyswietlenia = self.zamien_perspektywe(self.plansza)
                    else:
                        plansza_do_wyswietlenia = self.plansza

                    if notebook:
                        print(f"Runda: {runda} - REMIS!")
                        display(HTML("<style>pre, code {font-family: 'Courier New', monospace !important;}</style>"))
                        self.wyswietl_plansze(plansza_do_wyswietlenia, pokaz_legende=False, notebook=True)
                        print(f"\n🤝 Remis! 3-krotne powtórzenie pozycji 🤝\n")
                    else:
                        print(f"\033[KRunda: {runda} - REMIS!")
                        self.wyswietl_plansze(plansza_do_wyswietlenia, pokaz_legende=False, notebook=notebook)
                        print(f"\033[K\n🤝 Remis! 3-krotne powtórzenie pozycji 🤝\n")

                if self.debug and self.debug_file:
                    self.debug_file.write(f"\n\n{'='*70}\n")
                    self.debug_file.write(f"REMIS - 3-krotne powtórzenie pozycji\n")
                    self.debug_file.write(f"{'='*70}\n")
                    self.debug_file.close()
                    print(f"\n[DEBUG] Zapisano historię gry do pliku: debug_gra.txt\n")

                return 0  # Remis

            # Wyświetl planszę
            if show:
                if notebook:
                    clear_output(wait=True)
                else:
                    if not pierwsza_runda:
                        print("\033[21A", end="")

                if runda % 2 == 1:
                    plansza_do_wyswietlenia = self.zamien_perspektywe(self.plansza)
                else:
                    plansza_do_wyswietlenia = self.plansza

                if notebook:
                    print(f"Runda: {runda}")
                    display(HTML("<style>pre, code {font-family: 'Courier New', monospace !important;}</style>"))
                    self.wyswietl_plansze(plansza_do_wyswietlenia, pokaz_legende=pierwsza_runda, notebook=True)
                else:
                    print(f"\033[KRunda: {runda}")
                    self.wyswietl_plansze(plansza_do_wyswietlenia, pokaz_legende=pierwsza_runda, notebook=notebook)

                if pierwsza_runda:
                    pierwsza_runda = False

                time.sleep(show_time)

    def wyswietl_plansze(self, plansza=None, pokaz_legende=True, notebook=False):
        """Wyświetla planszę 8x8."""
        if plansza is None:
            plansza = self.plansza

        # Kolory ANSI
        RESET = '\033[0m'
        RED = '\033[91m'
        BLUE = '\033[94m'
        GRAY = '\033[90m'

        # Symbole
        EMPTY_DARK = '·'
        PIECE = '●'
        KING = '▣'

        clear_line = "" if notebook else "\033[K"

        print(f"\n{clear_line}╔═══╤═══╤═══╤═══╤═══╤═══╤═══╤═══╗")

        for row in range(8):
            print(f"{clear_line}║", end="")
            for col in range(8):
                val = plansza[row, col]

                if val is None:
                    # Białe pole (niedostępne)
                    print("   ", end="")
                elif val == 0:
                    # Puste ciemne pole
                    print(f" {EMPTY_DARK} ", end="")
                elif val == 1:
                    # Pion gracza (niebieski)
                    print(f" {BLUE}{PIECE}{RESET} ", end="")
                elif val == 2:
                    # Pion przeciwnika (czerwony)
                    print(f" {RED}{PIECE}{RESET} ", end="")
                elif val == 3:
                    # Król gracza
                    print(f" {BLUE}{KING}{RESET} ", end="")
                elif val == 4:
                    # Król przeciwnika
                    print(f" {RED}{KING}{RESET} ", end="")

                if col < 7:
                    print("│", end="")

            print(f"║ {row}{clear_line}")

            if row < 7:
                print(f"{clear_line}╟───┼───┼───┼───┼───┼───┼───┼───╢")

        print(f"{clear_line}╚═══╧═══╧═══╧═══╧═══╧═══╧═══╧═══╝")
        print(f"{clear_line}  0   1   2   3   4   5   6   7")

        if pokaz_legende:
            print(f"{clear_line}\nLegenda:")
            print(f"{clear_line}  {BLUE}{PIECE}{RESET} Twój pion  {RED}{PIECE}{RESET} Pion przeciwnika  "
                  f"{BLUE}{KING}{RESET} Twój król  {RED}{KING}{RESET} Król przeciwnika")
            print(f"{clear_line}  {EMPTY_DARK} Puste pole  (spacja) Białe pole (niedostępne)")
        else:
            if not notebook:
                print(clear_line)
