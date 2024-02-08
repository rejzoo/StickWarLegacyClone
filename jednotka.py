import math
import time
import arcade
import objekty
from enum import Enum
from Healthbar import HealthBar

AKTUALIZACIA_ZA_FRAME = 10
SMER_VPRAVO = 0
SMER_VLAVO = 1
POCET_TEXTUR = 5
CIELOVA_NAVRAT_SUR_X_HRAC = -300
HRANICA_PRE_ODOVZDANIE_ZLATA_HRAC = 100
CIELOVA_NAVRAT_SUR_X_NEPRIATEL = 6900
HRANICA_PRE_ODOVZDANIE_ZLATA_NEPRIATEL = 6500

KAPACITA_VOZIKA = 80
RYCHLOST_POHYBU_KOPACA = 80
RYCHLOST_POHYBU_MECIARA = 120
RYCHLOST_POHYBU_KOPIJNIKA = 100

DOSAH_NA_UTOK_MECIAR = 100
DOSAH_NA_UTOK_KOPIJA = 130

MECIAR_POSKODENIE = 40
KOPIJA_POSKODENIE = 80

ZIVOTY_KOPIJNIKA = 200
ZIVOTY_MECIAR = 100
ZIVOTY_KOPAC = 100

SAFEZONA_HRACOVE_JEDNOTKY_X = 30
SAFEZONA_NEPRIATEL_JEDNOTKY_X = 6400

class AktualnyRozkaz(Enum):
    OBRANA = 1
    IDLE = 2
    UTOK = 3
    TAZENIE = 4

def load_texture_pair(filename):
    return [
        arcade.Sprite(filename),
        arcade.Sprite(filename, flipped_horizontally=True)
    ]

