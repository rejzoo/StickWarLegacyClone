import arcade
import Menu

NAZOV_OBRAZOVKY = "Stick War Legacy Clone"
SIRKA_OBRAZOVKY_MENU = 1000
VYSKA_OBRAZOVKY_MENU = 500

def main():
    okno = arcade.Window(SIRKA_OBRAZOVKY_MENU, VYSKA_OBRAZOVKY_MENU, NAZOV_OBRAZOVKY)
    okno.center_window()
    okno.show_view(Menu.StartMenu())
    arcade.run()


if __name__ == "__main__":
    main()