import arcade
import arcade.gui
from gameHandler import HraView

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

    def on_draw(self):
        self.clear()
        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            self.pozadie.width, self.pozadie.height,
                                            self.pozadie)
        self.manager.draw()


VYSKA_PAUSE_MENU = 500
SIRKA_PAUSE_MENU = 500

class PauseMenu(arcade.View):
    def __init__(self, aktualnaHra):
        super().__init__()

        self.manager = arcade.gui.UIManager()
        self.aktualnaHra = aktualnaHra

        unpauseButton = arcade.gui.UIFlatButton(width=200, text="Resume")

        @unpauseButton.event("on_click")
        def on_click_startGame(event):
            hra = HraView()
            self.window.show_view(self.aktualnaHra)

        rozlozenie = arcade.gui.UIBoxLayout(vertical=True, space_between=10)
        rozlozenie.add(unpauseButton)
        self.manager.add(arcade.gui.UIAnchorWidget(anchor_x="center", anchor_y="center", child=rozlozenie))

    def on_hide_view(self):
        self.manager.disable()

    def on_show_view(self):
        self.manager.enable()
        self.window.background_color = arcade.color.RED
        self.window.set_size(SIRKA_PAUSE_MENU, VYSKA_PAUSE_MENU)
        self.window.center_window()

    def on_draw(self):
        self.clear()
        self.manager.draw()