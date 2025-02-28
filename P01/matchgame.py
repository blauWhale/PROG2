import random

def anzeigen(stapel):
    """Zeigt den aktuellen Streichholzstapel an"""
    for i in range(stapel):
        print("========O")
    if stapel == 1:
        print("| Noch", stapel, "Streichholz. |")
    else:
        print("| Noch", stapel, "Streichhölzer. |")
    print("\n")
    
def spieler_zug(stapel):
    """Lässt den Spieler eine gültige Anzahl nehmen"""
    while True:
        try:
            zug = int(input("Wie viele nimmst du? (1-3): "))
            if zug >= 1 and zug <= 3:
                if zug < stapel:
                    return zug
            print("Ungültig! Wähle 1, 2 oder 3, aber nicht das letzte.")
        except ValueError:
            print("Gib eine Zahl (1-3) ein.")

def computer_zug(stapel):
    """Computerspielzug basierend auf optimaler Strategie"""
    if stapel == 2 or stapel == 3:
        return stapel - 1
    else:
        if stapel % 4 == 0:
            return random.choice([1, 2, 3])
        else:
            return stapel % 4

def spiel():
    """Startet das Spiel"""
    stapel = random.randint(10, 20)
    spieler_dran = random.choice([True, False])

    print("\nWillkommen! Wer das letzte Streichholz nimmt, verliert!\n")

    while stapel > 1:
        anzeigen(stapel)
        if spieler_dran:
            zug = spieler_zug(stapel)
        else:
            zug = computer_zug(stapel)

        if spieler_dran:
            print("Du nimmst", zug)
        else:
            print("Computer nimmt", zug)

        stapel = stapel - zug
        if spieler_dran:
            spieler_dran = False
        else:
            spieler_dran = True

    anzeigen(stapel)

    if spieler_dran:
        print("Du verlierst!")
    else:
        print("Computer verliert! Du gewinnst!")

spiel()

