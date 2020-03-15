from questgame.common.rules import ATTRIBUTES, GameRules, Effects
from questgame.common.base_classes import Modifiers, BaseStats
from questgame.game_items.items import Item
from questgame.game_items import spells
from questgame.common.dice import Dice

class Trap(Item):
    """ Abstract Mechanical Trap """
    @staticmethod
    def _get_stats(): return TrapStats

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
        return Dice.roll(dice,sides) + bonus

    def is_critical_strike(self, attack_roll): return attack_roll in TrapStats.get_critical_hit_range(self)
    def is_critical_miss(self, attack_roll): return attack_roll == 1
    
    def critical_strike(self, player):
        return sum(self.normal_strike(player) for x in range(self.critical_hit_multiplier))

    def normal_strike(self, player):
        dmg = self._damage(player)
        return dmg

    def get_attack_modifier(self):
        return TrapStats.get_attack_modifier(self)

    def disarm(self, player):
        #TODO: Roll
        self.__armed = False

    def _defense(self, player):
        return player.get_defense(), 0, False

    def trigger(self, player):
        player.notify_observers_log('{} triggered'.format(self.__class__.__name__))
        if not self.is_armed: return
        defense_roll, defense_mod, defense_roll_check = self._defense(player)
        attack_roll = GameRules.roll_trap_attack_score(self)
        dmg = 0
        hit = True
        if defense_roll_check:
            if defense_roll == 20:
                hit = False
            elif defense_roll == 1:
                defense_mod = 0
        if hit:
            if self.is_critical_strike(attack_roll.roll):
                #hit
                dmg = self.critical_strike(player)
            elif self.is_critical_miss(attack_roll.roll):
                #miss
                dmg = 0
            elif attack_roll.total > defense_roll + defense_mod:
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
        dice_roll = GameRules.roll_saving_spell_throw(self.__spell, player)
        return dice_roll.roll, dice_roll.modifier,True

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
    _NAME_MATCHES = BaseStats._NAME_MATCHES
    _DAMAGE = 1
    _CRITICAL_HIT = 2
    _SPELL = 3
    _ATTACK_MODIFER = 4

    _STATS = {
        SpikeTrap: { _NAME_MATCHES: ['spike trap'], _AC_CLASS:0, _WEIGHT: 1, _COST: 10, _DAMAGE: [1,4,3], _ATTACK_MODIFER: 3, _CRITICAL_HIT: range(20,21) },
        FireballTrap: { _NAME_MATCHES: ['fireball trap'], _AC_CLASS:0, _WEIGHT: 1, _COST: 10, _SPELL: spells.FireballSpell, _ATTACK_MODIFER: 3, _CRITICAL_HIT: range(20,21) },
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