class Jednotka(arcade.Sprite):
    def __init__(self, x, y, nepriatel=False):
        super().__init__()
        self.suradnicaX = x
        self.suradnicaY = y
        self.zivoty = 100
        self.zoznamTexturNaAnimaciu = None
        self.sprite = None
        self.typJednotky = None
        self.aktualnyRozkaz = AktualnyRozkaz.IDLE
        self.aktualnyGlobalnyRozkaz = AktualnyRozkaz.IDLE
        self.aktualnaTextura = -1
        if nepriatel:
            self.smerPohybuCharakteru = SMER_VLAVO
        else:
            self.smerPohybuCharakteru = SMER_VPRAVO
        self.posunTexturu = 1
        self.nepriatel = nepriatel
        self.rychlostPohybuJednotky = 0
        self.naMieste = False
        self.HPBar = HealthBar(self.suradnicaX, self.suradnicaY, self.zivoty)

    def nacitajAnimacie(self, typJednotky):
        self.zoznamTexturNaAnimaciu = []
        for i in range(POCET_TEXTUR):
            texture = load_texture_pair(f"Animacie/{typJednotky}/{typJednotky}_p{i}.png")
            self.zoznamTexturNaAnimaciu.append(texture)

    def nastavNovyRozkaz(self, rozkaz):
        self.aktualnyRozkaz = rozkaz
        self.aktualnyGlobalnyRozkaz = rozkaz
        # Obrana
        if self.aktualnyRozkaz.value == 1:
            if self.nepriatel:
                self.smerPohybuCharakteru = SMER_VPRAVO
            else:
                self.smerPohybuCharakteru = SMER_VLAVO
        # Idle
        elif self.aktualnyRozkaz.value == 2:
            if self.nepriatel:
                self.smerPohybuCharakteru = SMER_VLAVO
            else:
                self.smerPohybuCharakteru = SMER_VPRAVO
        # Utok
        elif self.aktualnyRozkaz.value == 3:
            if self.nepriatel:
                self.smerPohybuCharakteru = SMER_VLAVO
            else:
                self.smerPohybuCharakteru = SMER_VPRAVO

    def updateAnimacie(self):
        if (self.aktualnyRozkaz == AktualnyRozkaz.IDLE
                and isinstance(self, Kopac) is not True
                and self.naMieste):
            textura = load_texture_pair(f"Animacie/{self.typJednotky}/{self.typJednotky}_idle.png")
            if self.nepriatel:
                self.sprite = textura[1]
            else:
                self.sprite = textura[0]
            return

        if self.aktualnyRozkaz == AktualnyRozkaz.TAZENIE:
            textura = load_texture_pair(f"Animacie/{self.typJednotky}/{self.typJednotky}_idle.png")
            if self.pravyKopac:
                self.sprite = textura[1]
            else:
                self.sprite = textura[0]
            return

        self.aktualnaTextura += self.posunTexturu
        if self.aktualnaTextura > POCET_TEXTUR * AKTUALIZACIA_ZA_FRAME:
            self.posunTexturu = -self.posunTexturu
            self.aktualnaTextura = AKTUALIZACIA_ZA_FRAME * (POCET_TEXTUR - 1)
            return
        if self.aktualnaTextura == -1:
            self.posunTexturu = -self.posunTexturu
            self.aktualnaTextura = AKTUALIZACIA_ZA_FRAME - 1
            return
        frame = self.aktualnaTextura // AKTUALIZACIA_ZA_FRAME
        smer = self.smerPohybuCharakteru
        if frame > POCET_TEXTUR - 1:
            return
        self.sprite = self.zoznamTexturNaAnimaciu[frame][smer]
        self.sprite.set_position(self.suradnicaX, self.suradnicaY)

    def navratDoSafeZony(self, delta_time): # Vytiahnut logiku na odovzdavanie zlata do pomocnej metody ?
        if (CIELOVA_NAVRAT_SUR_X_HRAC + 1 > self.suradnicaX > CIELOVA_NAVRAT_SUR_X_HRAC - 1
                and self.nepriatel is False):
            return

        if (HRANICA_PRE_ODOVZDANIE_ZLATA_HRAC + 1 > self.suradnicaX > HRANICA_PRE_ODOVZDANIE_ZLATA_HRAC - 1
                and self.nepriatel is False):
            if (isinstance(self, Kopac)
                    and self.aktualnyGlobalnyRozkaz == AktualnyRozkaz.IDLE
                    or self.aktualnyGlobalnyRozkaz == AktualnyRozkaz.UTOK):
                self.aktualnyRozkaz = AktualnyRozkaz.IDLE
                self.pocetDovezenehoZlata += self.vypocitajZaokruhlenuHodnotuDovezenehoZlata()
                self.pocetZlataVoVoziku = 0
                return
            elif isinstance(self, Kopac) and self.aktualnyGlobalnyRozkaz == AktualnyRozkaz.OBRANA:
                self.pocetDovezenehoZlata += self.vypocitajZaokruhlenuHodnotuDovezenehoZlata()
                self.pocetZlataVoVoziku = 0

        if (CIELOVA_NAVRAT_SUR_X_NEPRIATEL + 1 > self.suradnicaX > CIELOVA_NAVRAT_SUR_X_NEPRIATEL - 1
                and self.nepriatel):
            return

        if (HRANICA_PRE_ODOVZDANIE_ZLATA_NEPRIATEL + 1 > self.suradnicaX > HRANICA_PRE_ODOVZDANIE_ZLATA_NEPRIATEL - 1
                and self.nepriatel):
            if (isinstance(self, Kopac)
                    and self.aktualnyGlobalnyRozkaz == AktualnyRozkaz.IDLE
                    or self.aktualnyGlobalnyRozkaz == AktualnyRozkaz.UTOK):
                self.aktualnyRozkaz = AktualnyRozkaz.IDLE
                self.pocetZlataVoVoziku = 0
                return
            elif isinstance(self, Kopac) and self.aktualnyGlobalnyRozkaz == AktualnyRozkaz.OBRANA:
                self.pocetDovezenehoZlata += self.vypocitajZaokruhlenuHodnotuDovezenehoZlata()
                self.pocetZlataVoVoziku = 0

        if self.suradnicaX > CIELOVA_NAVRAT_SUR_X_HRAC and self.nepriatel is False:
            self.suradnicaX -= self.rychlostPohybuJednotky * delta_time
            self.smerPohybuCharakteru = SMER_VLAVO
        elif self.suradnicaX < CIELOVA_NAVRAT_SUR_X_NEPRIATEL and self.nepriatel:
            self.suradnicaX += self.rychlostPohybuJednotky * delta_time
            self.smerPohybuCharakteru = SMER_VPRAVO

    def updateVojaka(self, delta_time, zoznamJednotiek, veza):
        self.sprite.set_position(self.suradnicaX, self.suradnicaY)
        self.HPBar.updateHpBar(self.suradnicaX, self.suradnicaY, self.zivoty)
        self.spravanieVojaka(delta_time, zoznamJednotiek, veza)

    def nachadzaSaVojakVSafeZone(self):
        if self.nepriatel and self.suradnicaX > SAFEZONA_NEPRIATEL_JEDNOTKY_X:
            return True
        if self.nepriatel != False and self.suradnicaX < SAFEZONA_HRACOVE_JEDNOTKY_X:
            return True
        return False

    def ObdrzPoskodenie(self, poskodenie):
        self.zivoty -= poskodenie

    def mrtvy(self):
        return True if self.zivoty <= 0 else False

    def getSprite(self):
        return self.sprite

    def spravanieVojaka(self, delta_time, zoznamJednotiek, veza):
        pass

