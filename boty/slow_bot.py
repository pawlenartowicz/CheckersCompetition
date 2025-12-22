"""
Bot testowy który celowo jest wolny, aby przetestować system time benchmark.
"""
import time

class bot():
    def __init__(self):
        self.move_count = 0

    def move(self, plansza, ruchy):
        '''
        Bot który celowo czeka różną ilość czasu na różnych ruchach.

        Ruch 0: normalny (szybki)
        Ruch 1: przekracza benchmark ale nie 2x (test time_flags)
        Ruch 2: przekracza benchmark ale nie 2x (test time_flags)
        Ruch 3: przekracza benchmark ale nie 2x (test time_flags)
        Ruch 4: przekracza benchmark ale nie 2x (powinien użyć losowego - brak flags)
        Ruch 5+: przekracza 2x benchmark (timeout - losowy ruch)
        '''
        self.move_count += 1

        if self.move_count == 1:
            # Normalny szybki ruch
            time.sleep(0.001)
        elif self.move_count in [2, 3, 4]:
            # Przekracza benchmark (~0.33s) ale nie 2x
            # Czeka 0.4s (więcej niż benchmark, mniej niż 2x)
            time.sleep(0.4)
        elif self.move_count == 5:
            # Przekracza benchmark ale bot już nie ma flags
            time.sleep(0.4)
        else:
            # Przekracza 2x benchmark - timeout
            time.sleep(1.5)

        return ruchy[0]
