from dice import Dice
from enum import Enum, unique

@unique
class Size(Enum):
    Tiny = 1
    Small = 2
    Medium = 3
    Large = 4
    Huge = 5
    Gargantuan = 6

@unique
class Material(Enum):
    Cloth = 1
    Paper = 2
    Rope = 3
    Crystal = 4
    Glass = 5
    Ice = 6
    Wood = 7
    Bone = 8
    Stone = 9
    Iron = 10
    Steel = 11
    Mithral = 12
    Adamantine = 13
    Gold = 14
    Silver = 15
    Copper = 16
    Food = 17

@unique
class Effects(Enum):
    Damage = 1
    Heal = 2
    Repair = 3

class ATTRIBUTES(object):
    STRENGTH = 1
    DEXTERITY = 2
    CONSITUTION = 3
    INTELLIGENCE = 4
    WISDOM = 5
    CHARISMA = 6
    ### Determined attributes ###
    INITIATIVE = 7 # Used in iniative check (dexterity + initiative bonus)
    ATTACK = 8 #used in attack roll
    DEFENSE = 9 #used in defense (Armor AC)
    THROW = 10 #allows bonus on throw for thief class

    __NAMES = [
        'Strength',
        'Dexterity',
        'Constitution',
        'Intelligence',
        'Wisdom',
        'Charisma',
        'Initiative',
        'Attack',
        'Defense',
        'Throw'
        ]

    @staticmethod
    def get_name(attr): return ATTRIBUTES.__NAMES[attr-1]

class DiceRoll:
    @property
    def roll(self): return self.__roll
    @property
    def modifier(self): return self.__modifier
    @property
    def total(self):
        #Critical roll :(
        if self.__roll == 1:
            return self.__roll
        return self.__roll + self.__modifier

    def __init__(self, roll, modifier):
        self.__roll = roll
        self.__modifier = modifier
           
