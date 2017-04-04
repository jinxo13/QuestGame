from questgame.game_items import armor, weapons
import character_classes
from questgame.common.rules import ATTRIBUTES, Level, GameRules
from questgame.common.base_classes import Modifiers, BaseStats, Observable
from questgame.game_items.standard_items import Inventory
from questgame.common.utils import Helpers
import json

class Player(Modifiers, Observable):
    
    @staticmethod
    def create_from_state(state):
        cls = Helpers.class_for_name('questgame.players.character_classes',state['character_class'])
        inst = Player(cls())
        inst.__attributes = state['attributes']
        return inst

    def get_state(self):
        result = {}
        result['character_class'] = self.character_class.__class__.__name__
        result['attributes'] = json.dumps(self.__attributes)
        return result

    @property
    def dexterity(self): return self.get_attribute_current(ATTRIBUTES.DEXTERITY)
    @property
    def strength(self): return self.get_attribute_current(ATTRIBUTES.STRENGTH)
    @property
    def intelligence(self): return self.get_attribute_current(ATTRIBUTES.INTELLIGENCE)
    @property
    def constitution(self): return self.get_attribute_current(ATTRIBUTES.CONSITUTION)
    @property
    def charisma(self): return self.get_attribute_current(ATTRIBUTES.CHARISMA)
    @property
    def wisdom(self): return self.get_attribute_current(ATTRIBUTES.WISDOM)

    @property
    def carry_capacity(self): return GameRules.determine_carry_capacity(self)
    @property
    def carry_weight(self): return self.__inventory.weight

    @property
    def inventory(self): return self.__inventory

    @property
    def strength_base(self): return self.get_attribute_base(ATTRIBUTES.STRENGTH)
    @strength_base.setter
    def strength_base(self, value): self.__attributes[ATTRIBUTES.STRENGTH] = value
    @property
    def dexterity_base(self):  return self.get_attribute_base(ATTRIBUTES.DEXTERITY)
    @dexterity_base.setter
    def dexterity_base(self, value): self.__attributes[ATTRIBUTES.DEXTERITY] = value
    @property
    def constitution_base(self):  return self.get_attribute_base(ATTRIBUTES.CONSITUTION)
    @constitution_base.setter
    def constitution_base(self, value): self.__attributes[ATTRIBUTES.CONSITUTION] = value
    @property
    def intelligence_base(self):  return self.get_attribute_base(ATTRIBUTES.INTELLIGENCE)
    @intelligence_base.setter
    def intelligence_base(self, value): self.__attributes[ATTRIBUTES.INTELLIGENCE] = value
    @property
    def wisdom_base(self): return self.get_attribute_base(ATTRIBUTES.WISDOM)
    @wisdom_base.setter
    def wisdom_base(self, value): self.__attributes[ATTRIBUTES.WISDOM] = value
    @property
    def charisma_base(self): return self.get_attribute_base(ATTRIBUTES.CHARISMA)
    @charisma_base.setter
    def charisma_base(self, value): self.__attributes[ATTRIBUTES.CHARISMA] = value

    def get_attribute_base(self,attr): return self.__attributes[attr]
    def get_attribute_current(self,attr): return self.get_attribute_base(attr) + self.__get_modifiers(attr)

    ### Returns the modifier based on the attribute score
    def get_attribute_modifier(self, attr):
        if attr is None: return 0
        return GameRules.get_attribute_modifier(self.get_attribute_current(attr))

    ### Modifiers based on equiped items
    def attack_modifier(self): return self.get_attribute_modifier(self.get_equipped_weapon().damage_modifier_attribute)
    def damage_modifier(self): return self.attack_modifier()

    def initiative_modifier(self): return self.__get_modifiers(ATTRIBUTES.INITIATIVE)
    def defense_bonus(self): return self.__get_modifiers(ATTRIBUTES.DEFENSE)
    def attack_bonus(self): return self.__get_modifiers(ATTRIBUTES.ATTACK)

    def wisdom_modifier(self): return self.__get_modifiers(ATTRIBUTES.WISDOM)
    def dexterity_modifier(self): return self.__get_modifiers(ATTRIBUTES.DEXTERITY)
    def constitution_modifier(self): return self.__get_modifiers(ATTRIBUTES.CONSITUTION)

    @property
    def is_dead(self): return self.__is_dead
    @property
    def is_unconscious(self): return not self.is_dead and self.hit_points == 0
    @property
    def is_stunned(self): return self.__is_stunned
    @property
    def can_act(self): return not self.is_stunned and not self.is_dead and not self.is_unconscious
    @property
    def is_undead(self): return False

    @property
    def is_encumbered(self): return self.carry_weight > self.carry_capacity

    @property
    def character_class(self): return self.__character_class
    
    ## Hit points
    @property
    def max_hit_points(self): return self.__max_hit_points
    @max_hit_points.setter
    def max_hit_points(self, value):
        delta = value - self.__max_hit_points
        self.__max_hit_points = value
        self.__set_hit_points(self.hit_points + delta)
    @property
    def hit_points(self): return self.__hit_points
    def __set_hit_points(self, value):
        self.__hit_points = min(max(0,value),self.max_hit_points)

    def wound(self, points):
        self.notify_observers('LOG', "{} wounded {}".format(self.__class__.__name__,points))
        if points == 0: return
        if (self.hit_points - points) <= 0: self.__is_dead = True
        self.__set_hit_points(self.hit_points - points)

    def heal(self, points): self.__set_hit_points(self.hit_points + points)

    def throw(self, item, target):
        if self.__inventory().remove(item):
            w = self.get_equipped_weapon()
            if not w.is_throwable():
                self.notify_observers('LOG', "{} - weapon {} is not throwable".format(self.class_name, w.class_name))
                return
            self.strike(target)
            #The weapon is gone!
            self.equip_weapon(None)

    def strike(self, defender):
        defender_name = defender.__class__.__name__
        attacker_name = self.__class__.__name__

        if not self.can_act:
            self.notify_observers('LOG', "{} - stunned, unconscious or dead - can't attack".format(attacker_name))
            return

        self.get_equipped_weapon().strike(self, defender)

    def cast(self, spell, defender):
        #if not self.character_class.is_skill_proficient(skill.__class__):
        #    self.notify_observers('LOG', "{} - isn't proficient in this skill - can't attack".format(attacker_name))
        #    return
        spell.cast(self, defender)

    def drink_potion(self, potion):
        if not self.inventory.contains(potion):
            self.notify_observers('LOG', "{} - doesn't have potion {}".format(self.class_name, potion.class_name))
            return
        potion.drink(self)
        self.get_rid_of(potion)

    def skill_attack(self, skill, defender):
        defender_name = defender.__class__.__name__
        attacker_name = self.__class__.__name__
        if not self.character_class.is_skill_proficient(self, skill.__class__):
            self.notify_observers('LOG', "{} - isn't proficient in this skill - can't attack".format(attacker_name))
            return

        dmg = skill.damage(self)
        self.notify_observers('LOG', "{} - used skill {}! Damage {}".format(attacker_name, skill.__class__.__name__, dmg))
        defender.wound(dmg)
        if defender.is_dead:
            self.notify_observers('LOG', "{} - DIED!".format(defender_name))

    @property
    def level(self): return self.__level.level
    @level.setter
    def level(self, value): self.__level.level = value
    @property
    def proficiency(self): return self.__level.proficiency
    def equip_weapon(self,weapon):
        if weapon is None: weapon = weapons.Fists()
        self.__weapon = weapon
    def equip_armor(self, armor):
        self.__armor = armor

    def __init__(self, character_class):
        super(Player,self).__init__(None)
        Observable.__init__(self)
        self.__hit_points = 0
        self.__max_hit_points = 0
        self.__attributes = {}
        self.__weapon = weapons.Fists()
        self.__armor = armor.BodyArmor()
        self.__character_class = character_class
        self.__experience = 0
        self.__level = Level()
        self.__is_stunned = False
        self.__is_dead = False
        self.__inventory = Inventory(self)
        a = self.__attributes
        a[ATTRIBUTES.STRENGTH] = 0
        a[ATTRIBUTES.DEXTERITY] = 0
        a[ATTRIBUTES.CONSITUTION] = 0
        a[ATTRIBUTES.INTELLIGENCE] = 0
        a[ATTRIBUTES.WISDOM] = 0
        a[ATTRIBUTES.CHARISMA] = 0

    def __get_set_attribute(self, attr, value=None):
        if value: self.__attributes[attr] = value
        return self.__attributes[attr]

    def __get_modifiers(self,attr):
        val = 0
        #player modifiers
        val += self.get_modifier_value(attr)
        #equiped armor modifiers
        val += self.get_equipped_armor().get_modifier_value(attr)
        #equiped weapon modifiers
        val += self.get_equipped_weapon().get_modifier_value(attr)
        return val

    def __set_attribute(self, attr, value):
        if value: self.__attributes[attr] = value
    
    def get_equipped_weapon(self): return self.__weapon
    def get_equipped_armor(self): return self.__armor

    def get_weapon_proficiency(self):
        """ Modifies attack and damage based on proficiency with the weapon"""
        weapon = self.get_equipped_weapon()
        if self.character_class.is_weapon_proficient(self, weapon):
            return self.proficiency
        return 0

    def get_spell_proficiency(self, spell):
        """ Modifies attack and damage based on proficiency with the weapon"""
        if self.character_class.is_spell_proficient(self, spell):
            return self.proficiency
        return 0

    def get_armor_class(self):
        """ Determines current armor class - base and any modifiers """
        return GameRules.get_armor_class(self)

    def add_experience(self, exp):
        current_level = self.__level.level
        new_level = Level.get_level_by_exp(self.__experience+exp)
        if current_level != new_level:
            self.__level.level = new_level

    def _set_encumbered(self):
        self.notify_observers('LOG', "{} encumbered".format(self.class_name))
        self.add_modifier('ENCUMBERED',ATTRIBUTES.DEXTERITY, -4)

    def _set_unencumbered(self):
        self.notify_observers('LOG', "{} unencumbered".format(self.class_name))
        self.remove_modifier('ENCUMBERED')

    def pickup(self, item):
        if isinstance(item, list):
            if len(item) == 0: return
            self.notify_observers('LOG', "{} picked up {} {}".format(self.class_name, len(item), item[0].class_name))
            for i in list:
                self.__inventory.add(i)
        else:
            self.notify_observers('LOG', "{} picked up {}".format(self.class_name, item.class_name))
            self.__inventory.add(item)
        return True

    def drop(self, item):
        if isinstance(item, list):
            if len(item) == 0: return
            self.notify_observers('LOG', "{} dropped {} {}".format(self.class_name, len(item), item[0].class_name))
            for i in list:
                self.__inventory.remove(i)
        else:
            if (self.__inventory.remove(item)):
                self.notify_observers('LOG', "{} dropped {}".format(self.class_name, item.class_name))
                return True
            else:
                self.notify_observers('LOG', "Drop failed, {} not carrying {}".format(self.class_name, item.class_name))
                return False

    def get_rid_of(self, item):
        if (self.__inventory.remove(item)):
            self.notify_observers('LOG', "{} used up".format(item.class_name))
            return True
        else:
            self.notify_observers('LOG', "Get rid of item failed, {} not carrying {}".format(self.class_name, item.class_name))
            return False

    def give(self, item, to_player):
        if isinstance(item, list):
            if len(item) == 0: return
            self.notify_observers('LOG', "{} gave {} {} to {}".format(self.class_name, len(item), item[0].class_name, to_player.class_name))
            for i in item:
                self.__inventory.remove(item)
                to_player.__inventory.add(item)
            to_player.notify_observers('LOG', "{} received {} {} from {}".format(to_player.class_name, len(item), item[0].class_name, self.class_name))
        else:
            if (self.__inventory.remove(item)):
                self.notify_observers('LOG', "{} gave {} to {}".format(self.class_name, item.class_name, to_player.class_name))

                to_player.__inventory.add(item)
                to_player.notify_observers('LOG', "{} received {} from {}".format(to_player.class_name, item.class_name, self.class_name))
                return True
            else:
                self.notify_observers('LOG', "Give failed, {} not carrying {}".format(self.class_name, item.class_name))
                return False

