import arcade
import Menu
from gameHandler import Hra


SIRKA_OBRAZOVKY_HRY = 1600
VYSKA_OBRAZOVKY_HRY = 800
NAZOV_OBRAZOVKY = "Stick War Legacy Clone"
SIRKA_OBRAZOVKY_MENU = 1000
VYSKA_OBRAZOVKY_MENU = 500

class Test:
    def __init__(self):
        self.zapnutieHry = False

    def nastavZapnutie(self, stav):
        self.zapnutieHry = stav

def main():
    test = Test()
    okno = arcade.Window(SIRKA_OBRAZOVKY_MENU, VYSKA_OBRAZOVKY_MENU, NAZOV_OBRAZOVKY)
    okno_menu = Menu.StartMenu(test)
    okno.show_view(okno_menu)
    arcade.run()
    if test.zapnutieHry:
        hra = Hra(SIRKA_OBRAZOVKY_HRY, VYSKA_OBRAZOVKY_HRY, NAZOV_OBRAZOVKY)
        hra.setup()
        hra.run()


if __name__ == "__main__":
    main()