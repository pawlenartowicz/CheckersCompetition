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
        Tylko zwykłe ruchy, na razie bez bicia i promocji.
        
        Args:
            plansza: numpy array 4x8 reprezentujący ciemne pola
            
        Returns:
            lista krotek ((start_row, start_col), (end_row, end_col))
        """
        legalne_ruchy = []
        rows, cols = plansza.shape
        
        for row in range(rows):
            for col in range(cols):
                piece = plansza[row, col]
                
                # Sprawdź pionki gracza
                if piece == 1:  # Zwykły pion gracza
                    ruchy = self._ruchy_zwyklego_piona(plansza, row, col)
                    legalne_ruchy.extend(ruchy)
                elif piece == 3:  # Król gracza
                    ruchy = self._ruchy_krola(plansza, row, col)
                    legalne_ruchy.extend(ruchy)
        
        return legalne_ruchy

    def _ruchy_zwyklego_piona(self, plansza, row, col):
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

        # Przenieś pionek na nowe pole
        self.plansza[end_row, end_col] = pionek

        # Wyczyść stare pole
        self.plansza[start_row, start_col] = 0

        # Sprawdź promocję do króla (gracz osiąga wiersz 0)
        if end_row == 0 and pionek == 1:
            self.plansza[end_row, end_col] = 3  # Promuj do króla

        # TODO: Obsługa bicia (usuwanie zbitych pionków)

    def start(self, show=False, notebook=False):
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
                from IPython.display import clear_output
            self.wyswietl_plansze(self.plansza, pokaz_legende=True)
            time.sleep(2)
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
                    self.wyswietl_plansze(plansza_do_wyswietlenia, pokaz_legende=pierwsza_runda, notebook=True)
                else:
                    print(f"\033[KRunda: {runda}")
                    # Nie pokazuj legendy po pierwszej rundzie
                    self.wyswietl_plansze(plansza_do_wyswietlenia, pokaz_legende=pierwsza_runda)

                if pierwsza_runda:
                    pierwsza_runda = False

                # Czekaj 1 sekundę
                time.sleep(1)

    def wyswietl_plansze(self, plansza=None, pokaz_legende=True, notebook=False):
        """Wyświetla pełną planszę 8x8 z białymi polami i ładnymi symbolami."""
        if plansza is None:
            plansza = self.plansza

        # Symbole
        EMPTY_DARK = '·'
        EMPTY_LIGHT = ' '
        PIECE = '●'
        KING = '▣'

        # Mapowanie wartości na symbole
        symbole_text = {
            0: EMPTY_DARK,
            1: PIECE,
            2: PIECE,
            3: KING,
            4: KING
        }

        # Tworzenie pełnej planszy 8x8
        pelna_plansza = [[None for _ in range(8)] for _ in range(8)]

        # Wypełnianie ciemnych pól
        for row in range(8):
            for col_idx in range(4):
                if row % 2 == 0:
                    col = col_idx * 2 + 1
                else:
                    col = col_idx * 2
                pelna_plansza[row][col] = plansza[row][col_idx]

        if notebook:
            # Wyświetlanie HTML dla Google Colab
            from IPython.display import display, HTML
            
            kolory = {
                0: '#666',      # Puste ciemne pole
                1: '#4A90E2',   # Pion gracza (niebieski)
                2: '#E74C3C',   # Pion przeciwnika (czerwony)
                3: '#4A90E2',   # Król gracza
                4: '#E74C3C'    # Król przeciwnika
            }

            html = '<div style="font-family: \'Courier New\', Courier, monospace; font-size: 16px; line-height: 1.2; white-space: pre;">\n'
            html += '\n╔═══╤═══╤═══╤═══╤═══╤═══╤═══╤═══╗\n'

            for row in range(8):
                html += '║'
                for col in range(8):
                    if pelna_plansza[row][col] is not None:
                        val = pelna_plansza[row][col]
                        symbol = symbole_text[val]
                        color = kolory[val]
                        html += f' <span style="color: {color};">{symbol}</span> '
                    else:
                        html += f' <span style="color: #999;">{EMPTY_LIGHT}</span> '

                    if col < 7:
                        html += '│'

                html += f'║ {row}\n'

                if row < 7:
                    html += '╟───┼───┼───┼───┼───┼───┼───┼───╢\n'

            html += '╚═══╧═══╧═══╧═══╧═══╧═══╧═══╧═══╝\n'
            html += '  0   1   2   3   4   5   6   7\n'

            if pokaz_legende:
                html += '\nLegenda: '
                html += f'<span style="color: #4A90E2;">{PIECE}</span> Twój pion  '
                html += f'<span style="color: #E74C3C;">{PIECE}</span> Przeciwnik  '
                html += f'<span style="color: #4A90E2;">{KING}</span> Twój król  '
                html += f'<span style="color: #E74C3C;">{KING}</span> Król przeciwnika\n'

            html += '</div>'
            display(HTML(html))

        else:
            # Wyświetlanie ANSI dla terminala
            RESET = '\033[0m'
            RED = '\033[91m'
            BLUE = '\033[94m'
            GRAY = '\033[90m'

            symbole_ansi = {
                0: (EMPTY_DARK, ''),
                1: (PIECE, BLUE),
                2: (PIECE, RED),
                3: (KING, BLUE),
                4: (KING, RED)
            }

            clear_line = "\033[K"
            print(f"\n{clear_line}╔═══╤═══╤═══╤═══╤═══╤═══╤═══╤═══╗")

            for row in range(8):
                print(f"{clear_line}║", end="")
                for col in range(8):
                    if pelna_plansza[row][col] is not None:
                        val = pelna_plansza[row][col]
                        symbol, color = symbole_ansi[val]
                        print(f" {color}{symbol}{RESET} ", end="")
                    else:
                        print(f" {GRAY}{EMPTY_LIGHT}{RESET} ", end="")

                    if col < 7:
                        print("│", end="")

                print("║", end="")
                print(f" {row}{clear_line}")

                if row < 7:
                    print(f"{clear_line}╟───┼───┼───┼───┼───┼───┼───┼───╢")

            print(f"{clear_line}╚═══╧═══╧═══╧═══╧═══╧═══╧═══╧═══╝")
            print(f"{clear_line}  0   1   2   3   4   5   6   7")

            if pokaz_legende:
                print(f"{clear_line}\nLegenda: {BLUE}{PIECE}{RESET} Twój pion  {RED}{PIECE}{RESET} Przeciwnik  "
                    f"{BLUE}{KING}{RESET} Twój król  {RED}{KING}{RESET} Król przeciwnika")
            else:
                print(clear_line)