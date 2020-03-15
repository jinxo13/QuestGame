from questgame.common.rules import ATTRIBUTES, GameRules, Effects
from questgame.common.base_classes import BaseStats
from questgame.game_items.items import Item
from questgame.common.dice import Dice
from questgame.players import skills
from questgame.interface.alexa.utils import ReplyHelpers

class Strike:
    '''
    Immutable class representing a stike
    Includes hit or not, critical strike or not and damage
    '''
    @property
    def is_critical_hit(self): return self.__is_critical and self.__is_hit
    @property
    def is_critical_miss(self): return self.__is_critical and not self.__is_hit
    @property
    def is_hit(self): return self.__is_hit
    @property
    def is_miss(self): return not self.__is_hit
    @property
    def damage(self): return self.__damage
    def __init__(self, is_hit, is_critical, damage=0):
        self.__is_critical = is_critical
        self.__is_hit = is_hit
        self.__damage = damage

class Weapon(Item):
    """Weapon abstract class"""

    @staticmethod
    def _get_stats(): return WeaponStats

    def __init__(self, count=1):
        #Add any inital modifiers
        super(Weapon,self).__init__(count=count)

    @property
    def is_throwable(self): return False
    @property
    def throw_modifier_attribute(self): return ATTRIBUTES.STRENGTH

    def _damage(self, attacker):
        dice = WeaponStats.get_damage_dice(self)
        return Dice.roll(dice[0],dice[1])

    def get_attack_type(self): return WeaponStats.get_attack_type(self)

    def is_critical_strike(self, attack_roll): return attack_roll in WeaponStats.get_critical_hit_range(self)
    def is_critical_miss(self, attack_roll): return attack_roll == 1
    
    def _miss(self, attacker, defender):
        defender_name = defender.__class__.__name__
        attacker_name = attacker.__class__.__name__
        attacker.notify_observers_log("{} - MISSED {}".format(attacker_name, defender_name))

    def throw(self, attacker, defender):
        '''
        Return True if hit, False if missed
        '''
        from questgame.players.players import Player
        if isinstance(defender, Player):
            #throw at player or monster
            return self.strike(attacker, defender, True)
        
        #Otherwise some sort of room item
        item = defender
        attacker.notify_observers_reply('throw_at_item', template=ReplyHelpers.TEMPLATE_ACTION, weapon_text=self.description, item_text=item.description)
        from questgame.rooms import room
        if isinstance(item, Item) or isinstance(item, room.RoomItem):
            is_hit = item.throw_strike(self, attacker)
        else:
            is_hit = False
        return is_hit

    def strike(self, attacker, defender, is_throw=False):
        '''
        Return Strike object
        Representing hiut or miss and damage (and critical of not)
        '''
        player = attacker
        if attacker.is_monster:
            player = defender

        if not self.is_throwable and is_throw:
            player.notify_observers_reply(ReplyHelpers.render_action_template('not_throwable', weapon_text=self.description))
            return False

        defender_name = defender.__class__.__name__
        attacker_name = attacker.__class__.__name__
        defender_ac = defender.get_defense()
        attacker.notify_observers_log("{} - defense {}".format(defender_name, defender_ac))
        if is_throw:
            dice_roll = GameRules.roll_weapon_throw_score(attacker)
        else:
            dice_roll = GameRules.roll_weapon_attack_score(attacker)
        is_critical_strike = self.is_critical_strike(dice_roll.roll)
        is_critical_miss = self.is_critical_miss(dice_roll.roll)
        attacker.notify_observers_log("{} - attack roll: {}({})".format(attacker_name, dice_roll.total, dice_roll.roll))
        strike_type = 'miss'
        if is_critical_miss or dice_roll.total < defender_ac:
            #Miss!
            if is_critical_miss:
                strike_type = 'critical_miss'
            if is_throw: strike_type = 'throw_' + strike_type
            player.notify_observers_reply(ReplyHelpers.render_action_template(attacker.get_reply_key(strike_type), attacker_name=attacker_name, defender_name=defender_name, attack_type=self.get_attack_type()))
            self._miss(attacker, defender)
            return Strike(False, is_critical_miss)

        #Hit
        dmg = 0
        strike_type = 'strike'
        if is_critical_strike:
            dmg = self._critical_strike(attacker)
            strike_type = 'critical_strike'
        else:
            dmg = self._normal_strike(attacker)
        if is_throw:
            strike_type = 'throw_' + strike_type

        attacker.notify_observers_log("{} - damage roll: {}".format(attacker_name, dmg))
        defender.affect(attacker, Effects.Damage, dmg)
        player.notify_observers_reply(ReplyHelpers.render_action_template(player.get_reply_key(strike_type), attacker_name=attacker_name, defender_name=defender_name, damage=dmg, hit_points=defender.hit_points, attack_type=self.get_attack_type()))
        attacker.notify_observers_log("{} - DAMAGED {} {}, {} HP now {}!".format(attacker_name, defender_name, dmg, defender_name, defender.hit_points))
        if defender.is_dead:
            player.notify_observers_reply(
                ReplyHelpers.render_action_template(player.get_reply_key('killed'), attacker_name=attacker_name, defender_name=defender_name))
        return Strike(True, is_critical_strike, dmg)

    def _critical_strike(self, attacker):
        return sum(max(0,attacker.determine_ability_modifier()+self._damage(attacker)) for x in range(self.critical_hit_multiplier))

    def _normal_strike(self, attacker):
        mod = attacker.determine_ability_modifier()
        dmg = self._damage(attacker)
        return max(0,dmg + mod)

    @property
    def critical_hit_multiplier(self): return 2
    @property
    def modifier_attributes(self): return []
    @property
    def min_damage(self):
        dice = WeaponStats.get_damage_dice(self)
        dmg = dice[0]
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
    def is_ranged(self): return False
    @property
    def modifier_attributes(self): return [ATTRIBUTES.STRENGTH]

