from questgame.common.base_classes import BaseStats, Bonuses, Serializable
from questgame.common.rules import GameRules, PlayerAttributes, Effects
from questgame.common.dice import Dice
from questgame.common.utils import Helpers
from questgame.interface.alexa.utils import ReplyHelpers

class Spell(Bonuses, Serializable):
    """Spell abstract class"""

    @staticmethod
    def _get_stats(): return SpellStats

    @property
    def level(self): return self.__level

    @property
    def description(self): return BaseStats.get_matches(self)[0]

    """Roll to attack + spell modifier, Defend with saving spell throw"""
    def get_spell_attack_modifier(self, caster):
        """modifying attribute (normally intelligence)"""
        return caster.get_attribute_modifier(caster.character_class.spell_attack_attribute)

    def __init__(self):
        #Add any inital modifiers
        super(Spell,self).__init__(SpellStats)
        self.__level = SpellStats.get_level(self)
    
    def cast(self, caster, target):
        if not caster.can_cast_spell(self):
            return False
        caster.add_mana(-self.level)
        if self._hit(caster, target):
            self._effect(caster, target)
        return True

    def _hit(self, caster, target):
        return True

    def _effect(self, caster, target):
        raise NotImplementedError()

    def is_match(self, text):
        if text is None: return False
        for match in BaseStats.get_matches(self):
            if text.lower() == match or text.lower() == match+'s':
                return True
        return False

class DamageSpell(Spell):
    @property
    def saving_throw_attribute(self): return PlayerAttributes.DEXTERITY

    def _damage(self, caster):
        dice = SpellStats.get_damage_dice(self)
        return Dice.roll(dice[0],dice[1])

    def _hit(self, caster, target):
        defense_roll = GameRules.roll_saving_spell_throw(self, target)
        attack_roll = GameRules.roll_spell_attack_score(self, caster)
        caster.notify_observers_log("{} - cast {}".format(caster.class_name, self.class_name))
        caster.notify_observers_log('Defense: {}({}), Attack: {}({})'.format(defense_roll.total,defense_roll.roll,attack_roll.total,attack_roll.roll))

        hit = defense_roll.roll < 20 and attack_roll.total >= defense_roll.total
        if not hit:
            caster.notify_observers_log("{} - {} missed {}".format(caster.class_name, self.class_name, target.class_name))
            caster.notify_observers_reply(ReplyHelpers.render_action_template(caster.get_reply_key('cast_miss'), spell_text=self.description,
                attacker_name=caster.name, defender_name=target.name, mana_points=caster.mana_points))
        return hit

    def _effect(self, caster, target):
        dmg = self._damage(caster)
        if dmg == 0:
            caster.notify_observers_reply(ReplyHelpers.render_action_template(caster.get_reply_key('cast_defend'), spell_text=self.description,
                attacker_name=caster.name, defender_name=target.name, damage=dmg, hit_points=target.hit_points, mana_points=caster.mana_points))
        else:
            caster.notify_observers_log("{} {} hit! Damage {}".format(caster.class_name, self.class_name, dmg))
            caster.notify_observers_reply(ReplyHelpers.render_action_template(caster.get_reply_key('cast_hit'), spell_text=self.description,
                attacker_name=caster.name, defender_name=target.name, damage=dmg, hit_points=target.hit_points, mana_points=caster.mana_points))
            target.affect(self, Effects.Damage, dmg)

class FireballSpell(DamageSpell):
    def _damage(self, caster):
        return DamageSpell._damage(self, caster) * min(caster.level, 10)

class EffectSpell(Spell):
    """Attack spell has a difficulty class, Defend with saving spell throw"""
    
    def spell_difficulty_class(self, caster):
        """ Determines DC saving throw is made against """
        return GameRules.determine_spell_difficulty_class(self, caster)

    @property
    def saving_throw_attribute(self): return PlayerAttributes.DEXTERITY

    def _hit(self, caster, target):
        #If casting on one self it always hits
        if caster == target: return True
        defense_target = self.spell_difficulty_class(caster)
        saving_roll = GameRules.roll_saving_spell_throw(self, target)
        from questgame.players.players import Player
        if isinstance(target, Player):
            save = saving_roll.total
            caster.notify_observers_log('Defense: {}, Saving: {}({})'.format(defense_target, saving_roll.total, saving_roll.roll))
        else:
            save = target.spell_resistance
            caster.notify_observers_log('Defense: {}, Saving: {}'.format(defense_target, save))
        hit = save < 20 and save <= defense_target
        if not hit:
            caster.notify_observers_log('{} failed on {}'.format(self.__class__.__name__,target.__class__.__name__))
        return hit