class GameRules(object):
    """
    Attribute Modifier values
    1-2 −5
    2–3 −4
    4–5 −3
    6–7 −2
    8–9 −1
    10–11 +0
    12–13 +1
    14–15 +2
    16–17 +3
    18–19 +4
    20–21 +5
    22–23 +6
    24–25 +7
    26–27 +8
    28–29 +9
    30 +10
    """
    @staticmethod
    def get_attribute_modifier(score):
        if score>=30: return 10
        if score <= 1: return -5
        return (score // 2) -5

    @staticmethod
    def get_player_defense(player):
        """ base armor class + any modifiers """
        return player.get_equipped_armor().armor_total(player) + player.defense_bonus

    @staticmethod
    def roll_saving_will_throw(player):
        """ Saving throw from unusual/magic attack - mental attack/magical effect """
        dice_roll = Dice.roll(die=1,sides=20) #1d20
        wisdom_modifier = player.wisdom_modifier() + player.character_class.get_spell_save_will(player)
        return DiceRoll(dice_roll, wisdom_modifier)

    @staticmethod
    def roll_saving_spell_throw(spell, target):
        """ Saving throw from effect spell """
        dice_roll = Dice.roll(die=1,sides=20) #1d20
        spell_modifier = 0
        try:
            spell_modifier = target.get_attribute_modifier(spell.saving_throw_attribute)
        except:
            pass
        return DiceRoll(dice_roll, spell_modifier)

    @staticmethod
    def roll_saving_reflex_throw(player):
        """ Saving throw from unusual/magic attack - dodge area attack """
        dice_roll = Dice.roll(die=1,sides=20) #1d20
        dexterity_modifier = player.dexterity_modifier() + player.character_class.get_spell_save_reflex(player)
        return DiceRoll(dice_roll, dexterity_modifier)

    @staticmethod
    def roll_saving_fortitude_throw(player):
        """ Saving throw from unusual/magic attack - physical attack, or vitality/health attack """
        dice_roll = Dice.roll(die=1,sides=20) #1d20
        constitution_modifier = player.constitution_modifier() + player.character_class.get_spell_save_fortitude(player)
        return DiceRoll(dice_roll, constitution_modifier)

    @staticmethod
    def roll_initiative_check(player):
        """ Throw to check who responds first on encounter """
        dice_roll = Dice.roll(die=1,sides=20) #1d20
        dexterity_modifier = GameRules.get_attribute_modifier(player.dexterity)
        iniative_modifier = player.initiative_modifier
        return DiceRoll(dice_roll, dexterity_modifier + iniative_modifier)

    @staticmethod
    def roll_skill_check(player, skill):
        """ Throw to check skill success """
        dice_roll = Dice.roll(die=1,sides=20) #1d20
        skill_modifier = player.get_attribute_modifier(skill.attribute_modifier)
        #Other skill misc. modifier
        return DiceRoll(dice_roll, skill_modifier)

    @staticmethod
    def determine_spell_difficulty_class(spell, player):
        return 10 + spell.level + player.get_spell_proficiency(spell) + spell.get_spell_attack_modifier(player)

    @staticmethod
    def determine_hit_points(dice, sides, bonus):
        return bonus + Dice.roll(dice, sides)

    @staticmethod
    def roll_death_save(player):
        """ Saving throw on death """
        dice_roll = Dice.roll(die=1,sides=20) #1d20
        if dice_roll == 20:
            player.heal(1)
            return True
        elif dice_roll >= 10:
            return True
        return False

    @staticmethod
    def roll_weapon_attack_score(player):
        """ Returns critical_strike, 1D20 + ability modifier + proficiency bonus + any other attack bonus """
        #1d20 + ability_modifier + proficiency_bonus (if proficient) + any special attack bonus (like +1 on a weapon)
        attack_roll = Dice.roll(die=1,sides=20) #1d20
        ability_modifier = player.determine_ability_modifier()
        proficiency_bonus = player.determine_proficiency_bonus()
        other_attack_bonus = player.other_attack_bonus
        return DiceRoll(attack_roll, ability_modifier + proficiency_bonus + other_attack_bonus)

    @staticmethod
    def roll_weapon_throw_score(player):
        """ Returns critical_strike, 1D20 + weapon proficiency + weapon attack modifier """
        attack_roll = Dice.roll(die=1,sides=20) #1d20
        ability_modifier = player.determine_ability_modifier()
        proficiency_bonus = player.determine_proficiency_bonus()
        other_attack_bonus = player.other_attack_bonus + player.determine_throw_bonus()
        return DiceRoll(attack_roll, ability_modifier + proficiency_bonus + other_attack_bonus)

    @staticmethod
    def roll_trap_attack_score(trap):
        """ Returns dice roll (1D20) + trap modifier """
        attack_roll = Dice.roll(die=1,sides=20) #1d20
        trap_modifier = trap.get_attack_modifier()
        return DiceRoll(attack_roll, trap_modifier)
    
    @staticmethod
    def is_thrown_item_lost():
        """50% chance of losing arrow"""
        return Dice.roll(1, 2) == 1

    @staticmethod
    def roll_spell_attack_score(spell, player):
        """ Returns dice roll (1D20) + spell modifier """
        attack_roll = Dice.roll(die=1,sides=20) #1d20
        spell_modifier = spell.get_spell_attack_modifier(player)
        return DiceRoll(attack_roll, spell_modifier)

    @staticmethod
    def determine_carry_capacity(player):
        """Carry capacity"""
        return player.strength * 15

class Level(object):
    LEVELS = {
        #Level: [experience for next level, proficiency bonus]
        1: [300,2],
        2: [900,2],
        3: [2700,2],
        4: [6500,2],
        5: [14000,3],
        6: [23000,3],
        7: [34000,3],
        8: [48000,3],
        9: [64000,4],
        10: [85000,4],
        11: [100000,4],
        12: [120000,4],
        13: [140000,5],
        14: [165000,5],
        15: [195000,5],
        16: [225000,5],
        17: [265000,6],
        18: [305000,6],
        19: [355000,6],
        20: [999999,6]
        }

    @property
    def proficiency_bonus(self): return self.__get_level_obj()[1]
    @property
    def min_experience(self):
        if self.__level == 1: return 0
        return Level.LEVELS[self.__level-1][0]
    @property
    def max_experience(self):
        return Level.LEVELS[self.__level][0]

    def __init__(self):
        self.__level = 1

    def __get_level_obj(self): return Level.LEVELS[self.__level]
    
    
    @property
    def level(self): return self.__level
    @level.setter
    def level(self, value): self.__level = value
    
    @staticmethod
    def get_level_by_exp(exp):
        """Find the right level based on the characters experience"""
        if exp < Level.LEVELS[1][0]: return 1
        if exp >= Level.LEVELS[19][0]: return 20
        min_exp = 0
        for i in range(1,20):
            max_exp = Level.LEVELS[i][0]
            if exp >= min_exp and exp < max_exp: return i
            min_exp = max_exp

