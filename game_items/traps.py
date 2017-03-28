from common.rules import ATTRIBUTES, GameRules
from common.base_classes import Modifiers, BaseStats
from game_items.items import Item
from game_items import spells
from common.dice import Dice

class Trap(Item):
    """ Abstract Mechanical Trap """
    @staticmethod
    def _get_stats(): return TrapStats._STATS

    @property
    def is_armed(self): return self.__is_armed
    @property
    def min_damage(self): return TrapStats.get_damage_dice(self)+TrapStats.get_damage_bonus(self)
    @property
    def max_damage(self): return TrapStats.get_damage_dice(self) * TrapStats.get_damage_sides(self)+TrapStats.get_damage_bonus(self)
    @property
    def critical_hit_multiplier(self): return 1

    def __init__(self):
        super(Trap, self).__init__(TrapStats)
        self.__is_armed = True

    def reset(self): self.__is_armed = True

    def _damage(self, player):
        dice = TrapStats.get_damage_dice(self)
        sides = TrapStats.get_damage_sides(self)
        bonus = TrapStats.get_damage_bonus(self)
        return Dice.roll_dice(dice,sides) + bonus

    def is_critical_strike(self, attack_roll): return attack_roll in TrapStats.get_critical_hit_range(self)
    def is_critical_miss(self, attack_roll): return attack_roll == 1
    
    def critical_strike(self, player):
        dmg = 0
        for i in range(self.critical_hit_multiplier):
            dmg += self.normal_strike(player)
        return dmg

    def normal_strike(self, player):
        dmg = self._damage(player)
        return dmg

    def get_attack_modifier(self):
        return TrapStats.get_attack_modifier(self)

    def disarm(self, player):
        #TODO: Roll
        self.__armed = False

    def _defense(self, player):
        return player.get_armor_class(), 0, False

    def trigger(self, player):
        player.notify_observers('LOG','{} triggered'.format(self.__class__.__name__))
        if not self.is_armed: return
        defense_roll, defense_mod, defense_roll_check = self._defense(player)
        attack_roll, attack_mod = GameRules.roll_trap_attack_score(self)
        dmg = 0
        hit = True
        if defense_roll_check:
            if defense_roll == 20:
                hit = False
            elif defense_roll == 1:
                defense_mod = 0
        if hit:
            if self.is_critical_strike(attack_roll):
                #hit
                dmg = self.critical_strike(player)
            elif self.is_critical_miss(attack_roll):
                #miss
                dmg = 0
            elif attack_roll + attack_mod > defense_roll + defense_mod:
                #hit
                dmg = self.normal_strike(player)
            else:
                #miss
                pass
        player.wound(dmg)
        self.__is_armed = False
        return dmg

class SpellTrap(Trap):
    def __init__(self):
        super(SpellTrap, self).__init__()
        self.__spell = TrapStats.get_spell(self)
    
    def _defense(self, player):
        a,b = GameRules.roll_saving_spell_throw(self.__spell, player)
        return a,b,True

    def _damage(self, player):
        return self.__spell._damage(player)

class SpikeTrap(Trap): pass
class FireballTrap(SpellTrap): pass

class TrapStats(BaseStats):
    _AC_CLASS = BaseStats._AC_CLASS
    _WEIGHT = BaseStats._WEIGHT
    _COST = BaseStats._COST
    _NAME = BaseStats._NAME
    _ATTR_MODIFIERS = BaseStats._ATTR_MODIFIERS
    _SKILL_MODIFIERS = BaseStats._SKILL_MODIFIERS
    _DAMAGE = 1
    _CRITICAL_HIT = 2
    _SPELL = 3
    _ATTACK_MODIFER = 4

    _STATS = {
        SpikeTrap: { _AC_CLASS:0, _WEIGHT: 1, _COST: 10, _DAMAGE: [1,4,3], _ATTACK_MODIFER: 3, _CRITICAL_HIT: range(20,21) },
        FireballTrap: { _AC_CLASS:0, _WEIGHT: 1, _COST: 10, _SPELL: spells.FireballSpell, _ATTACK_MODIFER: 3, _CRITICAL_HIT: range(20,21) },
        }

    @staticmethod
    def get_damage_dice(trap): return TrapStats._STATS[trap.__class__][TrapStats._DAMAGE][0]
    @staticmethod
    def get_damage_sides(trap): return TrapStats._STATS[trap.__class__][TrapStats._DAMAGE][1]
    @staticmethod
    def get_damage_bonus(trap): return TrapStats._STATS[trap.__class__][TrapStats._DAMAGE][2]
    @staticmethod
    def get_attack_modifier(trap): return TrapStats._STATS[trap.__class__][TrapStats._ATTACK_MODIFER]
    @staticmethod
    def get_critical_hit_range(trap): return TrapStats._STATS[trap.__class__][TrapStats._CRITICAL_HIT]
    @staticmethod
    def get_spell(trap):
        if TrapStats._SPELL in TrapStats._STATS[trap.__class__]:
            #Create spell object and return it
            return TrapStats._STATS[trap.__class__][TrapStats._SPELL]()
        else:
            return None
