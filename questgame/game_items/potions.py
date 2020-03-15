from questgame.common.base_classes import Modifiers, BaseStats
from questgame.common.rules import ATTRIBUTES, Effects
from questgame.game_items.items import Drink
from questgame.common.dice import Dice
from questgame.interface.alexa.utils import ReplyHelpers

class Potion(Drink):
    """Potion base class"""

    @staticmethod
    def _get_stats(): return PotionStats

    def __init__(self, count=1):
        #Add any inital modifiers
        super(Potion,self).__init__(count=count, stats=PotionStats)
    
    def _effect(self, action, player):
        mods = self.get_modifiers()
        for id in mods:
            mod = mods[id]
            player.add_modifier(id, mod['key'], mod['value'])
            if mod['value'] > 0:
                player.notify_observers_log("{} {} improved by {}".format(player.class_name, ATTRIBUTES.get_name(mod['key']), mod['value']))

class DamagePotion(Potion):
    
    def _damage(self, target):
        dice = PotionStats.get_damage_dice(self)
        return Dice.roll(dice[0],dice[1])+dice[2]

    def _effect(self, action, target):
        dmg = self._damage(target)
        if dmg > 0:
            target.affect(self, Effects.Damage, dmg)
        else:
            target.affect(self, Effects.Heal, -dmg)
        return dmg


class HealingPotion(DamagePotion):
    def _damage(self, player):
        dmg = DamagePotion._damage(self, player)
        if player.is_undead:
            player.notify_observers_log("{} - harmed {}".format(player.class_name, dmg))
            return dmg
        else:
            player.notify_observers_log("{} - healed {}".format(player.class_name, dmg))
            return -dmg

class PowerfulHealingPotion(HealingPotion): pass

class HarmPotion(DamagePotion):
    def _damage(self, player):
        dmg = DamagePotion._damage(self, player)
        if player.is_undead:
            player.notify_observers_log("{} - healed {}".format(player.class_name, dmg))
            return -dmg
        else:
            player.notify_observers_log("{} - harmed {}".format(player.class_name, dmg))
            return dmg

class StrengthPotion(Potion): pass

class ManaPotion(Potion):
    def _mana(self):
        dice = PotionStats.get_mana_dice(self)
        return Dice.roll(dice[0],dice[1])+dice[2]

    def _effect(self, action, player):
        player.add_mana(self._mana())

class PotionStats(BaseStats):
    _AC_CLASS = BaseStats._AC_CLASS
    _WEIGHT = BaseStats._WEIGHT
    _COST = BaseStats._COST
    _NAME = BaseStats._NAME
    _ATTR_MODIFIERS = BaseStats._ATTR_MODIFIERS
    _SKILL_MODIFIERS = BaseStats._SKILL_MODIFIERS
    _NAME_MATCHES = BaseStats._NAME_MATCHES
    _DAMAGE = 1
    _MANA = 2

    _STATS = {
        StrengthPotion: { _NAME_MATCHES:['strength potion'], _AC_CLASS:0, _WEIGHT: 0.5, _COST: 5, _ATTR_MODIFIERS: {'BONUS':[ATTRIBUTES.STRENGTH,2]} },
        HealingPotion: { _NAME_MATCHES:['healing potion','heal potion'], _AC_CLASS:0, _WEIGHT: 0.5, _COST: 5, _DAMAGE: [2,4,2] }, #2d4+2
        ManaPotion: { _NAME_MATCHES:['mana potion'], _AC_CLASS:0, _WEIGHT: 0.5, _COST: 5, _MANA: [2,4,2] }, #2d4+2
        HarmPotion: { _NAME_MATCHES:['harm potion'], _AC_CLASS:0, _WEIGHT: 0.5, _COST: 5, _DAMAGE: [2,4,2] }, #2d4+2
        PowerfulHealingPotion: { _NAME_MATCHES:['large heal potion','large healing potion'], _AC_CLASS:0, _WEIGHT: 0.5, _COST: 20, _DAMAGE: [4,4,4] }, #4d4+4
        }
    @staticmethod
    def get_damage_dice(potion): return PotionStats._STATS[potion.__class__][PotionStats._DAMAGE]
    @staticmethod
    def get_mana_dice(potion): return PotionStats._STATS[potion.__class__][PotionStats._MANA]