class Kopac(Jednotka):
    def __init__(self, x, y, nepriatel=False):
        super().__init__(x, y, nepriatel=nepriatel)
        self.pocetDovezenehoZlata = 0
        self.pocetZlataVoVoziku = 0
        self.pocetZlataNaOdstranenieZLoziska = 0 #nepouziva sa zatial neviem este
        self.typJednotky = "Kopac"
        self.nacitajAnimacie(self.typJednotky)
        self.sprite = arcade.Sprite("Animacie/Kopac/Kopac_idle.png")
        self.rychlostPohybuJednotky = RYCHLOST_POHYBU_KOPACA
        self.tazeneZlato = None
        self.pravyKopac = False
        self.odstraneneZlato = False
        self.zivoty = ZIVOTY_KOPAC

    def skontrolujStavZlata(self):
        if self.tazeneZlato is not None and self.tazeneZlato.jeZlatoVykopane():
            self.tazeneZlato = None

    def cestujZaZlatom(self, delta_time):
        self.skontrolujStavZlata()
        if self.tazeneZlato is None:
            return

        suradniceXY = self.tazeneZlato.dajSuradnicuNaTazenie(self)

        if (suradniceXY[0] + 1 > self.suradnicaX > suradniceXY[0] - 1
                and suradniceXY[1] + 10 > self.suradnicaY > suradniceXY[1] - 10):
            return True

        if self.suradnicaX < suradniceXY[0] and self.nepriatel is False:
            self.suradnicaX += self.rychlostPohybuJednotky * delta_time
            self.smerPohybuCharakteru = SMER_VPRAVO
        elif self.suradnicaX > suradniceXY[0] and self.nepriatel:
            self.suradnicaX -= self.rychlostPohybuJednotky * delta_time
            self.smerPohybuCharakteru = SMER_VLAVO

        if suradniceXY[1] + 10 > self.suradnicaY > suradniceXY[1] - 10:
            return False

        if self.suradnicaY < suradniceXY[1]:
            self.suradnicaY += self.rychlostPohybuJednotky * delta_time
        elif self.suradnicaY > suradniceXY[1]:
            self.suradnicaY -= self.rychlostPohybuJednotky * delta_time
        return False

    def vytazZlato(self, delta_time):
        self.smerAnimacie()

        if self.pocetZlataVoVoziku < 80 and self.tazeneZlato.jeZlatoVykopane() is False:
            self.pocetZlataVoVoziku += 10 * delta_time

        self.pocetZlataNaOdstranenieZLoziska = math.ceil(self.pocetZlataVoVoziku)

        if self.pocetZlataVoVoziku >= KAPACITA_VOZIKA:
            self.pocetZlataVoVoziku = 80
            self.aktualnyRozkaz = AktualnyRozkaz.OBRANA
            self.odstranPocetVytazenehoZlataZoZivotaZdroja()
            if self.nepriatel:
                self.smerPohybuCharakteru = SMER_VPRAVO
            else:
                self.smerPohybuCharakteru = SMER_VLAVO

    def updateKopaca(self, delta_time):
        if self.pocetZlataVoVoziku == 0:
            self.odstraneneZlato = False
        if self.aktualnyRozkaz == AktualnyRozkaz.OBRANA:
            self.odstranPocetVytazenehoZlataZoZivotaZdroja()
            self.navratDoSafeZony(delta_time)
        elif self.aktualnyRozkaz == AktualnyRozkaz.IDLE or self.aktualnyRozkaz == AktualnyRozkaz.TAZENIE:
            if self.cestujZaZlatom(delta_time):
                self.aktualnyRozkaz = AktualnyRozkaz.TAZENIE
                self.vytazZlato(delta_time)
        elif self.aktualnyRozkaz == AktualnyRozkaz.UTOK:
            self.aktualnyRozkaz = AktualnyRozkaz.IDLE
            self.cestujZaZlatom(delta_time)
        self.sprite.set_position(self.suradnicaX, self.suradnicaY)
        self.HPBar.updateHpBar(self.suradnicaX, self.suradnicaY, self.zivoty)

    def vypocitajZaokruhlenuHodnotuDovezenehoZlata(self):
        if self.pocetZlataVoVoziku < 5:
            return 0
        elif self.pocetZlataVoVoziku <= 25:
            return 20
        elif self.pocetZlataVoVoziku <= 45:
            return 40
        elif self.pocetZlataVoVoziku <= 65:
            return 60
        else:
            return 80

    def odstranPocetVytazenehoZlataZoZivotaZdroja(self):
        if self.odstraneneZlato:
            return

        self.tazeneZlato.zmenZivotyZdrojaZlataO(self.vypocitajZaokruhlenuHodnotuDovezenehoZlata())
        self.odstraneneZlato = True

    def smerAnimacie(self):
        if self.pravyKopac and self.nepriatel is False and self.smerPohybuCharakteru is SMER_VPRAVO:
            self.smerPohybuCharakteru = SMER_VLAVO

        if self.pravyKopac is False and self.nepriatel and self.smerPohybuCharakteru is SMER_VLAVO:
            self.smerPohybuCharakteru = SMER_VPRAVO

