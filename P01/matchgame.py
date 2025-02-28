import random

def anzeigen(stapel):
    """Zeigt den aktuellen Streichholzstapel an"""
    print("\n" + "\n".join(["========O"] * stapel))
    print(f"| Noch {stapel} Streichhölzer. |\n")

def spieler_zug(stapel):
    """Lässt den Spieler eine gültige Anzahl nehmen"""
    while True:
        try:
            zug = int(input("Wie viele nimmst du? (1-3): "))
            if 1 <= zug <= 3 and zug < stapel:
                return zug
            print("Ungültig! Wähle 1, 2 oder 3, aber nicht das letzte.")
        except ValueError:
            print("Gib eine Zahl (1-3) ein.")

def computer_zug(stapel):
    """Computerspielzug basierend auf optimaler Strategie"""
    if stapel in [2, 3]:
        return stapel - 1  
    return stapel % 4 or random.choice([1, 2, 3])

def spiel():
    """Startet das Spiel"""
    stapel = random.randint(10, 20)
    spieler_dran = random.choice([True, False])

    print("\nWillkommen! Wer das letzte Streichholz nimmt, verliert!\n")

    while stapel > 1:
        anzeigen(stapel)
        zug = spieler_zug(stapel) if spieler_dran else computer_zug(stapel)
        print(f"{'Du' if spieler_dran else 'Computer'} nimmst {zug}.")
        stapel -= zug
        spieler_dran = not spieler_dran

    anzeigen(stapel)
    print("Du verlierst!" if spieler_dran else "Computer verliert! Du gewinnst!")

spiel()
