import arcade
import Menu

NAZOV_OBRAZOVKY = "Stick War Legacy Clone"

def main():
    okno = arcade.Window(10, 500, title="Stick Wars Legacy Clone")
    okno.center_window()
    okno.show_view(Menu.StartMenu())
    arcade.run()


if __name__ == "__main__":
    main()