from common.base_classes import Modifiers, BaseStats
from common.rules import ATTRIBUTES
from game_items.items import Item
from common.dice import Dice

class Potion(Item):
    """Spell abstract class"""

    @staticmethod
    def _get_stats(): return PotionStats._STATS

    def __init__(self):
        #Add any inital modifiers
        super(Potion,self).__init__(PotionStats)
    
    def _damage(self, player):
        dice = PotionStats.get_damage_dice(self)
        return Dice.roll_dice(dice[0],dice[1])+dice[2]

    def drink(self, player):
        player.notify_observers('LOG', "{} - drank {}".format(player.class_name, self.class_name))
        mods = self.get_modifiers()
        for id in mods:
            mod = mods[id]
            player.add_modifier(id, mod['key'], mod['value'])
            if mod['value'] > 0:
                player.notify_observers('LOG', "{} {} improved by {}".format(player.class_name, ATTRIBUTES.get_name(mod['key']), mod['value']))
        if PotionStats._DAMAGE in PotionStats._STATS[self.__class__]:
            dmg = self._damage(player)
            if dmg > 0:
                player.wound(dmg)
            else:
                player.heal(-dmg)
            return dmg

class HealingPotion(Potion):
    def _damage(self, player):
        dmg = Potion._damage(self, player)
        if player.is_undead:
            player.notify_observers('LOG', "{} - harmed {}".format(player.class_name, dmg))
            return dmg
        else:
            player.notify_observers('LOG', "{} - healed {}".format(player.class_name, dmg))
            return -dmg

class PowerfulHealingPotion(HealingPotion): pass

class HarmPotion(Potion):
    def _damage(self, player):
        dmg = Potion._damage(self, player)
        if player.is_undead:
            player.notify_observers('LOG', "{} - healed {}".format(player.class_name, dmg))
            return -dmg
        else:
            player.notify_observers('LOG', "{} - harmed {}".format(player.class_name, dmg, self.class_name))
            return dmg

class StrengthPotion(Potion): pass

class PotionStats(BaseStats):
    _AC_CLASS = BaseStats._AC_CLASS
    _WEIGHT = BaseStats._WEIGHT
    _COST = BaseStats._COST
    _NAME = BaseStats._NAME
    _ATTR_MODIFIERS = BaseStats._ATTR_MODIFIERS
    _SKILL_MODIFIERS = BaseStats._SKILL_MODIFIERS
    _DAMAGE = 1

    _STATS = {
        StrengthPotion: { _AC_CLASS:0, _WEIGHT: 0.5, _COST: 5, _ATTR_MODIFIERS: {'BONUS':[ATTRIBUTES.STRENGTH,2]} },
        HealingPotion: { _AC_CLASS:0, _WEIGHT: 0.5, _COST: 5, _DAMAGE: [2,4,2] }, #2d4+2
        HarmPotion: { _AC_CLASS:0, _WEIGHT: 0.5, _COST: 5, _DAMAGE: [2,4,2] }, #2d4+2
        PowerfulHealingPotion: { _AC_CLASS:0, _WEIGHT: 0.5, _COST: 20, _DAMAGE: [4,4,4] }, #4d4+4
        }
    @staticmethod
    def get_damage_dice(potion): return PotionStats._STATS[potion.__class__][PotionStats._DAMAGE]

