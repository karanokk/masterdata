from typing import List


class MCServantItem:
    def __init__(self, storage: List[str]):
        self.storage = storage

    @property
    def id(self) -> int:
        return int(self.storage[0])

    @property
    def star(self) -> int:
        return int(self.storage[1])

    @property
    def name_cn(self) -> str:
        return self.storage[2]

    @property
    def name_jp(self) -> str:
        return self.storage[3]

    @property
    def name_en(self) -> str:
        return self.storage[4]

    @property
    def name_link(self) -> str:
        return self.storage[5]

    @property
    def name_other(self) -> str:
        return self.storage[6]

    @property
    def cost(self) -> int:
        return int(self.storage[7])

    @property
    def faction(self) -> str:
        return self.storage[8]

    @property
    def get(self) -> str:
        return self.storage[9]

    @property
    def hp(self) -> int:
        return int(self.storage[10])

    @property
    def atk(self) -> int:
        return int(self.storage[11])

    @property
    def class_link(self) -> str:
        return self.storage[12]

    @property
    def avatar(self) -> str:
        return self.storage[13]

    @property
    def card1(self) -> str:
        return self.storage[14]

    @property
    def card2(self) -> str:
        return self.storage[15]

    @property
    def card3(self) -> str:
        return self.storage[16]

    @property
    def card4(self) -> str:
        return self.storage[17]

    @property
    def card5(self) -> str:
        return self.storage[18]

    @property
    def np_card(self) -> str:
        return self.storage[19]

    @property
    def np_type(self) -> str:
        return self.storage[20]

    @property
    def class_icon(self) -> str:
        return self.storage[21]

    @property
    def stars_marker(self) -> int:
        return int(self.storage[22])

    @property
    def class_marker(self) -> int:
        return int(self.storage[23])

    @property
    def get_marker(self) -> int:
        return int(self.storage[24])

    @property
    def cards_marker(self) -> int:
        return int(self.storage[25])

    @property
    def npc_marker(self) -> int:
        return int(self.storage[26])

    @property
    def npt_marker(self) -> int:
        return int(self.storage[27])

    @property
    def fac_marker(self) -> int:
        return int(self.storage[28])

    @property
    def sex_marker(self) -> int:
        return int(self.storage[29])

    @property
    def prop1_marker(self) -> int:
        return int(self.storage[30])

    @property
    def prop2_marker(self) -> int:
        return int(self.storage[31])

    @property
    def traits_marker(self) -> int:
        return int(self.storage[32])

    @property
    def sort_atk(self) -> int:
        return int(self.storage[33])

    @property
    def sort_hp(self) -> int:
        return int(self.storage[34])


class MCEssenceCraftItem:
    def __init__(self, storage: List[str]):
        self.storage = storage

    @property
    def id(self) -> int:
        return int(self.storage[0])

    @property
    def star(self) -> int:
        return int(self.storage[1])

    @property
    def star_str(self) -> str:
        return self.storage[2]

    @property
    def name(self) -> str:
        return self.storage[3]

    @property
    def name_link(self) -> str:
        return self.storage[4]

    @property
    def name_other(self) -> str:
        return self.storage[5]

    @property
    def cost(self) -> int:
        return int(self.storage[6])

    @property
    def hp1(self) -> int:
        return int(self.storage[7])

    @property
    def hpmax(self) -> int:
        return int(self.storage[8])

    @property
    def atk1(self) -> int:
        return int(self.storage[9])

    @property
    def atkmax(self) -> int:
        return int(self.storage[10])

    @property
    def des(self) -> str:
        return self.storage[11]

    @property
    def des_max(self) -> str:
        return self.storage[12]

    @property
    def icon(self) -> str:
        return self.storage[13]

    @property
    def icon_eff(self) -> str:
        return self.storage[14]

    @property
    def type_marker(self) -> int:
        return int(self.storage[15])

    @property
    def stars_marker(self) -> int:
        return int(self.storage[16])

    @property
    def stats_marker(self) -> int:
        return int(self.storage[17])

    @property
    def sort_atk(self) -> int:
        return int(self.storage[18])

    @property
    def sort_hp(self) -> int:
        return int(self.storage[19])