class MeleeFinessWeapon(Weapon):
    @property
    def is_ranged(self): return False
    @property
    def modifier_attributes(self): return [ATTRIBUTES.STRENGTH, ATTRIBUTES.DEXTERITY]

class RangedWeapon(Weapon):
    def __init__(self, count, ammo_class):
        super(RangedWeapon, self).__init__(count=count)
        self.__ammo_class = ammo_class
        self.__ammo = None
    @property
    def is_ranged(self): return True
    @property
    def modifier_attributes(self): return [ATTRIBUTES.DEXTERITY]
    @property
    def ammo_class(self): return self.__ammo_class
    def ammo_count(self, player):
        if self.__ammo is not None and self.__ammo.count > 0: return self.__ammo.count
        ammo = player.inventory.find_ammo(self.ammo_class)
        if not ammo: return 0
        self.__ammo = ammo
        return ammo.count

    def _normal_strike(self, player):
        if not self.ammo_count(player): return 0
        result = Weapon._normal_strike(self, player)
        #TODO: Arrow could be in body
        player.inventory.remove(self.__ammo.__class__())
        return result

    def _critical_strike(self, player):
        if not self.ammo_count(player): return 0
        result = Weapon._critical_strike(self, player)
        #TODO: Arrow could be in body
        player.inventory.remove(self.__ammo.__class__())
        return result

    def _damage(self, attacker):
        dmg = Weapon._damage(self, attacker)
        dice = WeaponStats.get_ammo_dice(self.__ammo)
        dmg += Dice.roll(dice[0],dice[1])+dice[2]
        return dmg

    def _miss(self, player, defender):
        Weapon._miss(self, player, defender)
        #Drop arrow
        #TODO: Arrow should be left on ground
        if GameRules.is_thrown_item_lost():
            player.inventory.remove(self.__ammo.__class__())
        else:
            player.get_rid_of_one(self.__ammo.__class__())

    def strike(self, attacker, defender, is_throw=False):
        if self.ammo_count(attacker) == 0:
            self.notify_observers_log("{} - weapon {} has no ammo".format(attacker.class_name, self.class_name))
            self.notify_observers_reply(ReplyHelpers.render_action_template('no_ammo', ammo_text=self.ammo_class, weapon_text=self.description))
            return
        super(RangedWeapon, self).strike(attacker, defender, is_throw)

