from questgame.game_items import weapons, armor, spells
from questgame.players import skills
from questgame.common.rules import PlayerAttributes

class Class(object):
    """description of class"""
    def __init__(self): pass

    @property
    def spell_attack_attribute(self): return PlayerAttributes.INTELLIGENCE
    def is_weapon_proficient(self, player, weapon): return weapon.__class__ in ClassStats.get_weapons(self, player.level)
    def is_skill_proficient(self, player, skill):
        for sk in ClassStats.get_skills(self, player.level):
            if skill.__class__ == sk or issubclass(skill.__class__, sk): return True
        return False
    def is_armor_proficient(self, player, armor):
        for sk in ClassStats.get_armor(self, player.level):
            if armor.__class__ == sk or issubclass(armor.__class__, sk): return True
        return False
    def get_spells(self, level):
        return ClassStats.get_spells(self, level)

    def knows_spell(self, player, spell):
        for sk in ClassStats.get_spells(self, player.level):
            if spell.__class__ == sk or issubclass(spell.__class__, sk): return True
        return False
    def get_skill_damage(self, skill, level): return ClassStats.get_skills_damage(self, level, skill)

    def get_mana_points(self, player): return ClassStats.get_mana(self, player.level)
    def get_attack_bonus(self, player): return ClassStats.get_attack_bonus(self, player.level)

    def get_spell_save_will(self, player): return ClassStats.get_spell_save(self, player.level)[2]
    def get_spell_save_reflex(self, player): return ClassStats.get_spell_save(self, player.level)[1]
    def get_spell_save_fortitude(self, player): return ClassStats.get_spell_save(self, player.level)[0]

class Thief(Class): pass
class Goblin(Class): pass
class Animal(Class): pass
class Mage(Class): pass
class Ranger(Class): pass
class Fighter(Class): pass