class Monster(Player):
    @staticmethod
    def _get_stats(): return MonsterStats._STATS

    def __init__(self, character_class):
        Modifiers.__init__(self, MonsterStats)
        super(Monster, self).__init__(character_class)
        attrs = MonsterStats.get_attributes(self)
        self.strength_base = attrs[ATTRIBUTES.STRENGTH]
        self.dexterity_base = attrs[ATTRIBUTES.DEXTERITY]
        self.constitution_base = attrs[ATTRIBUTES.CONSITUTION]
        self.wisdom_base = attrs[ATTRIBUTES.WISDOM]
        self.intelligence_base = attrs[ATTRIBUTES.INTELLIGENCE]
        self.charisma_base = attrs[ATTRIBUTES.CHARISMA]
        self.equip_weapon(MonsterStats.get_weapon(self))
        self.equip_armor(MonsterStats.get_armor(self))

        hp_dice = MonsterStats.get_hp_dice(self)
        hp_sides = MonsterStats.get_hp_sides(self)
        hp_bonus = MonsterStats.get_hp_bonus(self)
        self.max_hit_points = GameRules.determine_hit_points(hp_dice, hp_sides, hp_bonus)

class UndeadMonster(Monster):
    @property
    def is_undead(self): return True

    def __init__(self, character_class):
        super(UndeadMonster, self).__init__(character_class)

