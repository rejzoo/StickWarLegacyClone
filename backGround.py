import arcade
import random

RYCHLOST_POHYBU_MESIACA = 14
ROZOSTUPY_OBLAKOV_X = 250

class BackGround:
    def __init__(self):
        self.pozadieNebo = arcade.load_texture("Prostredie/Pozadie/pozadie_nebo.png")
        self.pozadieZem1 = arcade.load_texture("Prostredie/Pozadie/pozadieTrava.png")
        self.pozadieZem2 = arcade.load_texture("Prostredie/Pozadie/pozadie_trava2.png")
        self.mesiac = arcade.load_texture("Prostredie/Pozadie/mesiac.png")

        self.travaPriHracovejSoche = arcade.load_texture("Prostredie/Pozadie/travaPodVezou.png")
        self.travaPriEnemySoche = arcade.load_texture("Prostredie/Pozadie/travaPodVezou.png")
        self.poziciaXMesiaca = 600
        self.poslednaHodnotaPozicieKamery = -1

        self.zoznamTexturOblakov = []
        self.zoznamTexturOblakov.append(arcade.load_texture("Prostredie/Oblaky/oblak1.png"))
        self.zoznamTexturOblakov.append(arcade.load_texture("Prostredie/Oblaky/oblak2.png"))
        self.zoznamTexturOblakov.append(arcade.load_texture("Prostredie/Oblaky/oblak3.png"))
        self.zoznamOblakov = []

        self.seedPreRandom = random.randint(0, 50000)

    def vykresli(self):
        zaciatok = -150
        arcade.draw_lrwh_rectangle_textured(-150, 300, 7000, 600, self.pozadieNebo)
        arcade.draw_lrwh_rectangle_textured(self.poziciaXMesiaca, 550, 177, 184, self.mesiac)

        arcade.draw_lrwh_rectangle_textured(zaciatok, 280, self.pozadieZem2.width, self.pozadieZem2.height,
                                            self.pozadieZem2)
        arcade.draw_lrwh_rectangle_textured(zaciatok + 880 + self.pozadieZem2.width, 285, self.pozadieZem2.width,
                                            self.pozadieZem2.height,self.pozadieZem2)
        arcade.draw_lrwh_rectangle_textured(zaciatok + self.pozadieZem2.width * 2, 295, self.pozadieZem2.width,
                                            self.pozadieZem2.height,self.pozadieZem2)

        arcade.draw_lrwh_rectangle_textured(zaciatok, 0, self.pozadieZem1.width, self.pozadieZem1.height,
                                            self.pozadieZem1)
        arcade.draw_lrwh_rectangle_textured(zaciatok + self.pozadieZem1.width, 10, self.pozadieZem1.width,
                                            self.pozadieZem1.height, self.pozadieZem1)
        arcade.draw_lrwh_rectangle_textured(zaciatok + self.pozadieZem1.width * 2, 20, self.pozadieZem1.width,
                                            self.pozadieZem1.height, self.pozadieZem1)
        arcade.draw_lrwh_rectangle_textured(zaciatok + self.pozadieZem1.width * 3, 30, self.pozadieZem1.width,
                                            self.pozadieZem1.height, self.pozadieZem1)

        self.vytvorOblakyAVykresli()

    def vykresliTravuPriSochach(self):
        arcade.draw_lrwh_rectangle_textured(190, 280, self.travaPriHracovejSoche.width,
                                            self.travaPriHracovejSoche.height, self.travaPriHracovejSoche)
        arcade.draw_lrwh_rectangle_textured(5870, 290, self.travaPriEnemySoche.width,
                                            self.travaPriEnemySoche.height, self.travaPriEnemySoche)

    def updatePolohyMesiaca(self, scrollValue):
        if self.poslednaHodnotaPozicieKamery != scrollValue and scrollValue > self.poslednaHodnotaPozicieKamery:
            self.poziciaXMesiaca += RYCHLOST_POHYBU_MESIACA
            self.poslednaHodnotaPozicieKamery = scrollValue
        elif self.poslednaHodnotaPozicieKamery != scrollValue and scrollValue < self.poslednaHodnotaPozicieKamery:
            self.poziciaXMesiaca -= RYCHLOST_POHYBU_MESIACA
            self.poslednaHodnotaPozicieKamery = scrollValue

        if scrollValue == -10:
            self.poziciaXMesiaca = 474
        elif scrollValue == 335:
            self.poziciaXMesiaca = 5304

    def vytvorOblakyAVykresli(self):
        random.seed(self.seedPreRandom)

        for j in range(0, 7):
            for i in range(0, 3):
                randomTextura = self.zoznamTexturOblakov[random.randint(0, 2)]
                suradnicaX = (i * ROZOSTUPY_OBLAKOV_X) + (j * 950)
                self.zoznamOblakov.append(arcade.draw_lrwh_rectangle_textured(suradnicaX, random.randint(450, 700),
                                                                              randomTextura.width, randomTextura.height,
                                                                              randomTextura))