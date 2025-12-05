import numpy as np
import importlib.util
import os
import time


class GRA:
    def __init__(self, bot1, bot2):
        self.plansza = np.array([
            [2, 2, 2, 2],
            [2, 2, 2, 2],
            [2, 2, 2, 2],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [1, 1, 1, 1],
            [1, 1, 1, 1],
            [1, 1, 1, 1]
        ])

        # Ładowanie botów
        if type(bot1) == str:
            self.bot1 = self._zaladuj_bota(bot1)
        else:
            self.bot1 = bot1

        if type(bot2) == str:
            self.bot2 = self._zaladuj_bota(bot2)
        else:
            self.bot2 = bot2

    def _zaladuj_bota(self, nazwa_bota):
        """
        Ładuje klasę bota z pliku w folderze boty.

        Args:
            nazwa_bota: nazwa pliku bota (bez .py)

        Returns:
            instancja klasy bot
        """
        # Ścieżka do pliku bota
        sciezka_bota = os.path.join(os.path.dirname(__file__), 'boty', f'{nazwa_bota}.py')

        # Dynamiczne załadowanie modułu
        spec = importlib.util.spec_from_file_location(nazwa_bota, sciezka_bota)
        modul = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modul)

        # Utworzenie instancji klasy bot
        return modul.bot()

    def znajdz_legalne_ruchy(self, plansza):
        """
        Znajduje legalne ruchy dla gracza.
        Najpierw sprawdza bicia - jeśli są dostępne, zwraca tylko bicia.
        Jeśli nie ma bić, zwraca zwykłe ruchy.

        Args:
            plansza: numpy array 4x8 reprezentujący ciemne pola

        Returns:
            lista krotek ((start_row, start_col), (end_row, end_col))
        """
        bicia = []
        legalne_ruchy = []
        rows, cols = plansza.shape

        # Najpierw sprawdź czy są dostępne bicia
        for row in range(rows):
            for col in range(cols):
                piece = plansza[row, col]

                # Sprawdź bicia dla pionków gracza
                if piece == 1:  # Zwykły pion gracza
                    bicia_piona = self._bicia_piona(plansza, row, col)
                    bicia.extend(bicia_piona)
                elif piece == 3:  # Król gracza
                    bicia_krola = self._bicia_krola(plansza, row, col)
                    bicia.extend(bicia_krola)

        # Jeśli są bicia, zwróć tylko bicia (bicie jest obowiązkowe)
        if len(bicia) > 0:
            return bicia

        # Jeśli nie ma bić, znajdź zwykłe ruchy
        for row in range(rows):
            for col in range(cols):
                piece = plansza[row, col]

                # Sprawdź zwykłe ruchy dla pionków gracza
                if piece == 1:  # Zwykły pion gracza
                    ruchy = self._ruchy_piona(plansza, row, col)
                    legalne_ruchy.extend(ruchy)
                elif piece == 3:  # Król gracza
                    ruchy = self._ruchy_krola(plansza, row, col)
                    legalne_ruchy.extend(ruchy)

        return legalne_ruchy

    def _bicia_piona(self, plansza, row, col):
        """Znajduje możliwe bicia dla zwykłego piona (bicie do przodu i do tyłu)."""
        bicia = []
        rows, cols = plansza.shape

        # Konwertuj pozycję z reprezentacji 4x8 na prawdziwą kolumnę 8x8
        real_col = col * 2 + (1 if row % 2 == 0 else 0)

        # Pion może bić zarówno do przodu jak i do tyłu
        # Sprawdź wszystkie 4 kierunki przekątne na prawdziwej szachownicy
        # Kierunki: (zmiana_wiersza, zmiana_kolumny_8x8)
        kierunki_8x8 = [
            (-1, -1),  # Góra-lewo
            (-1, 1),   # Góra-prawo
            (1, -1),   # Dół-lewo
            (1, 1)     # Dół-prawo
        ]

        for dr, dc_real in kierunki_8x8:
            # Oblicz pozycję sąsiada na prawdziwej szachownicy
            adj_row = row + dr
            adj_col_real = real_col + dc_real

            # Konwertuj z powrotem na reprezentację 4x8
            if adj_row % 2 == 0:  # Parzyste wiersze: ciemne na 1,3,5,7
                if adj_col_real % 2 == 1 and 0 <= adj_col_real < 8:
                    adj_col = adj_col_real // 2
                else:
                    continue  # To pole nie jest ciemne
            else:  # Nieparzyste wiersze: ciemne na 0,2,4,6
                if adj_col_real % 2 == 0 and 0 <= adj_col_real < 8:
                    adj_col = adj_col_real // 2
                else:
                    continue

            # Sprawdź czy sąsiadujące pole jest w granicach i zawiera pionek przeciwnika
            if self._czy_pole_w_granicach(adj_row, adj_col, rows, cols):
                adj_piece = plansza[adj_row, adj_col]

                # Przeciwnik to pion (2) lub król (4)
                if adj_piece in [2, 4]:
                    # Oblicz pole docelowe (dwa pola dalej w tym samym kierunku)
                    target_row = adj_row + dr
                    target_col_real = adj_col_real + dc_real

                    # Konwertuj na reprezentację 4x8
                    if target_row % 2 == 0:  # Parzyste wiersze
                        if target_col_real % 2 == 1 and 0 <= target_col_real < 8:
                            target_col = target_col_real // 2
                        else:
                            continue
                    else:  # Nieparzyste wiersze
                        if target_col_real % 2 == 0 and 0 <= target_col_real < 8:
                            target_col = target_col_real // 2
                        else:
                            continue

                    # Sprawdź czy pole docelowe jest w granicach i puste
                    if self._czy_pole_w_granicach(target_row, target_col, rows, cols):
                        if plansza[target_row, target_col] == 0:
                            bicia.append(((row, col), (target_row, target_col)))

        return bicia

    def _ruchy_piona(self, plansza, row, col):
        """Znajduje ruchy dla zwykłego piona (ruch tylko do przodu)."""
        ruchy = []
        rows, cols = plansza.shape

        # Pion gracza porusza się w górę (w kierunku row-1)
        # Na planszy szachownicy parzysty/nieparzysty wiersz ma inne sąsiedztwo

        if row % 2 == 0:  # Parzyste wiersze: ciemne pola na 1,3,5,7
            # Sąsiedzi w górę to col_idx i col_idx+1 w wierszu row-1
            kierunki = [(-1, 0), (-1, 1)]
        else:  # Nieparzyste wiersze: ciemne pola na 0,2,4,6
            # Sąsiedzi w górę to col_idx-1 i col_idx w wierszu row-1
            kierunki = [(-1, -1), (-1, 0)]

        for dr, dc in kierunki:
            new_row, new_col = row + dr, col + dc

            if self._czy_pole_w_granicach(new_row, new_col, rows, cols):
                if plansza[new_row, new_col] == 0:  # Pole puste
                    ruchy.append(((row, col), (new_row, new_col)))

        return ruchy

    def _bicia_krola(self, plansza, row, col):
        """Znajduje możliwe bicia dla króla (bicie we wszystkich kierunkach)."""
        bicia = []
        rows, cols = plansza.shape

        # Konwertuj pozycję z reprezentacji 4x8 na prawdziwą kolumnę 8x8
        real_col = col * 2 + (1 if row % 2 == 0 else 0)

        # Król może bić we wszystkich 4 kierunkach przekątnych
        # Kierunki: (zmiana_wiersza, zmiana_kolumny_8x8)
        kierunki_8x8 = [
            (-1, -1),  # Góra-lewo
            (-1, 1),   # Góra-prawo
            (1, -1),   # Dół-lewo
            (1, 1)     # Dół-prawo
        ]

        for dr, dc_real in kierunki_8x8:
            # Oblicz pozycję sąsiada na prawdziwej szachownicy
            adj_row = row + dr
            adj_col_real = real_col + dc_real

            # Konwertuj z powrotem na reprezentację 4x8
            if adj_row % 2 == 0:  # Parzyste wiersze: ciemne na 1,3,5,7
                if adj_col_real % 2 == 1 and 0 <= adj_col_real < 8:
                    adj_col = adj_col_real // 2
                else:
                    continue  # To pole nie jest ciemne
            else:  # Nieparzyste wiersze: ciemne na 0,2,4,6
                if adj_col_real % 2 == 0 and 0 <= adj_col_real < 8:
                    adj_col = adj_col_real // 2
                else:
                    continue

            # Sprawdź czy sąsiadujące pole jest w granicach i zawiera pionek przeciwnika
            if self._czy_pole_w_granicach(adj_row, adj_col, rows, cols):
                adj_piece = plansza[adj_row, adj_col]

                # Przeciwnik to pion (2) lub król (4)
                if adj_piece in [2, 4]:
                    # Oblicz pole docelowe (dwa pola dalej w tym samym kierunku)
                    target_row = adj_row + dr
                    target_col_real = adj_col_real + dc_real

                    # Konwertuj na reprezentację 4x8
                    if target_row % 2 == 0:  # Parzyste wiersze
                        if target_col_real % 2 == 1 and 0 <= target_col_real < 8:
                            target_col = target_col_real // 2
                        else:
                            continue
                    else:  # Nieparzyste wiersze
                        if target_col_real % 2 == 0 and 0 <= target_col_real < 8:
                            target_col = target_col_real // 2
                        else:
                            continue

                    # Sprawdź czy pole docelowe jest w granicach i puste
                    if self._czy_pole_w_granicach(target_row, target_col, rows, cols):
                        if plansza[target_row, target_col] == 0:
                            bicia.append(((row, col), (target_row, target_col)))

        return bicia

    def _ruchy_krola(self, plansza, row, col):
        """Znajduje ruchy dla króla (ruch do przodu i do tyłu)."""
        ruchy = []
        rows, cols = plansza.shape

        # Król może się poruszać we wszystkich kierunkach po przekątnej
        if row % 2 == 0:  # Parzyste wiersze: ciemne pola na 1,3,5,7
            # Sąsiedzi: góra (col, col+1), dół (col, col+1)
            kierunki = [(-1, 0), (-1, 1), (1, 0), (1, 1)]
        else:  # Nieparzyste wiersze: ciemne pola na 0,2,4,6
            # Sąsiedzi: góra (col-1, col), dół (col-1, col)
            kierunki = [(-1, -1), (-1, 0), (1, -1), (1, 0)]

        for dr, dc in kierunki:
            new_row, new_col = row + dr, col + dc

            if self._czy_pole_w_granicach(new_row, new_col, rows, cols):
                if plansza[new_row, new_col] == 0:  # Pole puste
                    ruchy.append(((row, col), (new_row, new_col)))

        return ruchy

    def _czy_pole_w_granicach(self, row, col, max_rows, max_cols):
        """Sprawdza czy pole jest w granicach planszy."""
        return 0 <= row < max_rows and 0 <= col < max_cols

    def zamien_perspektywe(self, plansza):
        """
        Zamienia perspektywę planszy - pionki gracza stają się pionkami przeciwnika i odwrotnie.
        Plansza jest również odwracana wertykalnie i horyzontalnie, żeby przeciwnik widział ją ze swojej strony.

        Args:
            plansza: numpy array 4x8 reprezentujący planszę

        Returns:
            numpy array z zamienioną perspektywą
        """
        # Mapowanie: 0->0, 1->2, 2->1, 3->4, 4->3
        lookup = np.array([0, 2, 1, 4, 3])

        # Zamiana pionków przez indeksowanie i odwrócenie planszy
        zamieniona_plansza = lookup[plansza][::-1, ::-1]

        return zamieniona_plansza

    def update(self, ruch):
        """
        Aktualizuje planszę na podstawie wykonanego ruchu.

        Args:
            ruch: krotka ((start_row, start_col), (end_row, end_col))
        """
        start, end = ruch
        start_row, start_col = start
        end_row, end_col = end

        # Pobierz pionek
        pionek = self.plansza[start_row, start_col]

        # Sprawdź czy to był ruch bicia
        # Bicie ma miejsce gdy ruch przemieszcza się o 2 wiersze
        row_diff = abs(end_row - start_row)

        if row_diff == 2:  # To jest bicie
            # Najprostszy sposób: przeszukaj wiersz pomiędzy startem a końcem
            # i znajdź pionka przeciwnika (2 lub 4)
            captured_row = (start_row + end_row) // 2

            # Przeszukaj wszystkie 4 kolumny w wierszu captured_row
            for captured_col in range(4):
                piece = self.plansza[captured_row, captured_col]
                if piece in [2, 4]:  # Pionek przeciwnika
                    # Usuń zbity pionek
                    self.plansza[captured_row, captured_col] = 0
                    break

        # Przenieś pionek na nowe pole
        self.plansza[end_row, end_col] = pionek

        # Wyczyść stare pole
        self.plansza[start_row, start_col] = 0

        # Sprawdź promocję do króla (gracz osiąga wiersz 0)
        if end_row == 0 and pionek == 1:
            self.plansza[end_row, end_col] = 3  # Promuj do króla

    def start(self, show=False, notebook=False, time = 1.0):
        """
        Rozpoczyna grę między dwoma botami.
        Gra toczy się w pętli, aż jeden z botów nie ma legalnych ruchów.

        Args:
            show: jeśli True, wyświetla planszę po każdej rundzie i czeka 2 sekundy
        """
        runda = 0
        pierwsza_runda = True

        # Wyświetl początkową planszę przed pierwszym ruchem
        if show:
            if not notebook:
                print(f"\033[KRunda: {runda}")
            else:
                print(f"Runda: {runda}")
                from IPython.display import clear_output, display, HTML
                display(HTML("<style>pre, code {font-family: 'Courier New', monospace !important;}</style>"))
            self.wyswietl_plansze(self.plansza, pokaz_legende=True)
            time.sleep(time*2)
            pierwsza_runda = False

        while True:
            # Sprawdź legalne ruchy dla aktualnego gracza
            legalne_ruchy = self.znajdz_legalne_ruchy(self.plansza)

            # Jeśli brak legalnych ruchów - koniec gry
            if len(legalne_ruchy) == 0:
                poprzedni_gracz = 2 if runda % 2 == 0 else 1

                # Jeśli show=True, wyświetl gratulacje
                if show:
                    if notebook:
                        clear_output(wait=True)
                    else:
                        print("\033[21A", end="")  # Przenieś kursor do góry

                    # Zamień perspektywę z powrotem do widoku gracza 1
                    # Jeśli runda jest nieparzysta, plansza jest z perspektywy bot2, trzeba zamienić
                    # Jeśli runda jest parzysta, plansza jest z perspektywy bot1, NIE zamieniaj
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
                        self.wyswietl_plansze(plansza_do_wyswietlenia, pokaz_legende=False)
                        print(f"\033[K\n🎉 Gratulacje! Wygrywa Bot {poprzedni_gracz}! 🎉\n")

                return poprzedni_gracz  # Zwróć numer wygrywającego bota

            # Wybierz bota na podstawie parzystości rundy
            aktualny_bot = self.bot1 if runda % 2 == 0 else self.bot2

            # Pobierz ruch od bota
            wybrany_ruch = aktualny_bot.move(self.plansza, legalne_ruchy)

            # Zaktualizuj planszę
            self.update(wybrany_ruch)

            # Zamień perspektywę planszy dla następnego gracza
            self.plansza = self.zamien_perspektywe(self.plansza)

            runda += 1

            # Wyświetl planszę jeśli show=True
            if show:
                if notebook:
                    # W notebooku użyj clear_output
                    clear_output(wait=True)
                else:
                    # W terminalu użyj ANSI kodów
                    if not pierwsza_runda:
                        # Przenieś kursor 21 linii w górę (1 Runda + 20 linii planszy)
                        print("\033[21A", end="")

                # Zamień perspektywę z powrotem do widoku gracza 1
                # Po rundzie nieparzystej (bot1), plansza jest z perspektywy bot2, więc trzeba zamienić
                # Po rundzie parzystej (bot2), plansza jest z perspektywy bot1, więc NIE zamieniaj
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
                    # Nie pokazuj legendy po pierwszej rundzie
                    self.wyswietl_plansze(plansza_do_wyswietlenia, pokaz_legende=pierwsza_runda)

                if pierwsza_runda:
                    pierwsza_runda = False

                # Czekaj
                time.sleep(time)

    def wyswietl_plansze(self, plansza=None, pokaz_legende=True, notebook=False):
        """Wyświetla pełną planszę 8x8 z białymi polami i ładnymi symbolami."""
        if plansza is None:
            plansza = self.plansza

        # Kolory ANSI
        RESET = '\033[0m'
        RED = '\033[91m'      # Gracz (1)
        BLUE = '\033[94m'     # Przeciwnik (2)
        GRAY = '\033[90m'     # Białe pola

        # Symbole
        EMPTY_DARK = '·'
        EMPTY_LIGHT = ' '
        PIECE = '●'
        KING = '▣'

        # Mapowanie wartości na symbole i kolory
        symbole = {
            0: (EMPTY_DARK, ''),           # Puste ciemne pole
            1: (PIECE, BLUE),                # Pion gracza
            2: (PIECE, RED),               # Pion przeciwnika
            3: (KING, BLUE),              # Król gracza
            4: (KING, RED)                 # Król przeciwnika
        }

        # Tworzenie pełnej planszy 8x8
        pelna_plansza = [[None for _ in range(8)] for _ in range(8)]

        # Wypełnianie ciemnych pól
        for row in range(8):
            for col_idx in range(4):
                # Ciemne pola są na różnych pozycjach w zależności od parzystości wiersza
                if row % 2 == 0:
                    # Parzyste wiersze: ciemne pola na kolumnach 1, 3, 5, 7
                    col = col_idx * 2 + 1
                else:
                    # Nieparzyste wiersze: ciemne pola na kolumnach 0, 2, 4, 6
                    col = col_idx * 2

                pelna_plansza[row][col] = plansza[row][col_idx]

        # Wyświetlanie
        clear_line = "" if notebook else "\033[K"

        print(f"\n{clear_line}╔═══╤═══╤═══╤═══╤═══╤═══╤═══╤═══╗")

        for row in range(8):
            print(f"{clear_line}║", end="")
            for col in range(8):
                if pelna_plansza[row][col] is not None:
                    # Ciemne pole z figurą lub puste
                    val = pelna_plansza[row][col]
                    symbol, color = symbole[val]
                    print(f" {color}{symbol}{RESET} ", end="")
                else:
                    # Białe pole
                    print(f" {GRAY}{EMPTY_LIGHT}{RESET} ", end="")

                if col < 7:
                    print("│", end="")

            print("║", end="")
            print(f" {row}{clear_line}")  # Numeracja wierszy + wyczyść resztę linii

            if row < 7:
                print(f"{clear_line}╟───┼───┼───┼───┼───┼───┼───┼───╢")

        print(f"{clear_line}╚═══╧═══╧═══╧═══╧═══╧═══╧═══╧═══╝")
        print(f"{clear_line}  0   1   2   3   4   5   6   7")  # Numeracja kolumn

        # Legenda (opcjonalna)
        if pokaz_legende:
            print(f"{clear_line}\nLegenda: {BLUE}{PIECE}{RESET} Twój pion  {RED}{PIECE}{RESET} Przeciwnik  "
                f"{BLUE}{KING}{RESET} Twój król  {RED}{KING}{RESET} Król przeciwnika")
        else:
            # Wydrukuj pustą linię zamiast legendy (żeby zachować tę samą liczbę linii)
            if not notebook:
                print(clear_line)

