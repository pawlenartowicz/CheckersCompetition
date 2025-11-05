from silnik import GRA

#===============================================
# Wasz bot powinien być zaimplementowany w tej klasie
# W przyszłości, powinien to być osobny plik z botem
#===============================================

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

twoj_bot = bot()
#===============================================
# Inicjalizacja botów
# Tutaj można zmienić boty na inne
# Boty z nazwą jako string są ładowane z plików w folderze 'boty'
#===============================================
bot1 = twoj_bot
bot2 = "random_bot"

# Test
if __name__ == "__main__":

    gra = GRA(bot1, bot2)
    gra.start(show=True)
