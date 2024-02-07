import jednotka
from jednotka import AktualnyRozkaz
from enum import Enum
import arcade.gui
from arcade.gui import UIOnClickEvent

# texturaOff, texturaOn, callbackParameter
class TypTlacidla(Enum):
    TLACIDLO_KROMPAC = ("TexturaButton/kromp1.png", "TexturaButton/kromp2.png", "Krompac")
    TLACIDLO_MEC = ("TexturaButton/mec1.png", "TexturaButton/mec2.png", "Mec")
    TLACIDLO_KOPIJA = ("TexturaButton/kopija1.png", "TexturaButton/kopija2.png", "Kopija")
    TLACIDLO_POSUN_VLAVO = ("TexturaButton/vlavo.png", "TexturaButton/vlavo1.png", "PosunVlavo")
    TLACIDLO_POSUN_VPRAVO = ("TexturaButton/vpravo.png", "TexturaButton/vpravo1.png", "PosunVpravo")
    TLACIDLO_PAUZA = ("TexturaButton/pauza.png", "TexturaButton/pauza1.png", "NEMA")
    TLACIDLO_OBRANA = ("TexturaButton/deff.png", "TexturaButton/deff1.png", AktualnyRozkaz.OBRANA) #"Obrana"
    TLACIDLO_IDLE = ("TexturaButton/idle.png", "TexturaButton/idle1.png", AktualnyRozkaz.IDLE) #"Idle"
    TLACIDLO_UTOK = ("TexturaButton/off.png", "TexturaButton/off1.png", AktualnyRozkaz.UTOK) #"Utok"


SIRKA_TLACITKA = 65

class Tlacidlo(arcade.gui.UITextureButton):
    def __init__(self, typTlacidla, callbackMetoda=None):
        super().__init__(
                         width=SIRKA_TLACITKA,
                         height=SIRKA_TLACITKA,
                         texture=arcade.load_texture(typTlacidla.value[0])
                         )
        self.callbackMetoda = callbackMetoda
        self.callbackParameter = typTlacidla.value[2]
        self.texturaNestlacene = typTlacidla.value[0]
        self.texturaStlacene = typTlacidla.value[1]
        if typTlacidla == TypTlacidla.TLACIDLO_IDLE:
            self.texture = arcade.load_texture(self.texturaStlacene)

    def on_click(self, event: UIOnClickEvent):
        if self.callbackMetoda:
            self.callbackMetoda(self.callbackParameter)

    def resetStlacene(self):
        self.texture = arcade.load_texture(self.texturaNestlacene)

    def setStlacene(self):
        self.texture = arcade.load_texture(self.texturaStlacene)
