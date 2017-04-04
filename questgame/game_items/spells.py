from questgame.common.base_classes import BaseStats, Modifiers
from questgame.common.rules import GameRules, ATTRIBUTES
from questgame.common.dice import Dice

class Spell(Modifiers):
    """Spell abstract class"""

    @staticmethod
    def _get_stats(): return SpellStats._STATS

    @property
    def level(self): return self.__level

    """Roll to attack + spell modifier, Defend with saving spell throw"""
    def get_spell_attack_modifier(self, caster):
        """modifying attribute (normally intelligence)"""
        return caster.get_attribute_modifier(caster.character_class.spell_attack_attribute)

    def __init__(self):
        #Add any inital modifiers
        super(Spell,self).__init__(SpellStats)
        self.__level = SpellStats.get_level(self)
    
    def cast(self, caster, target): raise NotImplementedError()

class HarmfulSpell(Spell):
    @property
    def saving_throw_attribute(self): return ATTRIBUTES.DEXTERITY

    def _damage(self):
        dice = SpellStats.get_damage_dice(self)
        return Dice.roll_dice(dice[0],dice[1])

    def cast(self, caster, target):
        defense_roll, defense_mod = GameRules.roll_saving_spell_throw(self, target)
        attack_roll, attack_mod = GameRules.roll_spell_attack_score(self, caster)

        caster.notify_observers('LOG', "{} - cast {}".format(caster.class_name, self.class_name))
        caster.notify_observers('LOG','Defense: {}({}), Attack: {}({})'.format(defense_roll+defense_mod,defense_roll,attack_roll+attack_mod,attack_roll))

        hit = True
        dmg = 0
        if defense_roll == 20:
            #miss
            hit = False
        elif defense_roll == 1:
            defense_mod = 0
        if hit:
            if attack_roll + attack_mod >= defense_roll + defense_mod:
                #hit
                dmg = self._damage(caster)
        if not hit:
            caster.notify_observers('LOG', "{} - {} missed {}".format(caster.class_name, self.class_name, target.class_name))
        else:
            caster.notify_observers('LOG', "{} {} hit! Damage {}".format(caster.class_name, self.class_name, dmg))
            target.wound(dmg)
            if target.is_dead:
                caster.notify_observers('LOG', "{} - DIED!".format(target.class_name))


class EffectSpell(Spell):
    """Attack spell has a difficulty class, Defend with saving spell throw"""
    
    def spell_difficulty_class(self, caster):
        """ Determines DC saving throw is made against """
        return GameRules.determine_spell_difficulty_class(self, caster)

    @property
    def saving_throw_attribute(self): return ATTRIBUTES.DEXTERITY

    def _effect(self, caster, target):
        """Apply spell effect"""
        raise NotImplementedError()

    def cast(self, caster, target):
        defense_target = self.spell_difficulty_class(caster)
        saving_roll, saving_mod = GameRules.roll_saving_spell_throw(self, target)
        caster.notify_observers('LOG','Defense: {}, Saving: {}({})'.format(defense_target,saving_roll+saving_mod,saving_roll))
        hit = True
        if saving_roll == 20:
            #miss
            hit = False
        elif saving_roll == 1:
            defense_mod = 0
        if hit:
            if saving_roll + saving_mod < defense_target:
                #hit
                self._effect(caster, target)

class MentalSpell(Spell):
    @property
    def saving_throw_attribute(self): return ATTRIBUTES.WISDOM

class OpenSpell(EffectSpell):
    def cast(self, caster, target):
        caster.notify_observers('LOG','{} successfull on {}'.format(self.__class__.__name__,target.__class__.__name__))
        self._effect(caster, target)

    def _effect(self, caster, target):
        target.open(caster)

class CloseSpell(EffectSpell):
    def cast(self, caster, target):
        caster.notify_observers('LOG','{} successfull on {}'.format(self.__class__.__name__,target.__class__.__name__))
        self._effect(caster, target)

    def _effect(self, caster, target):
        target.close(caster)

class UnlockSpell(EffectSpell):
    def cast(self, caster, target):
        resistence = target.spell_resistance
        defense_target = self.spell_difficulty_class(caster)

        if resistence <= defense_target:
            caster.notify_observers('LOG','{} successfull attempt on {}, DC: {}, Resistence: {}'.format(self.__class__.__name__,target.__class__.__name__,defense_target, resistence))
            self._effect(caster, target)            
        else:
            caster.notify_observers('LOG','{} failed attempt on {}, DC: {}, Resistence: {}'.format(self.__class__.__name__,target.__class__.__name__,defense_target, resistence))

    def _effect(self, caster, target):
        target.unlock_with_spell(self, caster)

class LockSpell(UnlockSpell):
    def _effect(self, caster, target):
        target.lock_with_spell(self, caster)

class HarmSpell(EffectSpell):
    @property
    def saving_throw_attribute(self): return ATTRIBUTES.CONSITUTION

    def cast(self, caster, target):
        if target.is_undead:
            HealSpell().cast(caster, target)
        else:
            EffectSpell.cast(self, caster, target)
    
    def _effect(self, caster, target):
        target.wound(10*min(caster.level,15))

class HealSpell(EffectSpell):

    def cast(self, caster, target):
        if target.is_undead:
            HarmSpell().cast(caster, target)
        else:
            self._effect(caster, target)
    
    def _effect(self, caster, target):
        target.heal(10*min(caster.level,15))

class FireballSpell(HarmfulSpell):
    def _damage(self, caster):
        return HarmfulSpell._damage(self) * min(caster.level, 10)

class SpellStats(BaseStats):
    _AC_CLASS = BaseStats._AC_CLASS
    _WEIGHT = BaseStats._WEIGHT
    _COST = BaseStats._COST
    _NAME = BaseStats._NAME
    _ATTR_MODIFIERS = BaseStats._ATTR_MODIFIERS
    _SKILL_MODIFIERS = BaseStats._SKILL_MODIFIERS
    _DAMAGE = 1
    _LEVEL = 2

    _STATS = {
        FireballSpell: { _AC_CLASS:0, _LEVEL:1, _DAMAGE:[1,6], _WEIGHT:0, _COST:'10' },
        OpenSpell: { _AC_CLASS:0, _LEVEL:1, _WEIGHT:0, _COST:'10' },
        CloseSpell: { _AC_CLASS:0, _LEVEL:1, _WEIGHT:0, _COST:'10' },
        UnlockSpell: { _AC_CLASS:0, _LEVEL:1, _WEIGHT:0, _COST:'10' },
        LockSpell: { _AC_CLASS:0, _LEVEL:1, _WEIGHT:0, _COST:'10' },
        HealSpell: { _AC_CLASS:0, _LEVEL:1, _WEIGHT:0, _COST:'10' },
        HarmSpell: { _AC_CLASS:0, _LEVEL:1, _WEIGHT:0, _COST:'10' }
        }
    @staticmethod
    def get_damage_dice(spell): return SpellStats._STATS[spell.__class__][SpellStats._DAMAGE]
    @staticmethod
    def get_level(spell): return SpellStats._STATS[spell.__class__][SpellStats._LEVEL]

