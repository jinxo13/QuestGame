from game_items import weapons, armor
import skills
from common.rules import ATTRIBUTES

class Class(object):
    """description of class"""
    def __init__(self): pass

    @property
    def spell_attack_attribute(self): return ATTRIBUTES.INTELLIGENCE

    def is_weapon_proficient(self, player, weapon): return weapon.__class__ in ClassStats.get_weapons(self, player.level)
    def is_skill_proficient(self, player, skill): return skill.__class__ in ClassStats.get_skills(self, player.level)
    def is_armor_proficient(self, player, armor): return armor.__class__ in ClassStats.get_armor(self, player.level)
    def is_spell_proficient(self, player, spell): return spell.__class__ in ClassStats.get_spells(self, player.level)

    def get_skill_damage(self, skill, level): return ClassStats.get_skills_damage(self, level, skill)

    def get_spell_save_will(self, player): return ClassStats.get_spell_save(self, player.level)[2]
    def get_spell_save_reflex(self, player): return ClassStats.get_spell_save(self, player.level)[1]
    def get_spell_save_fortitude(self, player): return ClassStats.get_spell_save(self, player.level)[0]

class Thief(Class): pass
class Goblin(Class): pass
class Mage(Class): pass

class ClassStats(object):
    _SKILLS = 1
    _SKILLS_DMG = 2
    _ATTACK_BONUS = 3
    _ARMOR = 4
    _WEAPONS = 5
    _SPELLS = 6
    _SPELL_SAVE = 7
    _SPELL_SLOTS = 8
    _STATS = {
        Thief: {
            1: { _ATTACK_BONUS: [2], _SKILLS_DMG: {skills.SneakAttack: [1,6]},
                _SKILLS: [skills.SneakAttack],
                _ARMOR: [armor.LightArmor],
                _WEAPONS:[weapons.Dagger,weapons.ShortSword, weapons.LongSword, weapons.ShortBow] },
            2: { _ATTACK_BONUS: [2], _SKILLS_DMG: {skills.SneakAttack: [1,6]} },
            3: { _ATTACK_BONUS: [2], _SKILLS_DMG: {skills.SneakAttack: [2,6]} },
            4: { _ATTACK_BONUS: [2], _SKILLS_DMG: {skills.SneakAttack: [2,6]} },
            5: { _ATTACK_BONUS: [3], _SKILLS_DMG: {skills.SneakAttack: [3,6]} },
            6: { _ATTACK_BONUS: [3], _SKILLS_DMG: {skills.SneakAttack: [3,6]} },
            7: { _ATTACK_BONUS: [3], _SKILLS_DMG: {skills.SneakAttack: [4,6]} },
            8: { _ATTACK_BONUS: [3], _SKILLS_DMG: {skills.SneakAttack: [4,6]} },
            9: { _ATTACK_BONUS: [4], _SKILLS_DMG: {skills.SneakAttack: [5,6]} },
            10: { _ATTACK_BONUS: [4], _SKILLS_DMG: {skills.SneakAttack: [5,6]} },
            11: { _ATTACK_BONUS: [4], _SKILLS_DMG: {skills.SneakAttack: [6,6]} },
            12: { _ATTACK_BONUS: [4], _SKILLS_DMG: {skills.SneakAttack: [6,6]} },
            13: { _ATTACK_BONUS: [5], _SKILLS_DMG: {skills.SneakAttack: [7,6]} },
            14: { _ATTACK_BONUS: [5], _SKILLS_DMG: {skills.SneakAttack: [7,6]} },
            15: { _ATTACK_BONUS: [5], _SKILLS_DMG: {skills.SneakAttack: [8,6]} },
            16: { _ATTACK_BONUS: [5], _SKILLS_DMG: {skills.SneakAttack: [8,6]} },
            17: { _ATTACK_BONUS: [6], _SKILLS_DMG: {skills.SneakAttack: [9,6]} },
            18: { _ATTACK_BONUS: [6], _SKILLS_DMG: {skills.SneakAttack: [9,6]} },
            19: { _ATTACK_BONUS: [6], _SKILLS_DMG: {skills.SneakAttack: [10,6]} },
            20: { _ATTACK_BONUS: [6], _SKILLS_DMG: {skills.SneakAttack: [10,6]} }
        },
        Mage: {
            1: { _ATTACK_BONUS: [0], _SPELL_SAVE: [0,0,2], _SPELL_SLOTS: [1]},
            2: { _ATTACK_BONUS: [1], _SPELL_SAVE: [0,0,3], _SPELL_SLOTS: [2]},
            3: { _ATTACK_BONUS: [1], _SPELL_SAVE: [1,1,3], _SPELL_SLOTS: [2,1]},
            4: { _ATTACK_BONUS: [2], _SPELL_SAVE: [1,1,4], _SPELL_SLOTS: [3,2]},
            5: { _ATTACK_BONUS: [2], _SPELL_SAVE: [1,1,4], _SPELL_SLOTS: [3,2,1]},
            6: { _ATTACK_BONUS: [3], _SPELL_SAVE: [2,2,5], _SPELL_SLOTS: [3,3,2]},
            7: { _ATTACK_BONUS: [3], _SPELL_SAVE: [2,2,5], _SPELL_SLOTS: [4,3,2,1]},
            8: { _ATTACK_BONUS: [4], _SPELL_SAVE: [2,2,6], _SPELL_SLOTS: [4,3,3,2]},
            9: { _ATTACK_BONUS: [4], _SPELL_SAVE: [3,3,6], _SPELL_SLOTS: [4,4,3,2,1]},
            10: { _ATTACK_BONUS: [5], _SPELL_SAVE: [3,3,7], _SPELL_SLOTS: [4,4,3,3,2]},
            11: { _ATTACK_BONUS: [5], _SPELL_SAVE: [3,3,7], _SPELL_SLOTS: [4,4,4,3,2,1]},
            12: { _ATTACK_BONUS: [6,1], _SPELL_SAVE: [4,4,8], _SPELL_SLOTS: [4,4,4,3,3,2]},
            13: { _ATTACK_BONUS: [6,1], _SPELL_SAVE: [4,4,8], _SPELL_SLOTS: [4,4,4,4,3,2,1]},
            14: { _ATTACK_BONUS: [7,2], _SPELL_SAVE: [4,4,9], _SPELL_SLOTS: [4,4,4,4,3,3,2]},
            15: { _ATTACK_BONUS: [7,2], _SPELL_SAVE: [5,5,9], _SPELL_SLOTS: [4,4,4,4,4,3,2,1]},
            16: { _ATTACK_BONUS: [8,3], _SPELL_SAVE: [5,5,10], _SPELL_SLOTS: [4,4,4,4,4,3,3,2]},
            17: { _ATTACK_BONUS: [8,3], _SPELL_SAVE: [5,5,10], _SPELL_SLOTS: [4,4,4,4,4,4,3,2,1]},
            18: { _ATTACK_BONUS: [9,4], _SPELL_SAVE: [6,6,11], _SPELL_SLOTS: [4,4,4,4,4,4,3,3,2]},
            19: { _ATTACK_BONUS: [9,4], _SPELL_SAVE: [6,6,11], _SPELL_SLOTS: [4,4,4,4,4,4,4,3,3]},
            20: { _ATTACK_BONUS: [10,5], _SPELL_SAVE: [6,6,12], _SPELL_SLOTS: [4,4,4,4,4,4,4,4,4]},
        },
        Goblin: {
            1: { _ATTACK_BONUS: [0], _ARMOR: [armor.LightArmor], _WEAPONS:[weapons.Dagger] },
            2: { _ATTACK_BONUS: [0] }
        }
    }
    @staticmethod
    def get_spell_save(cls, level):
        if ClassStats._SPELL_SAVE in ClassStats._STATS[cls.__class__][level]:
            return ClassStats._STATS[cls.__class__][level][ClassStats._SPELL_SAVE]
        return [0,0,0]
    @staticmethod
    def get_spell_slots(cls, level):
        if ClassStats._SPELL_SLOTS in ClassStats._STATS[cls.__class__][level]:
            return ClassStats._STATS[cls.__class__][level][ClassStats._SPELL_SLOTS]
    @staticmethod
    def get_attack_bonus(cls, level): return ClassStats._STATS[cls.__class__][level][ClassStats._ATTACK_BONUS]
    @staticmethod
    def get_skills_damage(cls, level, skill):
        if ClassStats._SKILLS_DMG in ClassStats._STATS[cls.__class__][level]:
            return ClassStats._STATS[cls.__class__][level][ClassStats._SKILLS_DMG][skill.__class__]
        return [0,0]
    @staticmethod
    def get_skills(cls, level): return ClassStats.__get_stats(cls, level, ClassStats._SKILLS)
    @staticmethod
    def get_armor(cls, level): return ClassStats.__get_stats(cls, level, ClassStats._ARMOR)
    @staticmethod
    def get_weapons(cls, level): return ClassStats.__get_stats(cls, level, ClassStats._WEAPONS)
    @staticmethod
    def get_spells(cls, level): return ClassStats.__get_stats(cls, level, ClassStats._SPELLS)
    @staticmethod
    def __get_stats(cls, level, key):
        results = []
        for i in range(level):
            if key in ClassStats._STATS[cls.__class__][i+1]:
                results.extend(ClassStats._STATS[cls.__class__][i+1][key])
        return results