class MentalSpell(Spell):
    @property
    def saving_throw_attribute(self): return PlayerAttributes.WISDOM

class OpenSpell(EffectSpell):
    def _effect(self, caster, target):
        target.open(caster, spell=self)

class CloseSpell(EffectSpell):
    def _effect(self, caster, target):
        target.close(caster, spell=self)

class UnlockSpell(EffectSpell):
    def _effect(self, caster, target):
        target.unlock(caster, spell=self)

class LockSpell(UnlockSpell):
    def _effect(self, caster, target):
        target.lock(caster, spell=self)

class HarmSpell(EffectSpell):
    @property
    def saving_throw_attribute(self): return PlayerAttributes.CONSITUTION

    def _effect(self, caster, target):
        if target.is_undead:
            target.affect(self, Effects.Heal, 10*min(caster.level,15))
        else:
            target.affect(self, Effects.Damage, 10*min(caster.level,15))

class HealSpell(EffectSpell):
    def _effect(self, caster, target):
        if target.is_undead:
            target.wound(10*min(caster.level,15))
        else:
            target.heal(10*min(caster.level,15))

class SpellStats(BaseStats):
    _ARMOR_CLASS = BaseStats._ARMOR_CLASS
    _WEIGHT = BaseStats._WEIGHT
    _COST = BaseStats._COST
    _NAME = BaseStats._NAME
    _ATTR_MODIFIERS = BaseStats._ATTR_MODIFIERS
    _SKILL_MODIFIERS = BaseStats._SKILL_MODIFIERS
    _NAME_MATCHES = BaseStats._NAME_MATCHES
    _DAMAGE = 1
    _LEVEL = 2

    _STATS = {
        FireballSpell: { _NAME_MATCHES: ['fireball','fireball spell'], _ARMOR_CLASS:0, _LEVEL:1, _DAMAGE:[1,6], _WEIGHT:0, _COST:'10' },
        OpenSpell: { _NAME_MATCHES: ['open','open spell'], _ARMOR_CLASS:0, _LEVEL:1, _WEIGHT:0, _COST:'10' },
        CloseSpell: { _NAME_MATCHES: ['close','close spell'], _ARMOR_CLASS:0, _LEVEL:1, _WEIGHT:0, _COST:'10' },
        UnlockSpell: { _NAME_MATCHES: ['unlock','unlock spell'], _ARMOR_CLASS:0, _LEVEL:1, _WEIGHT:0, _COST:'10' },
        LockSpell: { _NAME_MATCHES: ['lock','lock spell'], _ARMOR_CLASS:0, _LEVEL:1, _WEIGHT:0, _COST:'10' },
        HealSpell: { _NAME_MATCHES: ['heal','heal spell'], _ARMOR_CLASS:0, _LEVEL:1, _WEIGHT:0, _COST:'10' },
        HarmSpell: { _NAME_MATCHES: ['harm','harm spell'], _ARMOR_CLASS:0, _LEVEL:1, _WEIGHT:0, _COST:'10' }
        }
    @staticmethod
    def get_damage_dice(spell): return SpellStats._STATS[spell.__class__][SpellStats._DAMAGE]
    @staticmethod
    def get_level(spell): return SpellStats._STATS[spell.__class__][SpellStats._LEVEL]

    @staticmethod
    def get_spell_by_text(spell_text):
        return next((spell_cls() for spell_cls in SpellStats._STATS.keys() if spell_cls().is_match(spell_text)), False)

        # for key in SpellStats._STATS.keys():
        #     spell = key()
        #     if spell.is_match(spell_text):
        #         return spell
        # return None