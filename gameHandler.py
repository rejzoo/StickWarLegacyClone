import arcade
import arcade.gui
import jednotka
import objekty
from tlacidlo import Tlacidlo
from tlacidlo import TypTlacidla
import time
import random
from backGround import BackGround

RYCHLOST_POSUNU_KAMERY = 15
SPAWN_SURADNICA_X_HRACA = -150
SPAWN_SURADNICA_X_NEPRIATELA = 6850
MAXIMALNY_POCET_JEDNOTIEK = 22
MAXIMALNY_POCET_KOPACOV = 6


class Hra(arcade.Window):
    def __init__(self, sirka, vyska, title):
        super().__init__(sirka, vyska, title)
        arcade.set_background_color(arcade.color.WHITE)

        # Zoznamy jednotiek a veze
        self.zoznamHracovychJednotiek = []
        self.vezaHraca = None
        self.zoznamNepriatelJednotiek = []
        self.vezaNepriatela = None
        self.zoznamLoziskZlataHracovaStrana = []
        self.zoznamLoziskZlataNepriatelovaStrana = []

        # Kamera
        self.poziciaMyskyX = 0
        self.poziciaMyskyY = 0
        self.posunKamery = 0
        self.kameraSprity = arcade.Camera(sirka, vyska)
        self.kameraSprity.move_to((0, 0), 1)
        self.camera_gui = arcade.Camera(sirka, vyska)

        # Zoznamy tlacidiel a manazer GUI
        self.manazerGUI = None
        self.zoznamTlacidiel = []

        self.aktualnyRozkaz = jednotka.AktualnyRozkaz.IDLE
        self.pocetHracovhoZlata = 0

        # Matice pre formacie pre IDLE rezim - obsahuje vojakov
        self.formaciaHracovychJednotiek = [[None for _ in range(4)] for _ in range(4)]
        self.formaciaNepriatelovychJednotiek = [[None for _ in range(4)] for _ in range(4)]
        # Matice pre suradnice pre urcite pozicie
        self.suradniceHracFormacia = [
            [(1150, 350), (1250, 350), (1350, 350), (1450, 350)],
            [(1150, 300), (1250, 300), (1350, 300), (1450, 300)],
            [(1150, 250), (1250, 250), (1350, 250), (1450, 250)],
            [(1150, 200), (1250, 200), (1350, 200), (1450, 200)]
        ]
        self.suradniceNeprFormacia = [
            [(5000, 350), (5100, 350), (5200, 350), (5300, 350)],
            [(5000, 300), (5100, 300), (5200, 300), (5300, 300)],
            [(5000, 250), (5100, 250), (5200, 250), (5300, 250)],
            [(5000, 200), (5100, 200), (5200, 200), (5300, 200)]
        ]

        self.manazerPozadia = BackGround()

    def vytvorObjektyNaMape(self):
        self.vezaHraca = objekty.Veza(400, 500)
        self.vezaNepriatela = objekty.Veza(6000, 500, nepriatel=True)

        self.zoznamLoziskZlataHracovaStrana.append(objekty.ZlatoZdroj(600, 150))
        self.zoznamLoziskZlataHracovaStrana.append(objekty.ZlatoZdroj(830, 230))
        self.zoznamLoziskZlataHracovaStrana.append(objekty.ZlatoZdroj(1050, 190))

        self.zoznamLoziskZlataNepriatelovaStrana.append(objekty.ZlatoZdroj(5800, 200))
        self.zoznamLoziskZlataNepriatelovaStrana.append(objekty.ZlatoZdroj(5600, 230))
        self.zoznamLoziskZlataNepriatelovaStrana.append(objekty.ZlatoZdroj(5400, 150))

    def setup(self):

        self.vytvorTlacidla()
        self.vytvorObjektyNaMape()

        # Vytvorenie vezi a zakladnych kopacov pre Hraca aj PC
        # Hrac
        kopacHrac1 = jednotka.Kopac(SPAWN_SURADNICA_X_HRACA, 250)
        kopacHrac2 = jednotka.Kopac(SPAWN_SURADNICA_X_HRACA, 300)
        self.zoznamHracovychJednotiek.append(kopacHrac1)
        self.zoznamHracovychJednotiek.append(kopacHrac2)

        # Nepriatel
        kopacNepr1 = jednotka.Kopac(SPAWN_SURADNICA_X_NEPRIATELA, 350, True)
        kopacNepr2 = jednotka.Kopac(SPAWN_SURADNICA_X_NEPRIATELA, 300, True)
        self.zoznamNepriatelJednotiek.append(kopacNepr1)
        self.zoznamNepriatelJednotiek.append(kopacNepr2)

    # Vykreslovanie Spritov a textur
    def on_draw(self):
        self.clear()
        arcade.start_render()

        self.kameraSprity.use()
        self.manazerPozadia.vykresli()
        self.vezaHraca.getSprite().draw()
        self.vezaHraca.HPBar.vykresli()
        self.vezaNepriatela.getSprite().draw()
        self.vezaNepriatela.HPBar.vykresli()
        self.manazerPozadia.vykresliTravuPriSochach()

        for zlato in self.zoznamLoziskZlataHracovaStrana:
            zlato.getSprite().draw()

        for zlato in self.zoznamLoziskZlataNepriatelovaStrana:
            zlato.getSprite().draw()

        for priatel in self.zoznamHracovychJednotiek:
            priatel.getSprite().draw()
            priatel.HPBar.vykresli()

        for nepriatel in self.zoznamNepriatelJednotiek:
            nepriatel.getSprite().draw()
            nepriatel.HPBar.vykresli()

        # Kamera
        self.camera_gui.use()
        self.debugPanel()
        self.manazerGUI.draw()

    # Update
    def on_update(self, delta_time):
        self.updateLoziskZlata()
        self.updateJednotiek(delta_time)
        # self.odstranMrtvehoVojakaZFormacie()
        self.skontrolujPocetDovezenychVozikovZlata()

        # kamera
        self.posunKMysi()

        self.manazerPozadia.updatePolohyMesiaca(self.posunKamery)
        self.updateTlacidiel()

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        self.poziciaMyskyX = x
        self.poziciaMyskyY = y

    # Pomocna metoda
    def updateLoziskZlata(self):
        for loziskoZlata in self.zoznamLoziskZlataHracovaStrana:
            if loziskoZlata.jeZlatoVykopane():
                self.zoznamLoziskZlataHracovaStrana.remove(loziskoZlata)
            for jednotkaHracova in self.zoznamHracovychJednotiek:
                if isinstance(jednotkaHracova, jednotka.Kopac):
                    if jednotkaHracova.tazeneZlato is None:
                        loziskoZlata.pridajKopaca(jednotkaHracova)

        for loziskoZlata in self.zoznamLoziskZlataNepriatelovaStrana:
            if loziskoZlata.jeZlatoVykopane():
                self.zoznamLoziskZlataNepriatelovaStrana.remove(loziskoZlata)
            for jednotkaNepriatelova in self.zoznamNepriatelJednotiek:
                if isinstance(jednotkaNepriatelova, jednotka.Kopac):
                    if jednotkaNepriatelova.tazeneZlato is None:
                        loziskoZlata.pridajKopaca(jednotkaNepriatelova)

    # Pomocna metoda
    def updateJednotiek(self, delta_time):

        for jednotkaHracova in self.zoznamHracovychJednotiek:
            if jednotkaHracova.mrtvy():
                self.zoznamHracovychJednotiek.remove(jednotkaHracova)
                continue
            jednotkaHracova.updateAnimacie()
            if isinstance(jednotkaHracova, jednotka.Kopac):
                jednotkaHracova.updateKopaca(delta_time)
            else:
                jednotkaHracova.updateVojaka(delta_time, self.zoznamHracovychJednotiek, self.zoznamNepriatelJednotiek,
                                             self.vezaHraca, self.vezaNepriatela)

        for jednotkaNepriatel in self.zoznamNepriatelJednotiek:
            if jednotkaNepriatel.mrtvy():
                self.zoznamNepriatelJednotiek.remove(jednotkaNepriatel)
                continue
            jednotkaNepriatel.updateAnimacie()
            if isinstance(jednotkaNepriatel, jednotka.Kopac):
                jednotkaNepriatel.updateKopaca(delta_time)
            else:
                jednotkaNepriatel.updateVojaka(delta_time, self.zoznamHracovychJednotiek, self.zoznamNepriatelJednotiek,
                                               self.vezaHraca, self.vezaNepriatela)

    def updateTlacidiel(self):
        for tlacidlo in self.zoznamTlacidiel:
            tlacidlo.update(self.aktualnyRozkaz)

    def posunKMysi(self):
        # VLAVO
        lavaHranica = 80
        pravaHranica = self.width - lavaHranica
        hornaHranica = self.height - 200
        if self.poziciaMyskyX < lavaHranica and self.poziciaMyskyY < hornaHranica and self.posunKamery > -10:
            self.posunKamery -= 1

        # VPRAVO
        if self.poziciaMyskyX > pravaHranica and self.poziciaMyskyY < hornaHranica and self.posunKamery < 335:
            self.posunKamery += 1

        # Vypocitanie novej X pozicie
        novaPozicia = (self.posunKamery * RYCHLOST_POSUNU_KAMERY), 0
        self.kameraSprity.move_to(novaPozicia)

    def vytvorTlacidla(self):
        self.manazerGUI = arcade.gui.UIManager()
        self.manazerGUI.enable()
        buyTlacidla = arcade.gui.UIBoxLayout(vertical=False, space_between=10)
        posunTlacidla = arcade.gui.UIBoxLayout(vertical=False, space_between=1402)
        rozkazyTlacidla = arcade.gui.UIBoxLayout(vertical=False, space_between=10)

        buttonKupKrompac = Tlacidlo(TypTlacidla.TLACIDLO_KROMPAC, self.pridanieVojaka)
        buttonKupMec = Tlacidlo(TypTlacidla.TLACIDLO_MEC, self.pridanieVojaka)
        buttonKupKopiju = Tlacidlo(TypTlacidla.TLACIDLO_KOPIJA, self.pridanieVojaka)
        buyTlacidla.add(buttonKupKrompac)
        buyTlacidla.add(buttonKupMec)
        buyTlacidla.add(buttonKupKopiju)

        buttonPosunVlavo = Tlacidlo(TypTlacidla.TLACIDLO_POSUN_VLAVO, self.posunKameru)
        buttonPosunVpravo = Tlacidlo(TypTlacidla.TLACIDLO_POSUN_VPRAVO, self.posunKameru)
        posunTlacidla.add(buttonPosunVlavo)
        posunTlacidla.add(buttonPosunVpravo)

        buttonUtok = Tlacidlo(TypTlacidla.TLACIDLO_UTOK, self.nastavenieRozkazov, tlacidloBezResetu=True)
        buttonDeff = Tlacidlo(TypTlacidla.TLACIDLO_OBRANA, self.nastavenieRozkazov, tlacidloBezResetu=True)
        buttonIdle = Tlacidlo(TypTlacidla.TLACIDLO_IDLE, self.nastavenieRozkazov, tlacidloBezResetu=True)
        rozkazyTlacidla.add(buttonDeff)
        rozkazyTlacidla.add(buttonIdle)
        rozkazyTlacidla.add(buttonUtok)

        buttonPauza = Tlacidlo(TypTlacidla.TLACIDLO_PAUZA, self.pauzniHru)

        self.manazerGUI.add(arcade.gui.UIAnchorWidget(align_x=-660, align_y=340, child=buyTlacidla))
        self.manazerGUI.add(arcade.gui.UIAnchorWidget(align_x=0, align_y=270, child=posunTlacidla))
        self.manazerGUI.add(arcade.gui.UIAnchorWidget(align_x=658, align_y=340, child=rozkazyTlacidla))
        self.manazerGUI.add(arcade.gui.UIAnchorWidget(anchor_x="center", align_y=340, child=buttonPauza))

        self.zoznamTlacidiel.append(buttonKupKrompac)
        self.zoznamTlacidiel.append(buttonKupMec)
        self.zoznamTlacidiel.append(buttonKupKopiju)
        self.zoznamTlacidiel.append(buttonPosunVlavo)
        self.zoznamTlacidiel.append(buttonPosunVpravo)
        self.zoznamTlacidiel.append(buttonPauza)
        self.zoznamTlacidiel.append(buttonUtok)
        self.zoznamTlacidiel.append(buttonDeff)
        self.zoznamTlacidiel.append(buttonIdle)

    def getPocetHracovychJednotiek(self):
        return len(self.zoznamHracovychJednotiek)

    def pridajDoFormacie(self, novyVojak):
        if novyVojak.nepriatel is False:
            for j in range(len(self.formaciaHracovychJednotiek[0]) - 1, -1, -1):  # Iterate over columns in reverse
                for i in range(len(self.formaciaHracovychJednotiek)):  # Iterate over rows
                    if self.formaciaHracovychJednotiek[i][j] is None:
                        self.formaciaHracovychJednotiek[i][j] = novyVojak
                        suradnicaXYFormacia = self.suradniceHracFormacia[i][j]
                        novyVojak.surXIDLE = suradnicaXYFormacia[0]
                        novyVojak.surYIDLE = suradnicaXYFormacia[1]
                        break  # Stop iterating through rows after adding one soldier in the column
                else:
                    continue  # Continue to the next iteration of the outer loop if soldier is not added
                break
        else:
            for j in range(len(self.formaciaNepriatelovychJednotiek[0]) - 1, -1, -1):  # Iterate over columns in reverse
                for i in range(len(self.formaciaNepriatelovychJednotiek)):  # Iterate over rows
                    if self.formaciaNepriatelovychJednotiek[i][j] is None:
                        self.formaciaNepriatelovychJednotiek[i][j] = novyVojak
                        suradnicaXYFormacia = self.suradniceNeprFormacia[i][j]
                        novyVojak.surXIDLE = suradnicaXYFormacia[0]
                        novyVojak.surYIDLE = suradnicaXYFormacia[1]
                        break  # Stop iterating through rows after adding one soldier in the column
                else:
                    continue  # Continue to the next iteration of the outer loop if soldier is not added
                break

    def odstranMrtvychZFormacie(self):
        zoznamMrtvych = []
        for riadok in self.formaciaHracovychJednotiek:
            for vojak in riadok:
                if vojak is not None:
                    print(vojak.zivoty, end='\t')
                    if vojak.mrtvy():
                        zoznamMrtvych.append(vojak)
                else:
                    print("_", end='\t')
            print()

        for i in range(len(self.formaciaHracovychJednotiek)):
            for j in range(len(self.formaciaHracovychJednotiek[0])):
                vojak = self.formaciaHracovychJednotiek[i][j]
                for mrtvyVojak in zoznamMrtvych:
                    if vojak == mrtvyVojak:
                        self.zoznamHracovychJednotiek[i][j] = None

    def pridanieVojaka(self, typJednotky):
        if self.getPocetHracovychJednotiek() >= MAXIMALNY_POCET_JEDNOTIEK:
            return
        if (self.getPocetHracovychJednotiek() - self.getPocetKopacov() >= MAXIMALNY_POCET_JEDNOTIEK - MAXIMALNY_POCET_KOPACOV
                and typJednotky != "Krompac"):
            return
        suradnicaY = random.randint(200, 400)
        pridanaJednotka = None
        match typJednotky:
            case "Krompac":
                if self.getPocetKopacov() < MAXIMALNY_POCET_KOPACOV:
                    pridanaJednotka = jednotka.Kopac(SPAWN_SURADNICA_X_HRACA, suradnicaY)
                    self.zoznamHracovychJednotiek.append(pridanaJednotka)
                else:
                    return

            case "Mec":
                pridanaJednotka = jednotka.Meciar(SPAWN_SURADNICA_X_HRACA, suradnicaY)
                self.zoznamHracovychJednotiek.append(pridanaJednotka)

            case "Kopija":
                pridanaJednotka = jednotka.Kopijnik(SPAWN_SURADNICA_X_HRACA, suradnicaY)
                self.zoznamHracovychJednotiek.append(pridanaJednotka)

        if isinstance(pridanaJednotka, jednotka.Kopac) is False:
            self.pridajDoFormacie(pridanaJednotka)
        pridanaJednotka.nastavNovyRozkaz(self.aktualnyRozkaz)

    def posunKameru(self, smerPosunutia):
        match smerPosunutia:
            case "PosunVlavo":
                self.posunKamery = -10

            case "PosunVpravo":
                self.posunKamery = 335

    def nastavenieRozkazov(self, rozkaz):
        self.aktualnyRozkaz = rozkaz
        for hracovaJednotka in self.zoznamHracovychJednotiek:
            hracovaJednotka.nastavNovyRozkaz(rozkaz)

    def pauzniHru(self, neniPotreba):
        #self.buttonPauza.setStlacene()
        #self.casStlacenia = time.time()
        pass

    def getPocetKopacov(self):
        pocetKopacov = 0
        for jednotkaHrac in self.zoznamHracovychJednotiek:
            if isinstance(jednotkaHrac, jednotka.Kopac):
                pocetKopacov += 1
        return pocetKopacov

    def skontrolujPocetDovezenychVozikovZlata(self):
        zlatoNaPridanie = 0
        for kopac in self.zoznamHracovychJednotiek:
            if isinstance(kopac, jednotka.Kopac):
                zlatoNaPridanie += int(kopac.pocetDovezenehoZlata)
                kopac.pocetDovezenehoZlata = 0
        self.pocetHracovhoZlata += int(zlatoNaPridanie)

    def debugPanel(self):
        arcade.draw_rectangle_filled(self.width // 2, 20, self.width, 40, arcade.color.ALMOND)
        text = (f"      Rychlost:           ({self.posunKamery:5.1f})"
                f"      Scroll value:       ({self.posunKamery:5.1f})"
                f"      Pozicia X Mys:      ({self.poziciaMyskyX:5.1f})"
                f"      Pocet jednotiek:    ({self.getPocetHracovychJednotiek():})"
                f"      Pocet Zlata: ({self.pocetHracovhoZlata:})")
        arcade.draw_text(text, 10, 10, arcade.color.BLACK_BEAN, 20)
