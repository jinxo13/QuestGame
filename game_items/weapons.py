from common.rules import ATTRIBUTES, GameRules
from common.base_classes import BaseStats
from game_items.items import Item
from common.dice import Dice
from players import skills

class Weapon(Item):
    """Weapon abstract class"""

    @staticmethod
    def _get_stats(): return WeaponStats._STATS

    def __init__(self):
        #Add any inital modifiers
        super(Weapon,self).__init__(WeaponStats)

    def _damage(self, attacker):
        dice = WeaponStats.get_damage_dice(self)
        return Dice.roll_dice(dice[0],dice[1])

    def is_critical_strike(self, attack_roll): return attack_roll in WeaponStats.get_critical_hit_range(self)
    def is_critical_miss(self, attack_roll): return attack_roll == 1
    
    def _miss(self, attacker, defender):
        defender_name = defender.__class__.__name__
        attacker_name = attacker.__class__.__name__
        attacker.notify_observers('LOG', "{} - MISSED {}".format(attacker_name, defender_name))

    def strike(self, attacker, defender):
        if self.is_ranged and not self.ammo_count(attacker):
            self.notify_observers('LOG', "{} - weapon {} has no ammo".format(attacker.class_name, self.class_name))
            return

        defender_name = defender.__class__.__name__
        attacker_name = attacker.__class__.__name__
        defender_ac = defender.get_armor_class()
        attacker.notify_observers('LOG', "{} - defense {}".format(defender_name, defender_ac))
        dice_roll, atk = GameRules.roll_weapon_attack_score(attacker)
        atk += dice_roll
        is_critical_strike = self.is_critical_strike(dice_roll)
        is_critical_miss = self.is_critical_miss(dice_roll)
        attacker.notify_observers('LOG', "{} - attack roll: {}({})".format(attacker_name, atk, dice_roll))
        if is_critical_miss or atk < defender_ac:
            self._miss(attacker, defender)
            return
        #Hit
        dmg = 0
        if is_critical_strike:
            dmg = self._critical_strike(attacker)
        else:
            dmg = self._normal_strike(attacker)

        attacker.notify_observers('LOG', "{} - damage roll: {}".format(attacker_name, dmg))
        defender.wound(dmg)
        attacker.notify_observers('LOG', "{} - DAMAGED {} {}, {} HP now {}!".format(attacker_name, defender_name, dmg, defender_name, defender.hit_points))
        if defender.is_dead:
            attacker.notify_observers('LOG', "{} - DIED :(".format(defender_name))

    def _critical_strike(self, attacker):
        dmg = 0
        for i in range(self.critical_hit_multiplier):
            dmg += attacker.get_attribute_modifier(self.damage_modifier_attribute)
            dmg += self._damage(attacker)
        return dmg

    def _normal_strike(self, attacker):
        mod = attacker.get_attribute_modifier(self.damage_modifier_attribute)
        dmg = self._damage(attacker)
        return dmg + mod

    @property
    def critical_hit_multiplier(self): return 2
    @property
    def damage_modifier_attribute(self): return None
    @property
    def min_damage(self):
        dmg = WeaponStats.get_damage_dice(self)[0]
        if len(dice) == 3: dmg + dice[2]
        return dmg

    @property
    def max_damage(self):
        dice = WeaponStats.get_damage_dice(self)
        dmg = dice[0]*dice[1]
        if len(dice) == 3: dmg + dice[2]
        return dmg

class MeleeWeapon(Weapon):
    @property
    def is_throwable(self): return True
    @property
    def is_ranged(self): return False
    @property
    def damage_modifier_attribute(self): return ATTRIBUTES.STRENGTH

class RangedWeapon(Weapon):
    def __init__(self, ammo_class):
        super(RangedWeapon, self).__init__()
        self.__ammo_class = ammo_class
        self.__ammo = None
    @property
    def is_throwable(self): return False
    @property
    def is_ranged(self): return True
    @property
    def damage_modifier_attribute(self): return ATTRIBUTES.DEXTERITY
    @property
    def ammo_class(self): return self.__ammo_class
    def ammo_count(self, player):
        if self.__ammo is not None and len(self.__ammo) > 0: return len(self.__ammo)
        ammo = player.inventory.find_ammo(self.ammo_class)
        if not ammo: return 0
        self.__ammo = ammo
        return len(ammo)

    def _normal_strike(self, player):
        if not self.ammo_count(player): return 0
        result = Weapon._normal_strike(self, player)
        player.inventory.remove(self.__ammo[0])
        return result

    def _critical_strike(self, player):
        if not self.ammo_count(player): return 0
        result = Weapon._critical_strike(self, player)
        player.inventory.remove(self.__ammo[0])
        return result

    def _damage(self, attacker):
        dmg = Weapon._damage(self, attacker)
        dice = WeaponStats.get_ammo_dice(self.__ammo[0])
        dmg += Dice.roll_dice(dice[0],dice[1])+dice[2]
        return dmg

    def _miss(self, player, defender):
        Weapon._miss(self, player, defender)
        #Drop arrow
        if GameRules.determine_if_arrow_miss_is_lost():
            player.inventory.remove(self.__ammo[0])
        else:
            player.get_rid_of(self.__ammo[0])

