import arcade

class HealthBar:
    def __init__(self, x, y, max_hp, width=40, height=6):
        self.healthBarOffsetY = 90
        self.healthBarOffsetX = 70
        self.suradnicaX = x
        self.suradnicaY = y + self.healthBarOffsetY
        self.width = width
        self.height = height
        self.hp = max_hp
        self.maxHp = max_hp

    def updateHpBar(self, surX, surY, zivoty):
        self.suradnicaX = surX
        self.suradnicaY = surY
        self.hp = zivoty

    def vykresli(self):
        if self.hp == self.maxHp:
            return

        ratio = self.hp / self.maxHp
        arcade.draw_rectangle_filled(self.suradnicaX + self.healthBarOffsetX, self.suradnicaY + self.healthBarOffsetY,
                                     self.width, self.height, arcade.color.BLACK)
        arcade.draw_rectangle_filled(self.suradnicaX + self.healthBarOffsetX, self.suradnicaY + self.healthBarOffsetY,
                                     (self.width - 5), self.height - 10, arcade.color.RED)
        arcade.draw_rectangle_filled(self.suradnicaX + self.healthBarOffsetX, self.suradnicaY + self.healthBarOffsetY,
                                     (self.width - 5) * ratio, self.height - 10, arcade.color.GREEN)