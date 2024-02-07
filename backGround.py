import arcade


class BackGround(arcade.Window):
    def __init__(self, sirka, vyska):
        super().__init__()
        self.pozadia = arcade.SpriteList()
        self.camera = arcade.Camera(sirka, vyska)