class Vojak(Jednotka): # Dorobit cestovanie za cielom
    def __init__(self, x, y, nepriatel=False, poskodenie=0,):
        super().__init__(x, y, nepriatel=nepriatel)
        self.poskodenie = poskodenie
        self.surXIDLE = 0
        self.surYIDLE = 0
        self.cielNaUtok = None
        self.vzdialenostKCielu = 0
        self.bojuje = False
        self.dosahUtoku = None
        self.casPoslednehoUtoku = time.time()

    def spravanieVojaka(self, delta_time, zoznamJednotiek, veza):
        if self.aktualnyRozkaz == AktualnyRozkaz.OBRANA:
            self.navratDoSafeZony(delta_time)
            self.naMieste = False
        elif self.aktualnyRozkaz == AktualnyRozkaz.IDLE:
            if self.nastupJednotkuNaPoziciu(delta_time):
                self.naMieste = True
        elif self.aktualnyRozkaz == AktualnyRozkaz.UTOK:
            self.naMieste = False
            if self.bojuje: # Dorobit to ze ak jednotka umrie tak bojuje = False a ak pride na vzdialenost utoku True
                self.zautoc()
            else:
                self.najdiCielPreUtok(zoznamJednotiek, veza)
                self.pohybKCielu(delta_time)

    def nastupJednotkuNaPoziciu(self, delta_time):
        if (self.surXIDLE + 1 > self.suradnicaX > self.surXIDLE - 1
                and self.surYIDLE + 10 > self.suradnicaY > self.surYIDLE - 10):
            return True

        if self.nepriatel is False and self.suradnicaX < self.surXIDLE:
            self.suradnicaX += self.rychlostPohybuJednotky * delta_time
            self.smerPohybuCharakteru = SMER_VPRAVO
        elif self.nepriatel is False and self.suradnicaX > self.surXIDLE:
            self.suradnicaX -= self.rychlostPohybuJednotky * delta_time
            self.smerPohybuCharakteru = SMER_VLAVO

        if self.nepriatel and self.suradnicaX > self.surXIDLE:
            self.suradnicaX -= self.rychlostPohybuJednotky * delta_time
            self.smerPohybuCharakteru = SMER_VLAVO
        elif self.nepriatel and self.suradnicaX < self.surXIDLE:
            self.suradnicaX += self.rychlostPohybuJednotky * delta_time
            self.smerPohybuCharakteru = SMER_VPRAVO

        if self.surYIDLE + 10 > self.suradnicaY > self.surYIDLE - 10:
            return False

        if self.suradnicaY < self.surYIDLE:
            self.suradnicaY += self.rychlostPohybuJednotky * delta_time
        elif self.suradnicaY > self.surYIDLE:
            self.suradnicaY -= self.rychlostPohybuJednotky * delta_time
        return False

    def udelPoskodenie(self, jednotka):
        jednotka.ObdrzPoskodenie(self.poskodenie)

    def zautoc(self):
        aktualnyCas = time.time()
        if aktualnyCas - self.casPoslednehoUtoku >= 2:
            if isinstance(self.cielNaUtok, objekty.Veza):
                self.cielNaUtok.poskodVezu(self.poskodenie)
                self.bojuje = False
                self.casPoslednehoUtoku = time.time()
                return
            self.udelPoskodenie(self.cielNaUtok)
            self.casPoslednehoUtoku = time.time()
        self.bojuje = False

    def najdiCielPreUtok(self, zoznamJednotiek, veza):
        najkratsiaVzdialenost = 500000
        for jednotka in zoznamJednotiek:
            if jednotka.nachadzaSaVojakVSafeZone():
                continue
            vypocitanaVzdialenost = self.vzdialenost(self.suradnicaX, self.suradnicaY, jednotka.suradnicaX, jednotka.suradnicaY)
            if vypocitanaVzdialenost < najkratsiaVzdialenost:
                self.cielNaUtok = jednotka
                najkratsiaVzdialenost = vypocitanaVzdialenost
                self.vzdialenostKCielu = vypocitanaVzdialenost

        vzdialenostKVezi = self.vzdialenost(self.suradnicaX, self.suradnicaY, veza.suradnicaX, veza.suradnicaY)
        if vzdialenostKVezi < najkratsiaVzdialenost:
            self.cielNaUtok = veza
            self.vzdialenostKCielu = vzdialenostKVezi

    def vzdialenost(self, suradnicaX1, suradnicaY1, suradnicaX2, suradnicaY2):
        vzdialenostX = abs(suradnicaX1 - suradnicaX2)
        vzdialenostY = abs(suradnicaY1 - suradnicaY2)
        vzdialenost = math.sqrt(math.pow(vzdialenostX, 2) + math.pow(vzdialenostY, 2))
        return vzdialenost

    def pohybKCielu(self, delta_time):
        if (self.cielNaUtok.suradnicaX + self.dosahUtoku > self.suradnicaX > self.cielNaUtok.suradnicaX - self.dosahUtoku
                and self.cielNaUtok.suradnicaY + 10 > self.suradnicaY > self.cielNaUtok.suradnicaY - 10):
            self.bojuje = True
            return

        if self.cielNaUtok is not None and self.nepriatel is False and self.suradnicaX > self.cielNaUtok.suradnicaX:
            self.suradnicaX -= self.rychlostPohybuJednotky * delta_time
            self.smerPohybuCharakteru = SMER_VLAVO
        elif self.cielNaUtok is not None and self.nepriatel is False and self.suradnicaX < self.cielNaUtok.suradnicaX:
            self.suradnicaX += self.rychlostPohybuJednotky * delta_time
            self.smerPohybuCharakteru = SMER_VPRAVO

        if (self.cielNaUtok.suradnicaY + 10 > self.suradnicaY > self.cielNaUtok.suradnicaY - 10) is False\
                and self.vzdialenostKCielu < 700:
            if self.suradnicaY < self.cielNaUtok.suradnicaY:
                self.suradnicaY += self.rychlostPohybuJednotky * delta_time
            elif self.suradnicaY > self.cielNaUtok.suradnicaY:
                self.suradnicaY -= self.rychlostPohybuJednotky * delta_time

        #if
        #elif self.suradnicaX < CIELOVA_NAVRAT_SUR_X_NEPRIATEL and self.nepriatel:
        #    self.suradnicaX += self.rychlostPohybuJednotky * delta_time
        #    self.smerPohybuCharakteru = SMER_VPRAVO

