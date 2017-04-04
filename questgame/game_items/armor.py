from questgame.common.rules import GameRules, ATTRIBUTES
from questgame.common.base_classes import BaseStats
from questgame.game_items.items import Item

class Armor(Item):
    """description of class"""
    @staticmethod
    def _get_stats(): return ArmorStats._STATS

    def __init__(self):
        super(Armor, self).__init__(ArmorStats)

    @property
    def armor_modifier_attribute(self): return None

    def armor_total(self, player):
        mod = player.get_attribute_modifier(self.armor_modifier_attribute)
        return self.armor_class + mod

class LightArmor(Armor):
    def __init__(self):
        super(LightArmor, self).__init__()
    @property
    def armor_modifier_attribute(self): return ATTRIBUTES.DEXTERITY

class BodyArmor(LightArmor): pass
class HeavyArmor(Armor): pass

class ArmorStats(BaseStats):
    _AC_CLASS = BaseStats._AC_CLASS
    _WEIGHT = BaseStats._WEIGHT
    _COST = BaseStats._COST
    _NAME = BaseStats._NAME
    _ATTR_MODIFIERS = BaseStats._ATTR_MODIFIERS
    _SKILL_MODIFIERS = BaseStats._SKILL_MODIFIERS
    _STATS = {
        LightArmor: { _AC_CLASS:11, _WEIGHT: 1, _COST: 5 },
        BodyArmor: { _AC_CLASS:10, _WEIGHT: 0, _COST: 0 },
        HeavyArmor: { _AC_CLASS:13, _WEIGHT: 0, _COST: 0, _ATTR_MODIFIERS: {'PENALTY': [ATTRIBUTES.DEXTERITY, -2]} }
        }
  