import time

import arcade
import arcade.gui

import Menu
import jednotka
import objekty
import random
from tlacidlo import Tlacidlo
from tlacidlo import TypTlacidla
from backGround import BackGround

RYCHLOST_POSUNU_KAMERY = 15
SPAWN_SURADNICA_X_HRACA = -150
SPAWN_SURADNICA_X_NEPRIATELA = 6850
MAXIMALNY_POCET_JEDNOTIEK = 22
MAXIMALNY_POCET_KOPACOV = 6

SIRKA_OBRAZOVKY_HRY = 1600
VYSKA_OBRAZOVKY_HRY = 800

CENA_KOPACA = 150
CENA_MECIARA = 125
CENA_KOPIJNIKA = 500

DLZKA_SPAWNU_KOPACA = 2
DLZKA_SPAWNU_MECIARA = 2
DLZKA_SPAWNU_KOPIJNIKA = 3

class HraView(arcade.View):
    def __init__(self):
        super().__init__()
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
        self.kameraSprity = arcade.Camera(SIRKA_OBRAZOVKY_HRY, VYSKA_OBRAZOVKY_HRY)
        self.kameraSprity.move_to((0, 0), 1)
        self.camera_gui = arcade.Camera(SIRKA_OBRAZOVKY_HRY, VYSKA_OBRAZOVKY_HRY)

        # Zoznamy tlacidiel a manazer GUI
        self.manazerGUI = None
        self.zoznamTlacidiel = []

        self.aktualnyRozkazHrac = jednotka.AktualnyRozkaz.IDLE
        self.pocetHracovhoZlata = 100000

        self.aktualnyRozkazEnemy = jednotka.AktualnyRozkaz.IDLE
        self.pocetEnemyZlata = 0

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
        self.casZapnutiaHry = time.time()

        self.zoznamJednotiekNaPridanieHrac = []
        self.zoznamJednotiekNaPridanieEnemy = []

        self.casSpawnuPoslednejJednotkyHrac = 0
        self.casSpawnuPoslednejJednotkyEnemy = 0

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
        self.manazerGUI.add(arcade.gui.UIAnchorWidget(align_x=0, align_y=220, child=posunTlacidla))
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
        self.vykresliPocetVerbujucichJednotiek()
        self.debugPanel()
        self.manazerGUI.draw()

    # Update
    def on_update(self, delta_time):
        self.updateLoziskZlata()
        self.updateJednotiek(delta_time)
        self.skontrolujPocetDovezenychVozikovZlata()
        self.spawnujJednotky()

        # kamera
        self.posunKameryVlavoVpravo()

        self.manazerPozadia.updatePolohyMesiaca(self.posunKamery)
        self.updateTlacidiel()
        self.kontrolaZivotovVezi()

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        self.poziciaMyskyX = x
        self.poziciaMyskyY = y

    def on_show(self):
        self.window.set_size(SIRKA_OBRAZOVKY_HRY, VYSKA_OBRAZOVKY_HRY)
        arcade.set_viewport(0, SIRKA_OBRAZOVKY_HRY, 0, VYSKA_OBRAZOVKY_HRY)
        self.window.center_window()

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
                jednotkaHracova.updateVojaka(delta_time, self.zoznamNepriatelJednotiek, self.vezaNepriatela)

        for jednotkaNepriatel in self.zoznamNepriatelJednotiek:
            if jednotkaNepriatel.mrtvy():
                self.zoznamNepriatelJednotiek.remove(jednotkaNepriatel)
                continue
            jednotkaNepriatel.updateAnimacie()
            if isinstance(jednotkaNepriatel, jednotka.Kopac):
                jednotkaNepriatel.updateKopaca(delta_time)
            else:
                print(jednotkaNepriatel.surXIDLE)
                jednotkaNepriatel.updateVojaka(delta_time, self.zoznamHracovychJednotiek, self.vezaHraca)

    def updateTlacidiel(self):
        for tlacidlo in self.zoznamTlacidiel:
            tlacidlo.update(self.aktualnyRozkazHrac)

    def kontrolaZivotovVezi(self):
        if self.vezaHraca.jeVezaZnicena():
            self.window.show_view(Menu.EndScreen("Pocitac", self.casZapnutiaHry))
        if self.vezaNepriatela.jeVezaZnicena():
            self.window.show_view(Menu.EndScreen("Hrac", self.casZapnutiaHry))

    def posunKameryVlavoVpravo(self):
        # VLAVO
        lavaHranica = 80
        pravaHranica = SIRKA_OBRAZOVKY_HRY - lavaHranica
        hornaHranica = VYSKA_OBRAZOVKY_HRY - 200
        if self.poziciaMyskyX < lavaHranica and self.poziciaMyskyY < hornaHranica and self.posunKamery > -10:
            self.posunKamery -= 1

        # VPRAVO
        if self.poziciaMyskyX > pravaHranica and self.poziciaMyskyY < hornaHranica and self.posunKamery < 335:
            self.posunKamery += 1

        # Vypocitanie novej X pozicie
        novaPozicia = (self.posunKamery * RYCHLOST_POSUNU_KAMERY), 0
        self.kameraSprity.move_to(novaPozicia)

    def getPocetHracovychJednotiek(self):
        return len(self.zoznamHracovychJednotiek) + len(self.zoznamJednotiekNaPridanieHrac)

    def getPocetEnemyJednotiek(self):
        return len(self.zoznamNepriatelJednotiek) + len(self.zoznamJednotiekNaPridanieEnemy)

    def pridajDoFormacie(self, novyVojak):
        if novyVojak.nepriatel is False:
            for j in range(len(self.formaciaHracovychJednotiek[0]) - 1, -1, -1):
                for i in range(len(self.formaciaHracovychJednotiek)):
                    if self.formaciaHracovychJednotiek[i][j] is None:
                        self.formaciaHracovychJednotiek[i][j] = novyVojak
                        suradnicaXYFormacia = self.suradniceHracFormacia[i][j]
                        novyVojak.surXIDLE = suradnicaXYFormacia[0]
                        novyVojak.surYIDLE = suradnicaXYFormacia[1]
                        break
                else:
                    continue
                break
        else:
            for j in range(len(self.formaciaNepriatelovychJednotiek[0]) - 1, -1, -1):
                for i in range(len(self.formaciaNepriatelovychJednotiek)):
                    if self.formaciaNepriatelovychJednotiek[i][j] is None:
                        self.formaciaNepriatelovychJednotiek[i][j] = novyVojak
                        suradnicaXYFormacia = self.suradniceNeprFormacia[i][j]
                        novyVojak.surXIDLE = suradnicaXYFormacia[0]
                        novyVojak.surYIDLE = suradnicaXYFormacia[1]
                        break
                else:
                    continue
                break

    """
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
    """

    def pridanieVojaka(self, typJednotky, hracPridava=True):
        if self.getPocetHracovychJednotiek() >= MAXIMALNY_POCET_JEDNOTIEK:
            return
        if (self.getPocetHracovychJednotiek() - self.getPocetKopacov() >= MAXIMALNY_POCET_JEDNOTIEK - MAXIMALNY_POCET_KOPACOV
                and typJednotky != "Krompac"):
            return
        suradnicaY = random.randint(200, 400)
        jednotkaNaPridanie = None
        match typJednotky:
            case "Krompac":
                if hracPridava:
                    if self.getPocetKopacov() < MAXIMALNY_POCET_KOPACOV:
                        if self.pocetHracovhoZlata < CENA_KOPACA:
                            return
                        self.pocetHracovhoZlata -= CENA_KOPACA
                        pridanaJednotka = jednotka.Kopac(SPAWN_SURADNICA_X_HRACA, suradnicaY)
                        self.zapisCasSpawnuAkPrvyNaSpawn()
                        self.zoznamJednotiekNaPridanieHrac.append(pridanaJednotka)
                else:
                    if self.getPocetKopacov(hracovychKopacov=False) < MAXIMALNY_POCET_KOPACOV:
                        if self.pocetEnemyZlata < CENA_KOPACA:
                            return
                        self.pocetEnemyZlata -= CENA_KOPACA
                        pridanaJednotka = jednotka.Kopac(SPAWN_SURADNICA_X_NEPRIATELA, suradnicaY, True)
                        self.zapisCasSpawnuAkPrvyNaSpawn(False)
                        self.zoznamJednotiekNaPridanieEnemy.append(pridanaJednotka)

            case "Mec":
                if hracPridava:
                    if self.pocetHracovhoZlata < CENA_MECIARA:
                        return
                    self.pocetHracovhoZlata -= CENA_MECIARA
                    jednotkaNaPridanie = jednotka.Meciar(SPAWN_SURADNICA_X_HRACA, suradnicaY)
                    self.zapisCasSpawnuAkPrvyNaSpawn()
                    self.zoznamJednotiekNaPridanieHrac.append(jednotkaNaPridanie)
                else:
                    if self.pocetEnemyZlata < CENA_MECIARA:
                        return
                    self.pocetEnemyZlata -= CENA_MECIARA
                    jednotkaNaPridanie = jednotka.Meciar(SPAWN_SURADNICA_X_NEPRIATELA, suradnicaY, True)
                    self.zapisCasSpawnuAkPrvyNaSpawn(False)
                    self.zoznamJednotiekNaPridanieEnemy.append(jednotkaNaPridanie)

            case "Kopija":
                if hracPridava:
                    if self.pocetHracovhoZlata < CENA_KOPIJNIKA:
                        return
                    self.pocetHracovhoZlata -= CENA_KOPIJNIKA
                    jednotkaNaPridanie = jednotka.Kopijnik(SPAWN_SURADNICA_X_HRACA, suradnicaY)
                    self.zapisCasSpawnuAkPrvyNaSpawn()
                    self.zoznamJednotiekNaPridanieHrac.append(jednotkaNaPridanie)
                else:
                    if self.pocetEnemyZlata < CENA_KOPIJNIKA:
                        return
                    self.pocetEnemyZlata -= CENA_KOPIJNIKA
                    jednotkaNaPridanie = jednotka.Kopijnik(SPAWN_SURADNICA_X_NEPRIATELA, suradnicaY, True)
                    self.zapisCasSpawnuAkPrvyNaSpawn(False)
                    self.zoznamJednotiekNaPridanieEnemy.append(jednotkaNaPridanie)

        if jednotkaNaPridanie is not None:
            self.pridajDoFormacie(jednotkaNaPridanie)

    def spawnujJednotky(self):
        aktualnyCas = time.time()
        if len(self.zoznamJednotiekNaPridanieHrac) != 0:
            if aktualnyCas - self.casSpawnuPoslednejJednotkyHrac >= self.casSpawnuJednotkyNaRade():
                jednotkaNaSpawn = self.zoznamJednotiekNaPridanieHrac[0]
                self.zoznamJednotiekNaPridanieHrac.remove(jednotkaNaSpawn)
                jednotkaNaSpawn.nastavNovyRozkaz(self.aktualnyRozkazHrac)
                self.zoznamHracovychJednotiek.append(jednotkaNaSpawn)
                self.casSpawnuPoslednejJednotkyHrac = time.time()

        if len(self.zoznamJednotiekNaPridanieEnemy) != 0:
            if aktualnyCas - self.casSpawnuPoslednejJednotkyEnemy >= self.casSpawnuJednotkyNaRade(False):
                jednotkaNaSpawn = self.zoznamJednotiekNaPridanieEnemy[0]
                self.zoznamJednotiekNaPridanieEnemy.remove(jednotkaNaSpawn)
                jednotkaNaSpawn.nastavNovyRozkaz(self.aktualnyRozkazEnemy)
                self.zoznamNepriatelJednotiek.append(jednotkaNaSpawn)
                self.casSpawnuPoslednejJednotkyEnemy = time.time()

    def casSpawnuJednotkyNaRade(self, hracova=True):
        if hracova:
            jednotkaNaSpawn = self.zoznamJednotiekNaPridanieHrac[0]
        else:
            jednotkaNaSpawn = self.zoznamJednotiekNaPridanieEnemy[0]

        match jednotkaNaSpawn.typJednotky:
            case "Kopac":
                return DLZKA_SPAWNU_KOPACA
            case "Meciar":
                return DLZKA_SPAWNU_MECIARA
            case "Kopijnik":
                return DLZKA_SPAWNU_KOPIJNIKA

    def zapisCasSpawnuAkPrvyNaSpawn(self, hracZoznam=True):
        if hracZoznam and len(self.zoznamJednotiekNaPridanieHrac) == 0:
            self.casSpawnuPoslednejJednotkyHrac = time.time()

        if hracZoznam is False and len(self.zoznamJednotiekNaPridanieEnemy) == 0:
            self.casSpawnuPoslednejJednotkyEnemy = time.time()

    def posunKameru(self, smerPosunutia):
        match smerPosunutia:
            case "PosunVlavo":
                self.posunKamery = -10

            case "PosunVpravo":
                self.posunKamery = 335

    def nastavenieRozkazov(self, rozkaz):
        self.aktualnyRozkazHrac = rozkaz
        for hracovaJednotka in self.zoznamHracovychJednotiek:
            hracovaJednotka.nastavNovyRozkaz(rozkaz)

    def pauzniHru(self, neniPotreba):
        self.window.show_view(Menu.PauseMenu(self))

    def getPocetKopacov(self, hracovychKopacov=True):
        pocetKopacov = 0
        if hracovychKopacov:
            for jednotkaHrac in self.zoznamHracovychJednotiek:
                if isinstance(jednotkaHrac, jednotka.Kopac):
                    pocetKopacov += 1
            for jednotkaHrac in self.zoznamJednotiekNaPridanieHrac:
                if isinstance(jednotkaHrac, jednotka.Kopac):
                    pocetKopacov += 1
            return pocetKopacov
        else:
            for jednotkaEnemy in self.zoznamNepriatelJednotiek:
                if isinstance(jednotkaEnemy, jednotka.Kopac):
                    pocetKopacov += 1
            for jednotkaEnemy in self.zoznamJednotiekNaPridanieEnemy:
                if isinstance(jednotkaEnemy, jednotka.Kopac):
                    pocetKopacov += 1
            return pocetKopacov

    def skontrolujPocetDovezenychVozikovZlata(self):
        zlatoNaPridanieHrac = 0
        for kopac in self.zoznamHracovychJednotiek:
            if isinstance(kopac, jednotka.Kopac):
                zlatoNaPridanieHrac += int(kopac.pocetDovezenehoZlata)
                kopac.pocetDovezenehoZlata = 0
        self.pocetHracovhoZlata += int(zlatoNaPridanieHrac)

        zlatoNaPridanieEnemy = 0
        for kopac in self.zoznamNepriatelJednotiek:
            if isinstance(kopac, jednotka.Kopac):
                zlatoNaPridanieEnemy += int(kopac.pocetDovezenehoZlata)
                kopac.pocetDovezenehoZlata = 0
        self.pocetEnemyZlata += int(zlatoNaPridanieEnemy)

    def vykresliPocetVerbujucichJednotiek(self):
        zoznamPoctuJednotiek = self.getPoctyJednotlivychJednotiekVoVerbovani()
        if zoznamPoctuJednotiek[0] != 0:
            arcade.draw_text(zoznamPoctuJednotiek[0], 58, 670, arcade.color.YELLOW, 20)
        if zoznamPoctuJednotiek[1] != 0:
            arcade.draw_text(zoznamPoctuJednotiek[1], 132, 670, arcade.color.YELLOW, 20)
        if zoznamPoctuJednotiek[2] != 0:
            arcade.draw_text(zoznamPoctuJednotiek[2], 205, 670, arcade.color.YELLOW, 20)

    def getPoctyJednotlivychJednotiekVoVerbovani(self):
        zoznamPoctuJednotiek = []
        pocetKopacov = 0
        pocetMeciarov = 0
        pocetKopijnikov = 0
        for jednotkaHrac in self.zoznamJednotiekNaPridanieHrac:
            if isinstance(jednotkaHrac, jednotka.Kopac):
                pocetKopacov += 1
            if isinstance(jednotkaHrac, jednotka.Meciar):
                pocetMeciarov += 1
            if isinstance(jednotkaHrac, jednotka.Kopijnik):
                pocetKopijnikov += 1
        zoznamPoctuJednotiek.append(pocetKopacov)
        zoznamPoctuJednotiek.append(pocetMeciarov)
        zoznamPoctuJednotiek.append(pocetKopijnikov)
        return zoznamPoctuJednotiek

    def debugPanel(self):
        texturaPozadieTlacidiel = arcade.load_texture("TexturaMenus/spodnyPanel.png")
        arcade.draw_lrwh_rectangle_textured(0, 0, SIRKA_OBRAZOVKY_HRY, 40, texture=texturaPozadieTlacidiel)
        text = (
            f"      Zlato: {self.pocetHracovhoZlata}"
            f"      Jednotky: {self.getPocetHracovychJednotiek()}"
            + " " * 80 +#105
            f"      Cas: {round(time.time() - self.casZapnutiaHry, 2)}"
            f"      Zlato: {self.pocetEnemyZlata}"
            f"      Jednotky: {self.getPocetEnemyJednotiek()}"
        )
        arcade.draw_text(text, 10, 10, arcade.color.BLACK_BEAN, 20)
