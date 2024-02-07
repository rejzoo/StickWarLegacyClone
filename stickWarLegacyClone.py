from gameHandler import Hra


SIRKA_OBRAZOVKY = 1600
VYSKA_OBRAZOVKY = 800
NAZOV_OBRAZOVKY = "Stick War Legacy Clone"


def main():
    hra = Hra(SIRKA_OBRAZOVKY, VYSKA_OBRAZOVKY, NAZOV_OBRAZOVKY)
    hra.setup()
    hra.run()


if __name__ == "__main__":
    main()


"""
Nastudovat callback funkciu - vyuzivane pri tlacitku - spawne jednotky

Do atributu ulozim metodu, ktoru potom zavolam ?

Dorobit aby tazili na oboch miestach zlata a mali by byt dorobeni kopaci
"""