class Meciar(Vojak):
    def __init__(self, x, y, nepriatel=False):
        super().__init__(x, y, nepriatel=nepriatel)
        self.typJednotky = "Meciar"
        self.nacitajAnimacie(self.typJednotky)
        self.sprite = arcade.Sprite("Animacie/Meciar/Meciar_idle.png")
        self.rychlostPohybuJednotky = RYCHLOST_POHYBU_MECIARA
        self.zivoty = ZIVOTY_MECIAR
        self.dosahUtoku = DOSAH_NA_UTOK_MECIAR
        self.poskodenie = MECIAR_POSKODENIE

    def spravanieVojaka(self, delta_time, zoznamJednotiek, veza):
        super().spravanieVojaka(delta_time, zoznamJednotiek, veza)

    def udelPoskodenie(self, jednotka):
        super().udelPoskodenie(jednotka)

class Kopijnik(Vojak):
    def __init__(self, x, y, nepriatel=False):
        super().__init__(x, y, nepriatel=nepriatel)
        self.typJednotky = "Kopijnik"
        self.nacitajAnimacie(self.typJednotky)
        self.sprite = arcade.Sprite("Animacie/Kopijnik/Kopijnik_idle.png")
        self.rychlostPohybuJednotky = RYCHLOST_POHYBU_KOPIJNIKA
        self.zivoty = ZIVOTY_KOPIJNIKA
        self.dosahUtoku = DOSAH_NA_UTOK_KOPIJA
        self.poskodenie = KOPIJA_POSKODENIE
        self.HPBar.hp = self.zivoty
        self.HPBar.maxHp = self.zivoty

    def spravanieVojaka(self, delta_time, zoznamJednotiek, veza):
        super().spravanieVojaka(delta_time, zoznamJednotiek, veza)

    def udelPoskodenie(self, jednotka):
        super().udelPoskodenie(jednotka)