class Bow(RangedWeapon):
    def __init__(self):
        return super(Bow, self).__init__(Arrow)

#Define weapons, attributes are set via table below
class Arrow(MeleeWeapon): pass
class WoodArrow(Arrow): pass
class IronArrow(Arrow): pass
class SteelArrow(Arrow): pass

class Fists(MeleeWeapon): pass
class Dagger(MeleeWeapon): pass
class ThiefsDagger(Dagger): pass
class Rock(MeleeWeapon): pass
class ShortSword(MeleeWeapon): pass
class LongSword(MeleeWeapon): pass

class LongBow(Bow): pass
class ShortBow(Bow): pass


class WeaponStats(BaseStats):
    _AC_CLASS = BaseStats._AC_CLASS
    _WEIGHT = BaseStats._WEIGHT
    _COST = BaseStats._COST
    _NAME = BaseStats._NAME
    _ATTR_MODIFIERS = BaseStats._ATTR_MODIFIERS
    _SKILL_MODIFIERS = BaseStats._SKILL_MODIFIERS
    _DAMAGE = 1
    _CRITICAL_HIT = 2
    _AMMO_DAMAGE = 3

    _STATS = {
        Fists: { _AC_CLASS:0, _DAMAGE:[1,3], _WEIGHT:0, _COST:'0', _CRITICAL_HIT: range(20,21) },
        Rock: { _AC_CLASS:0, _DAMAGE:[1,2], _WEIGHT:2, _COST:'0', _CRITICAL_HIT: range(20,21) },
        WoodArrow: { _AC_CLASS:0, _AMMO_DAMAGE:[0,0,0], _DAMAGE:[1,4], _WEIGHT:2, _COST:'0.01', _CRITICAL_HIT: range(20,21), _ATTR_MODIFIERS: {'PENALTY':[ATTRIBUTES.ATTACK,-4]} },
        IronArrow: { _AC_CLASS:0, _AMMO_DAMAGE:[0,0,1], _DAMAGE:[1,5], _WEIGHT:2, _COST:'0.05', _CRITICAL_HIT: range(20,21), _ATTR_MODIFIERS: {'PENALTY':[ATTRIBUTES.ATTACK,-4]} },
        SteelArrow: { _AC_CLASS:0, _AMMO_DAMAGE:[0,0,2], _DAMAGE:[1,6], _WEIGHT:2, _COST:'0.1', _CRITICAL_HIT: range(20,21), _ATTR_MODIFIERS: {'PENALTY':[ATTRIBUTES.ATTACK,-4]} },
        Dagger: { _AC_CLASS:0, _DAMAGE:[1,6], _WEIGHT:1, _COST:'0.2', _CRITICAL_HIT: range(20,21) },
        ThiefsDagger: { _AC_CLASS:0, _DAMAGE:[1,6], _WEIGHT:1, _COST:'0.2', _CRITICAL_HIT: range(20,21), _ATTR_MODIFIERS: {'BONUS':[ATTRIBUTES.DEXTERITY,2]}, _SKILL_MODIFIERS: {'BONUS':[skills.SneakAttack, 1]} },
        ShortSword: { _AC_CLASS:0, _DAMAGE:[1,8], _WEIGHT:2, _COST:'5', _CRITICAL_HIT: range(19,21) },
        LongSword: { _AC_CLASS:0, _DAMAGE:[1,10], _WEIGHT:5, _COST:'10', _CRITICAL_HIT: range(19,21) },
        ShortBow: { _AC_CLASS:0, _DAMAGE:[1,10], _WEIGHT:5, _COST:'10', _CRITICAL_HIT: range(19,21) },
        LongBow: { _AC_CLASS:0, _DAMAGE:[1,10], _WEIGHT:5, _COST:'10', _CRITICAL_HIT: range(19,21) },
        }
    @staticmethod
    def get_damage_dice(weapon): return WeaponStats._STATS[weapon.__class__][WeaponStats._DAMAGE]
    @staticmethod
    def get_critical_hit_range(weapon): return WeaponStats._STATS[weapon.__class__][WeaponStats._CRITICAL_HIT]
    @staticmethod
    def get_ammo_dice(weapon): return WeaponStats._STATS[weapon.__class__][WeaponStats._AMMO_DAMAGE]
