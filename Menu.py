import arcade
import arcade.gui

class StartMenu(arcade.View):
    def __init__(self, test):
        super().__init__()

        self.manager = arcade.gui.UIManager()
        self.rozhodnutie = test
        self.zapnutHru = False
        self.vypnutHru = False
        self.pozadie = arcade.load_texture("TexturaMenus/menuBackground1.png")
        texturaButtonStart = arcade.load_texture("TexturaButton/play.png")
        texturaButtonQuit = arcade.load_texture("TexturaButton/quit.png")

        startGame = arcade.gui.UITextureButton(width=texturaButtonStart.width, height=texturaButtonStart.height, texture=texturaButtonStart)
        quitGame = arcade.gui.UITextureButton(width=texturaButtonStart.width, height=texturaButtonStart.height, texture=texturaButtonQuit)

        @startGame.event("on_click")
        def on_click_startGame(event):
            self.zapnutHru = True

        @quitGame.event("on_click")
        def on_click_quitGame(event):
            self.vypnutHru = True

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

    def update(self, delta_time):
        if self.zapnutHru:
            self.rozhodnutie.nastavZapnutie(True)
            arcade.close_window()
        elif self.vypnutHru:
            self.rozhodnutie.nastavZapnutie(False)
            arcade.close_window()