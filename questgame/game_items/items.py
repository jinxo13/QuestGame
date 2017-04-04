from questgame.common.rules import ATTRIBUTES, GameRules
from questgame.common.base_classes import Modifiers, BaseStats

class Item(Modifiers):
    def __init__(self, stats=None):
        #Add any inital modifiers
        if stats:
            super(Item,self).__init__(stats)
        else:
            super(Item,self).__init__(ItemStats)
    
    @property
    def armor_class(self): return BaseStats.get_ac_class(self)
    @property
    def weight(self): return BaseStats.get_weight(self)
    @property
    def cost(self): return BaseStats.get_cost(self)

    @staticmethod 
    def _get_stats(): return ItemStats._STATS

class StrengthRing(Item): pass

class Key(Item):
    @property
    def id(self): return self.__id
    def __init__(self, key_id):
        super(Key, self).__init__(None)
        self.__id = key_id

class ItemStats(BaseStats):
    _AC_CLASS = BaseStats._AC_CLASS
    _WEIGHT = BaseStats._WEIGHT
    _COST = BaseStats._COST
    _NAME = BaseStats._NAME
    _ATTR_MODIFIERS = BaseStats._ATTR_MODIFIERS
    _SKILL_MODIFIERS = BaseStats._SKILL_MODIFIERS

    _STATS = {
        StrengthRing: { _AC_CLASS:0, _WEIGHT: 0.1, _COST: 5, _ATTR_MODIFIERS: {'BONUS':[ATTRIBUTES.STRENGTH,2]} },
        Key: { _AC_CLASS:0, _WEIGHT: 0.1, _COST: 0 },
        }