class Bow(RangedWeapon):
    def __init__(self, count=1):
        super(Bow, self).__init__(count=count, ammo_class=Arrow)

#Define weapons, attributes are set via table below
class Arrow(MeleeWeapon): pass
class WoodArrow(Arrow): pass
class IronArrow(Arrow): pass
class SteelArrow(Arrow): pass

class Fists(MeleeWeapon): pass
class Claws(MeleeWeapon): pass

class Dagger(MeleeFinessWeapon):
    @property
    def is_throwable(self): return True

class ThiefsDagger(Dagger): pass
class Rock(MeleeWeapon):
    @property
    def is_throwable(self): return True
class ShortSword(MeleeWeapon): pass
class LongSword(MeleeWeapon): pass
class GreatSword(MeleeWeapon): pass

class Axe(MeleeWeapon): pass
class Mace(MeleeWeapon): pass
class Spear(MeleeWeapon):
    @property
    def is_throwable(self): return True
class TwoHandedAxe(MeleeWeapon): pass

class Staff(MeleeWeapon): pass

class LongBow(Bow): pass
class ShortBow(Bow): pass


class WeaponStats(BaseStats):
    _AC_CLASS = BaseStats._AC_CLASS
    _WEIGHT = BaseStats._WEIGHT
    _COST = BaseStats._COST
    _NAME = BaseStats._NAME
    _ATTR_MODIFIERS = BaseStats._ATTR_MODIFIERS
    _SKILL_MODIFIERS = BaseStats._SKILL_MODIFIERS
    _NAME_MATCHES = BaseStats._NAME_MATCHES
    _DAMAGE = 1
    _CRITICAL_HIT = 2
    _AMMO_DAMAGE = 3
    _ATTACK_TYPE = 4 #Your punch hits the rat. The rat's punch hits you.

    _STATS = {
        Fists: { _ATTACK_TYPE:'punch', _NAME_MATCHES:['fists'], _AC_CLASS:0, _DAMAGE:[1,3], _WEIGHT:0, _COST:0, _CRITICAL_HIT: range(20,21) },
        Claws: { _ATTACK_TYPE:'claws', _NAME_MATCHES:['claws'], _AC_CLASS:0, _DAMAGE:[1,3], _WEIGHT:0, _COST:0, _CRITICAL_HIT: range(20,21) },
        Rock: { _ATTACK_TYPE:'rock', _NAME_MATCHES:['rock'], _AC_CLASS:0, _DAMAGE:[1,2], _WEIGHT:2, _COST:0, _CRITICAL_HIT: range(20,21) },
        WoodArrow: { _ATTACK_TYPE:'arrow', _NAME_MATCHES:['wood arrow'], _AC_CLASS:0, _AMMO_DAMAGE:[0,0,0], _DAMAGE:[1,4], _WEIGHT:2, _COST:0.01, _CRITICAL_HIT: range(20,21), _ATTR_MODIFIERS: {'PENALTY':[ATTRIBUTES.ATTACK,-4]} },
        IronArrow: { _ATTACK_TYPE:'arrow', _NAME_MATCHES:['iron arrow'], _AC_CLASS:0, _AMMO_DAMAGE:[0,0,1], _DAMAGE:[1,5], _WEIGHT:2, _COST:0.05, _CRITICAL_HIT: range(20,21), _ATTR_MODIFIERS: {'PENALTY':[ATTRIBUTES.ATTACK,-4]} },
        SteelArrow: { _ATTACK_TYPE:'arrow', _NAME_MATCHES:['steel arrow'], _AC_CLASS:0, _AMMO_DAMAGE:[0,0,2], _DAMAGE:[1,6], _WEIGHT:2, _COST:0.1, _CRITICAL_HIT: range(20,21), _ATTR_MODIFIERS: {'PENALTY':[ATTRIBUTES.ATTACK,-4]} },
        Dagger: { _ATTACK_TYPE:'dagger', _NAME_MATCHES:['dagger'], _AC_CLASS:0, _DAMAGE:[1,6], _WEIGHT:1, _COST:0.2, _CRITICAL_HIT: range(20,21) },
        Staff: { _ATTACK_TYPE:'staff', _NAME_MATCHES:['staff'], _AC_CLASS:0, _DAMAGE:[1,6], _WEIGHT:1, _COST:0.2, _CRITICAL_HIT: range(20,21) },
        ThiefsDagger: { _ATTACK_TYPE:'dagger', _NAME_MATCHES:['thiefs dagger'], _AC_CLASS:0, _DAMAGE:[1,6], _WEIGHT:1, _COST:0.2, _CRITICAL_HIT: range(20,21), _ATTR_MODIFIERS: {'BONUS':[ATTRIBUTES.DEXTERITY,2]}, _SKILL_MODIFIERS: {'BONUS':[skills.SneakAttack, 1]} },
        ShortSword: { _ATTACK_TYPE:'sword', _NAME_MATCHES:['short sword'], _AC_CLASS:0, _DAMAGE:[1,8], _WEIGHT:2, _COST:5, _CRITICAL_HIT: range(19,21) },
        LongSword: { _ATTACK_TYPE:'sword', _NAME_MATCHES:['long sword'], _AC_CLASS:0, _DAMAGE:[1,10], _WEIGHT:5, _COST:10, _CRITICAL_HIT: range(19,21) },
        GreatSword: { _ATTACK_TYPE:'sword', _NAME_MATCHES:['great sword'], _AC_CLASS:0, _DAMAGE:[1,10], _WEIGHT:5, _COST:10, _CRITICAL_HIT: range(19,21) },
        ShortBow: { _ATTACK_TYPE:'arrow', _NAME_MATCHES:['short bow'], _AC_CLASS:0, _DAMAGE:[1,10], _WEIGHT:5, _COST:10, _CRITICAL_HIT: range(19,21) },
        LongBow: { _ATTACK_TYPE:'arrow', _NAME_MATCHES:['long bow'], _AC_CLASS:0, _DAMAGE:[1,10], _WEIGHT:5, _COST:10, _CRITICAL_HIT: range(19,21) },
        Axe: { _ATTACK_TYPE:'axe', _NAME_MATCHES:['axe'], _AC_CLASS:0, _DAMAGE:[1,8], _WEIGHT:2, _COST:5, _CRITICAL_HIT: range(19,21) },
        Spear: { _ATTACK_TYPE:'spear', _NAME_MATCHES:['spear'], _AC_CLASS:0, _DAMAGE:[1,8], _WEIGHT:2, _COST:5, _CRITICAL_HIT: range(19,21) },
        Mace: { _ATTACK_TYPE:'mace', _NAME_MATCHES:['mace'], _AC_CLASS:0, _DAMAGE:[1,8], _WEIGHT:2, _COST:5, _CRITICAL_HIT: range(19,21) },
        TwoHandedAxe: { _ATTACK_TYPE:'axe', _NAME_MATCHES:['two handed axe'], _AC_CLASS:0, _DAMAGE:[1,8], _WEIGHT:2, _COST:5, _CRITICAL_HIT: range(19,21) },
        }
    @staticmethod
    def get_damage_dice(weapon): return WeaponStats._STATS[weapon.__class__][WeaponStats._DAMAGE]
    @staticmethod
    def get_critical_hit_range(weapon): return WeaponStats._STATS[weapon.__class__][WeaponStats._CRITICAL_HIT]
    @staticmethod
    def get_ammo_dice(weapon): return WeaponStats._STATS[weapon.__class__][WeaponStats._AMMO_DAMAGE]
    @staticmethod
    def get_attack_type(weapon): return WeaponStats._STATS[weapon.__class__][WeaponStats._ATTACK_TYPE]
