import arcade

class Veza(arcade.Sprite):
    def __init__(self, x, y, nepriatel=False):
        super().__init__()
        self.suradnicaX = x
        self.suradnicaY = y
        self.zivotVeze = 2500
        if nepriatel:
            self.sprite = arcade.Sprite("Prostredie/VezaNepriatel2.png", 0.7)
        else:
            self.sprite = arcade.Sprite("Prostredie/VezaPriatel2.png", 0.28)
        self.sprite.set_position(self.suradnicaX, self.suradnicaY)

    def jeVezaZnicena(self):
        return True if self.zivotVeze <= 0 else False

    def getSprite(self):
        return self.sprite

    def poskodVezu(self, poskodenie):
        self.zivotVeze -= poskodenie


class ZlatoZdroj(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.suradnicaX = x
        self.suradnicaY = y
        self.zivotyZlata = 160
        self.sprite = arcade.Sprite("Prostredie/Zlato.png", 0.8)
        self.sprite.set_position(self.suradnicaX, self.suradnicaY)
        self.suradnicaY += 50
        self.pocetKopacov = 0
        self.zoznamKopacov = []
        self.zoznamKopacov.append(None)
        self.zoznamKopacov.append(None)

    def getSprite(self):
        return self.sprite

    def pridajKopaca(self, kopac):
        if self.pocetKopacov < 2:
            if self.zoznamKopacov[0] is None:
                self.zoznamKopacov[0] = kopac
                self.pocetKopacov += 1
            elif self.zoznamKopacov[1] is None:
                self.zoznamKopacov[1] = kopac
                self.pocetKopacov += 1
                kopac.pravyKopac = True
            kopac.tazeneZlato = self

    def updateStavuZlata(self):
        zoznamMrtvychKopacov = []
        for kopaci in self.zoznamKopacov:
            if kopaci.mrtvy():
                zoznamMrtvychKopacov.append(kopaci)

        self.zoznamKopacov.remove(zoznamMrtvychKopacov)

    def jeZlatoVykopane(self):
        return True if self.zivotyZlata <= 0 else False

    def dajSuradnicuNaTazenie(self, kopac):
        suradnicaX = 0
        suradnicaY = 0

        if self.zoznamKopacov[0] is not None and self.zoznamKopacov[0] is kopac:
            suradnicaX = self.suradnicaX - 160
            suradnicaY = self.suradnicaY

        if self.zoznamKopacov[1] is not None and self.zoznamKopacov[1] is kopac:
            suradnicaX = self.suradnicaX + 125
            suradnicaY = self.suradnicaY

        return [
            suradnicaX,
            suradnicaY
        ]

    def vypisZivotyZlata(self):
        print(self.zivotyZlata)

    def zmenZivotyZdrojaZlataO(self, pocet):
        self.zivotyZlata -= pocet

    def getZivotyZlata(self):
        return self.zivotyZlata