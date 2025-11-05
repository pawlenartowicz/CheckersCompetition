import random

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
        wybrany_ruch = random.choice(ruchy)

        return wybrany_ruch