class ClassStats(object):
    _SKILLS = 1
    _SKILLS_DMG = 2
    _ATTACK_BONUS = 3 #Bonus to add to attack roll, more than one value is for multiple attacks
    _ARMOR = 4
    _WEAPONS = 5
    _SPELLS = 6
    _SPELL_SAVE = 7
    _MANA = 8
    _STATS = {
        Thief: {
            1: { _ATTACK_BONUS: [2], _SKILLS_DMG: {skills.SneakAttack: [1,6]},
                _SKILLS: [skills.SneakAttack, skills.LockPicking],
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
        Ranger: {
            1: { _ATTACK_BONUS: [2], _SKILLS_DMG: {skills.CriticalShot: [1,6]},
                _SKILLS: [skills.CriticalShot],
                _ARMOR: [armor.LightArmor],
                _WEAPONS:[weapons.ShortSword, weapons.LongSword, weapons.ShortBow, weapons.LongBow] },
            2: { _ATTACK_BONUS: [2], _SKILLS_DMG: {skills.CriticalShot: [1,6]} },
            3: { _ATTACK_BONUS: [2], _SKILLS_DMG: {skills.CriticalShot: [2,6]} },
            4: { _ATTACK_BONUS: [2], _SKILLS_DMG: {skills.CriticalShot: [2,6]} },
            5: { _ATTACK_BONUS: [3], _SKILLS_DMG: {skills.CriticalShot: [3,6]} },
            6: { _ATTACK_BONUS: [3], _SKILLS_DMG: {skills.CriticalShot: [3,6]} },
            7: { _ATTACK_BONUS: [3], _SKILLS_DMG: {skills.CriticalShot: [4,6]} },
            8: { _ATTACK_BONUS: [3], _SKILLS_DMG: {skills.CriticalShot: [4,6]} },
            9: { _ATTACK_BONUS: [4], _SKILLS_DMG: {skills.CriticalShot: [5,6]} },
            10: { _ATTACK_BONUS: [4], _SKILLS_DMG: {skills.CriticalShot: [5,6]} },
            11: { _ATTACK_BONUS: [4], _SKILLS_DMG: {skills.CriticalShot: [6,6]} },
            12: { _ATTACK_BONUS: [4], _SKILLS_DMG: {skills.CriticalShot: [6,6]} },
            13: { _ATTACK_BONUS: [5], _SKILLS_DMG: {skills.CriticalShot: [7,6]} },
            14: { _ATTACK_BONUS: [5], _SKILLS_DMG: {skills.CriticalShot: [7,6]} },
            15: { _ATTACK_BONUS: [5], _SKILLS_DMG: {skills.CriticalShot: [8,6]} },
            16: { _ATTACK_BONUS: [5], _SKILLS_DMG: {skills.CriticalShot: [8,6]} },
            17: { _ATTACK_BONUS: [6], _SKILLS_DMG: {skills.CriticalShot: [9,6]} },
            18: { _ATTACK_BONUS: [6], _SKILLS_DMG: {skills.CriticalShot: [9,6]} },
            19: { _ATTACK_BONUS: [6], _SKILLS_DMG: {skills.CriticalShot: [10,6]} },
            20: { _ATTACK_BONUS: [6], _SKILLS_DMG: {skills.CriticalShot: [10,6]} }
        },
        Fighter: {
            1: { _ATTACK_BONUS: [2], _SKILLS_DMG: {skills.Berserker: [1,6]},
                _SKILLS: [skills.Berserker],
                _ARMOR: [armor.HeavyArmor],
                _WEAPONS:[weapons.MeleeWeapon] },
            2: { _ATTACK_BONUS: [2], _SKILLS_DMG: {skills.Berserker: [1,6]} },
            3: { _ATTACK_BONUS: [2], _SKILLS_DMG: {skills.Berserker: [2,6]} },
            4: { _ATTACK_BONUS: [2], _SKILLS_DMG: {skills.Berserker: [2,6]} },
            5: { _ATTACK_BONUS: [3], _SKILLS_DMG: {skills.Berserker: [3,6]} },
            6: { _ATTACK_BONUS: [3], _SKILLS_DMG: {skills.Berserker: [3,6]} },
            7: { _ATTACK_BONUS: [3], _SKILLS_DMG: {skills.Berserker: [4,6]} },
            8: { _ATTACK_BONUS: [3], _SKILLS_DMG: {skills.Berserker: [4,6]} },
            9: { _ATTACK_BONUS: [4], _SKILLS_DMG: {skills.Berserker: [5,6]} },
            10: { _ATTACK_BONUS: [4], _SKILLS_DMG: {skills.Berserker: [5,6]} },
            11: { _ATTACK_BONUS: [4], _SKILLS_DMG: {skills.Berserker: [6,6]} },
            12: { _ATTACK_BONUS: [4], _SKILLS_DMG: {skills.Berserker: [6,6]} },
            13: { _ATTACK_BONUS: [5], _SKILLS_DMG: {skills.Berserker: [7,6]} },
            14: { _ATTACK_BONUS: [5], _SKILLS_DMG: {skills.Berserker: [7,6]} },
            15: { _ATTACK_BONUS: [5], _SKILLS_DMG: {skills.Berserker: [8,6]} },
            16: { _ATTACK_BONUS: [5], _SKILLS_DMG: {skills.Berserker: [8,6]} },
            17: { _ATTACK_BONUS: [6], _SKILLS_DMG: {skills.Berserker: [9,6]} },
            18: { _ATTACK_BONUS: [6], _SKILLS_DMG: {skills.Berserker: [9,6]} },
            19: { _ATTACK_BONUS: [6], _SKILLS_DMG: {skills.Berserker: [10,6]} },
            20: { _ATTACK_BONUS: [6], _SKILLS_DMG: {skills.Berserker: [10,6]} }
        },
        Mage: {
            1: { _ATTACK_BONUS: [0], _SPELL_SAVE: [0,0,2], _MANA: 4,
                _SPELLS: [spells.FireballSpell, spells.HealSpell, spells.HarmSpell],
                _ARMOR: [armor.LightArmor],
                _WEAPONS:[weapons.Staff] },
            2: { _ATTACK_BONUS: [1], _SPELL_SAVE: [0,0,3], _MANA: 6},
            3: { _ATTACK_BONUS: [1], _SPELL_SAVE: [1,1,3], _MANA: 8},
            4: { _ATTACK_BONUS: [2], _SPELL_SAVE: [1,1,4], _MANA: 11},
            5: { _ATTACK_BONUS: [2], _SPELL_SAVE: [1,1,4], _MANA: 14},
            6: { _ATTACK_BONUS: [3], _SPELL_SAVE: [2,2,5], _MANA: 18},
            7: { _ATTACK_BONUS: [3], _SPELL_SAVE: [2,2,5], _MANA: 23},
            8: { _ATTACK_BONUS: [4], _SPELL_SAVE: [2,2,6], _MANA: 29},
            9: { _ATTACK_BONUS: [4], _SPELL_SAVE: [3,3,6], _MANA: 36},
            10: { _ATTACK_BONUS: [5], _SPELL_SAVE: [3,3,7], _MANA: 44},
            11: { _ATTACK_BONUS: [5], _SPELL_SAVE: [3,3,7], _MANA: 53},
            12: { _ATTACK_BONUS: [6,1], _SPELL_SAVE: [4,4,8], _MANA: 63},
            13: { _ATTACK_BONUS: [6,1], _SPELL_SAVE: [4,4,8], _MANA: 74},
            14: { _ATTACK_BONUS: [7,2], _SPELL_SAVE: [4,4,9], _MANA: 87},
            15: { _ATTACK_BONUS: [7,2], _SPELL_SAVE: [5,5,9], _MANA: 100},
            16: { _ATTACK_BONUS: [8,3], _SPELL_SAVE: [5,5,10], _MANA: 115},
            17: { _ATTACK_BONUS: [8,3], _SPELL_SAVE: [5,5,10], _MANA: 130},
            18: { _ATTACK_BONUS: [9,4], _SPELL_SAVE: [6,6,11], _MANA: 147},
            19: { _ATTACK_BONUS: [9,4], _SPELL_SAVE: [6,6,11], _MANA: 163},
            20: { _ATTACK_BONUS: [10,5], _SPELL_SAVE: [6,6,12], _MANA: 180},
        },
        Goblin: {
            1: { _ATTACK_BONUS: [0], _ARMOR: [armor.LightArmor], _WEAPONS:[weapons.Dagger] },
            2: { _ATTACK_BONUS: [0] }
        },
        Animal: {
            1: { _ATTACK_BONUS: [0], _ARMOR: [], _WEAPONS:[] },
            2: { _ATTACK_BONUS: [0] }
        }
    }
    @staticmethod
    def get_spell_save(cls, level):
        if ClassStats._SPELL_SAVE in ClassStats._STATS[cls.__class__][level]:
            return ClassStats._STATS[cls.__class__][level][ClassStats._SPELL_SAVE]
        return [0,0,0]
    @staticmethod
    def get_mana(cls, level):
        if ClassStats._MANA in ClassStats._STATS[cls.__class__][level]:
            return ClassStats._STATS[cls.__class__][level][ClassStats._MANA]
        return 0
    @staticmethod
    def get_attack_bonus(cls, level):
        if ClassStats._ATTACK_BONUS in ClassStats._STATS[cls.__class__][level]:
            return ClassStats._STATS[cls.__class__][level][ClassStats._ATTACK_BONUS]
        return [0]
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