class Goblin(Monster):
    def __init__(self): super(Goblin, self).__init__(character_classes.Goblin())


class MonsterStats(BaseStats):
    __ATTRIBUTES = 1
    __WEAPON = 2
    __ARMOR = 3
    __HIT_POINTS = 4
    __ATTR_MODIFIERS = BaseStats._ATTR_MODIFIERS
    __SKILL_MODIFIERS = BaseStats._SKILL_MODIFIERS
    _STATS = {
        Goblin: {
            __HIT_POINTS: [1,8,1], #1d8+1
            __ATTRIBUTES: {
                ATTRIBUTES.INTELLIGENCE: 5,
                ATTRIBUTES.STRENGTH: 10,
                ATTRIBUTES.DEXTERITY: 11,
                ATTRIBUTES.CONSITUTION: 12,
                ATTRIBUTES.WISDOM: 2,
                ATTRIBUTES.CHARISMA: 2,
            },
            __ATTR_MODIFIERS: {
                'Faster Reaction': [ATTRIBUTES.INITIATIVE, 2]
              },
            __WEAPON: weapons.Dagger(),
            __ARMOR: armor.LightArmor()
        },
     }
    @staticmethod
    def get_attributes(monster): return MonsterStats._STATS[monster.__class__][MonsterStats.__ATTRIBUTES]
    @staticmethod
    def get_weapon(monster): return MonsterStats._STATS[monster.__class__][MonsterStats.__WEAPON]
    @staticmethod
    def get_armor(monster): return MonsterStats._STATS[monster.__class__][MonsterStats.__ARMOR]
    @staticmethod
    def get_hp_dice(monster): return MonsterStats._STATS[monster.__class__][MonsterStats.__HIT_POINTS][0]
    @staticmethod
    def get_hp_sides(monster): return MonsterStats._STATS[monster.__class__][MonsterStats.__HIT_POINTS][1]
    @staticmethod
    def get_hp_bonus(monster): return MonsterStats._STATS[monster.__class__][MonsterStats.__HIT_POINTS][2]

