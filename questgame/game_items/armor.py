from questgame.common.rules import GameRules, ATTRIBUTES
from questgame.common.base_classes import BaseStats
from questgame.game_items.items import Item

class Armor(Item):
    """description of class"""
    @staticmethod
    def _get_stats(): return ArmorStats

    def __init__(self, count=1):
        super(Armor, self).__init__(count)

    @property
    def _find_prefix(self):
        """You find a dagger"""
        """You find an axe"""
        """You find an egg"""
        """You find light armor"""
        return ''

    def armor_total(self, player):
        #DD5 rules
        mod = player.get_attribute_modifier(ATTRIBUTES.DEXTERITY)
        return self.armor_class + mod

class LightArmor(Armor):
    def __init__(self, count=1):
        super(LightArmor, self).__init__(count=count)
    @property
    def text_prefix(self): return ''

class BodyArmor(LightArmor): pass
class FurArmor(LightArmor): pass
class HeavyArmor(Armor):
    def armor_total(self, player):
        #DD5 rules, maximum +2 modifier
        mod = min(2, player.get_attribute_modifier(ATTRIBUTES.DEXTERITY))
        return self.armor_class + mod

class Robe(LightArmor): pass

class ArmorStats(BaseStats):
    _AC_CLASS = BaseStats._AC_CLASS
    _WEIGHT = BaseStats._WEIGHT
    _COST = BaseStats._COST
    _NAME = BaseStats._NAME
    _ATTR_MODIFIERS = BaseStats._ATTR_MODIFIERS
    _SKILL_MODIFIERS = BaseStats._SKILL_MODIFIERS
    _NAME_MATCHES = BaseStats._NAME_MATCHES

    _STATS = {
        LightArmor: { _NAME_MATCHES: ['light armor'], _AC_CLASS:11, _WEIGHT: 1, _COST: 5 },
        Robe: { _NAME_MATCHES: ['robe'], _AC_CLASS:11, _WEIGHT: 1, _COST: 5 },
        BodyArmor: { _NAME_MATCHES: ['body armor'], _AC_CLASS:10, _WEIGHT: 0, _COST: 0 },
        FurArmor: { _NAME_MATCHES: ['fur armor'], _AC_CLASS:6, _WEIGHT: 0, _COST: 0 },
        HeavyArmor: { _NAME_MATCHES: ['heavy armor'], _AC_CLASS:13, _WEIGHT: 0, _COST: 0, _ATTR_MODIFIERS: {'PENALTY': [ATTRIBUTES.DEXTERITY, -2]} }
        }
  