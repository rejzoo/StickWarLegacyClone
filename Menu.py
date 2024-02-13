import time

import arcade
import arcade.gui
from gameHandler import HraView

SIRKA_OBRAZOVKY_MENU = 1000
VYSKA_OBRAZOVKY_MENU = 460

class StartMenu(arcade.View):
    def __init__(self):
        super().__init__()

        self.manager = arcade.gui.UIManager()
        self.pozadie = arcade.load_texture("TexturaMenus/menuBackground1.png")
        texturaButtonStart = arcade.load_texture("TexturaButton/play.png")
        texturaButtonQuit = arcade.load_texture("TexturaButton/quit.png")

        startGame = arcade.gui.UITextureButton(width=texturaButtonStart.width, height=texturaButtonStart.height, texture=texturaButtonStart)
        quitGame = arcade.gui.UITextureButton(width=texturaButtonStart.width, height=texturaButtonStart.height, texture=texturaButtonQuit)

        @startGame.event("on_click")
        def on_click_startGame(event):
            hra = HraView()
            hra.setup()
            self.window.show_view(hra)

        @quitGame.event("on_click")
        def on_click_quitGame(event):
            arcade.close_window()

        rozlozenie = arcade.gui.UIBoxLayout(vertical=True, space_between=10)
        rozlozenie.add(startGame)
        rozlozenie.add(quitGame)
        self.manager.add(arcade.gui.UIAnchorWidget(align_x=250, align_y=-50, child=rozlozenie))

    def on_hide_view(self):
        self.manager.disable()

    def on_show_view(self):
        self.manager.enable()
        self.window.set_size(SIRKA_OBRAZOVKY_MENU, VYSKA_OBRAZOVKY_MENU)
        self.window.center_window()

    def on_draw(self):
        self.clear()
        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            self.pozadie.width, self.pozadie.height,
                                            self.pozadie)
        self.manager.draw()


SIRKA_PAUSE_MENU = 1600
VYSKA_PAUSE_MENU = 800

class PauseMenu(arcade.View):
    def __init__(self, aktualnaHra):
        super().__init__()

        self.manager = arcade.gui.UIManager()
        self.aktualnaHra = aktualnaHra
        self.texturaTlacidlo = arcade.load_texture("TexturaMenus/menuTlacidlo.png")
        self.texturaTlacidloStlacene = arcade.load_texture("TexturaMenus/menuTlacidloStlacene.png")

        unpauseButton = arcade.gui.UITextureButton(width=200, text="Resume", texture=self.texturaTlacidlo)
        unpauseButton.texture_hovered = self.texturaTlacidloStlacene
        menuButton = arcade.gui.UITextureButton(width=200, text="Main Menu", texture=self.texturaTlacidlo)
        menuButton.texture_hovered = self.texturaTlacidloStlacene
        quitButton = arcade.gui.UITextureButton(width=200, text="Quit Game", texture=self.texturaTlacidlo)
        quitButton.texture_hovered = self.texturaTlacidloStlacene

        @unpauseButton.event("on_click")
        def on_click_startGame(event):
            self.window.show_view(self.aktualnaHra)

        @menuButton.event("on_click")
        def on_click_startGame(event):
            mainMenu = StartMenu()
            self.window.show_view(mainMenu)

        @quitButton.event("on_click")
        def on_click_startGame(event):
            arcade.close_window()

        rozlozenie = arcade.gui.UIBoxLayout(vertical=True, space_between=30)
        rozlozenie.add(unpauseButton)
        rozlozenie.add(menuButton)
        rozlozenie.add(quitButton)
        self.manager.add(arcade.gui.UIAnchorWidget(anchor_x="center", anchor_y="center", child=rozlozenie))

    def on_hide_view(self):
        self.manager.disable()

    def on_show_view(self):
        self.manager.enable()
        self.window.set_size(SIRKA_PAUSE_MENU, VYSKA_PAUSE_MENU)
        arcade.set_viewport(0, SIRKA_PAUSE_MENU, 0, VYSKA_PAUSE_MENU)
        self.window.center_window()

    def on_draw(self):
        self.clear()
        self.aktualnaHra.on_draw()
        arcade.draw_text("Game is Paused", SIRKA_PAUSE_MENU / 2 - 175, 550, arcade.color.YELLOW, font_size=40, bold=True, font_name="Calibri")
        self.manager.draw()


SIRKA_END_VIEW = 700
VYSKA_END_VIEW = 700

class EndScreen(arcade.View):
    def __init__(self, vitazHry, casZapnutiaHry):
        super().__init__()

        self.text = "You won!" if vitazHry == "Hrac" else "You lost!"
        self.casHry = round(time.time() - casZapnutiaHry, 2)

        self.manager = arcade.gui.UIManager()
        self.texturaTlacidlo = arcade.load_texture("TexturaMenus/menuTlacidlo.png")
        self.texturaTlacidloStlacene = arcade.load_texture("TexturaMenus/menuTlacidloStlacene.png")

        menuButton = arcade.gui.UITextureButton(width=200, text="Main Menu", texture=self.texturaTlacidlo)
        menuButton.texture_hovered = self.texturaTlacidloStlacene
        quitButton = arcade.gui.UITextureButton(width=200, text="Quit Game", texture=self.texturaTlacidlo)
        quitButton.texture_hovered = self.texturaTlacidloStlacene

        @menuButton.event("on_click")
        def on_click_startGame(event):
            mainMenu = StartMenu()
            self.window.show_view(mainMenu)

        @quitButton.event("on_click")
        def on_click_startGame(event):
            arcade.close_window()

        rozlozenie = arcade.gui.UIBoxLayout(vertical=True, space_between=30)
        rozlozenie.add(menuButton)
        rozlozenie.add(quitButton)
        self.manager.add(arcade.gui.UIAnchorWidget(anchor_x="center", anchor_y="center", child=rozlozenie))

    def on_hide_view(self):
        self.manager.disable()

    def on_show_view(self):
        self.manager.enable()
        self.window.set_size(SIRKA_END_VIEW, VYSKA_END_VIEW)
        arcade.set_viewport(0, SIRKA_END_VIEW, 0, VYSKA_END_VIEW)
        self.window.center_window()

    def on_draw(self):
        self.clear()
        self.window.background_color = arcade.color.AERO_BLUE
        arcade.draw_text(self.text, SIRKA_END_VIEW / 2 - 110, 550, arcade.color.BLACK, font_size=40, bold=True, font_name="Calibri")
        arcade.draw_text(f"Time played: {self.casHry}s", SIRKA_END_VIEW / 2 - 190, 500, arcade.color.BLACK,
                         font_size=40, bold=True, font_name="Calibri")
        self.manager.draw()