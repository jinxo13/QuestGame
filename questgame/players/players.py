from questgame.game_items import armor, weapons, items, spells, potions
from questgame.players import character_classes, skills
from questgame.common.rules import PlayerAttributes, Level, GameRules, Effects, Actions
from questgame.common.base_classes import Bonuses, BaseStats, Observable, Serializable
from questgame.game_items.standard_items import Inventory
from questgame.common.utils import Helpers
from questgame.interface.alexa.utils import ReplyHelpers
import json
import copy

def action(action):
    def decorator(function):
        def wrapper(*args, **kwargs):
            inst = args[0]
            if not inst.can_act:
                inst.notify_observers_reply(ReplyHelpers.render_action_template('cannot_act', condition=inst.current_condition))
                return False
            inst.current_action = action
            try:
                result = function(*args, **kwargs)
            finally:
                inst.current_action = False
            return result
        return wrapper
    return decorator

class Player(Bonuses, Observable, Serializable):
    @property
    def description(self): return self.__class__.__name__.lower()
    @property
    def name(self): return self.__class__.__name__.lower()

    @property
    def dexterity(self): return self.get_attribute_current(PlayerAttributes.DEXTERITY)
    @property
    def strength(self): return self.get_attribute_current(PlayerAttributes.STRENGTH)
    @property
    def intelligence(self): return self.get_attribute_current(PlayerAttributes.INTELLIGENCE)
    @property
    def constitution(self): return self.get_attribute_current(PlayerAttributes.CONSITUTION)
    @property
    def charisma(self): return self.get_attribute_current(PlayerAttributes.CHARISMA)
    @property
    def wisdom(self): return self.get_attribute_current(PlayerAttributes.WISDOM)

    @property
    def carry_capacity(self):
        return GameRules.determine_carry_capacity(self)
    @property
    def carry_weight(self):
        return self.__inventory.weight

    @property
    def inventory(self): return self.__inventory

    @property
    def strength_base(self): return self.get_attribute_base(PlayerAttributes.STRENGTH)
    @strength_base.setter
    def strength_base(self, value): self.__set_attribute_base(PlayerAttributes.STRENGTH, value)
    @property
    def dexterity_base(self):  return self.get_attribute_base(PlayerAttributes.DEXTERITY)
    @dexterity_base.setter
    def dexterity_base(self, value): self.__set_attribute_base(PlayerAttributes.DEXTERITY, value)
    @property
    def constitution_base(self):  return self.get_attribute_base(PlayerAttributes.CONSITUTION)
    @constitution_base.setter
    def constitution_base(self, value): self.__set_attribute_base(PlayerAttributes.CONSITUTION, value)
    @property
    def intelligence_base(self):  return self.get_attribute_base(PlayerAttributes.INTELLIGENCE)
    @intelligence_base.setter
    def intelligence_base(self, value): self.__set_attribute_base(PlayerAttributes.INTELLIGENCE, value)
    @property
    def wisdom_base(self): return self.get_attribute_base(PlayerAttributes.WISDOM)
    @wisdom_base.setter
    def wisdom_base(self, value): self.__set_attribute_base(PlayerAttributes.WISDOM, value)
    @property
    def charisma_base(self): return self.get_attribute_base(PlayerAttributes.CHARISMA)
    @charisma_base.setter
    def charisma_base(self, value): self.__set_attribute_base(PlayerAttributes.CHARISMA, value)

    def __set_attribute_base(self,attr, value): self.__attributes[str(attr)] = value
    def get_attribute_base(self,attr):
        if str(attr) in self.__attributes:
            return self.__attributes[str(attr)]
        return 0
    def get_attribute_current(self,attr):
        result = self.get_attribute_base(attr) + self.__get_bonuses(attr)
        return result

    def is_match(self, text):
        return text.lower() == self.__class__.__name__.lower()

    ### Returns the modifier based on the attribute score
    def get_attribute_modifier(self, attrs):
        if not isinstance(attrs, list):
            attrs = [attrs]
        #If multiple select max
        if len(attrs) == 0: return 0
        max_attr_val = max(map(self.get_attribute_current, attrs))
        return GameRules.get_attribute_modifier(max_attr_val)

    ### Modifiers based on equiped items
    def determine_ability_modifier(self):
        '''Determined based on a weapons ability modifier(s), normally one of strength or dexterity'''
        result = self.get_attribute_modifier(self.get_equipped_weapon().modifier_attributes)
        return result

    def determine_damage_modifier(self):
        return self.determine_ability_modifier()

    @property
    def defense_bonus(self): return self.__get_bonuses(PlayerAttributes.DEFENSE)
    @property
    def other_attack_bonus(self):
        return  self.__get_bonuses(PlayerAttributes.ATTACK)

    def damage_bonus(self, attack_no=1):
        '''Return attack bonus used to roll for damage'''
        return self.character_class.get_attack_bonus(self)[attack_no-1]

    def determine_throw_bonus(self): return self.__get_bonuses(PlayerAttributes.THROW)

    @property
    def initiative_bonus(self): return self.__get_bonuses(PlayerAttributes.INITIATIVE)
    @property
    def wisdom_bonus(self): return self.__get_bonuses(PlayerAttributes.WISDOM)
    @property
    def dexterity_bonus(self): return self.__get_bonuses(PlayerAttributes.DEXTERITY)
    @property
    def constitution_bonus(self): return self.__get_bonuses(PlayerAttributes.CONSITUTION)
    @property
    def intelligence_bonus(self): return self.__get_bonuses(PlayerAttributes.INTELLIGENCE)
    @property
    def strength_bonus(self): return self.__get_bonuses(PlayerAttributes.STRENGTH)

    @property
    def is_dead(self):
        return self.__is_dead
    @property
    def is_looted(self): return self.__is_looted
    @property
    def is_unconscious(self): return not self.is_dead and self.hit_points == 0
    @property
    def is_stunned(self): return self.__is_stunned
    @property
    def current_condition(self):
        if self.is_stunned: return 'stunned'
        if self.is_unconscious: return 'unconscious'
        if self.is_dead: return 'dead'
        #TODO: Handle more states
        return 'ok'
    @property
    def is_in_battle(self): return self.__is_in_battle
    
    @property
    def current_action(self):
        return self.__current_action
    @current_action.setter
    def current_action(self, val):
        self.__current_action = val

    @property
    def can_act(self):
        return not self.is_stunned and not self.is_dead and not self.is_unconscious

    @property
    def is_undead(self): return False
    @property
    def is_monster(self): return False

    def get_reply_key(self, key):
        if self.is_monster:
            return 'monster_'+key
        return 'player_'+key

    @property
    def is_mage(self): return self.__class__ == Mage
    @property
    def is_thief(self): return self.__class__ == Thief
    @property
    def is_ranger(self): return self.__class__ == Ranger
    @property
    def is_fighter(self): return self.__class__ == Fighter

    @property
    def money(self): return self.__inventory.money

    @property
    def is_encumbered(self): return self.carry_weight > self.carry_capacity

    @property
    def character_class(self): return self.__character_class
    
    @property
    def max_mana_points(self): return self.__max_mana_points
    @max_mana_points.setter
    def max_mana_points(self, value):
        self.__max_mana_points = value
    @property
    def mana_points(self): return self.__mana_points
    def __set_mana_points(self, value):
        self.__mana_points = min(max(0,value),self.__max_mana_points)
    def add_mana(self, value):
        self.__set_mana_points(self.__mana_points + value)
    ## Hit points
    @property
    def max_hit_points(self): return self.__max_hit_points
    @max_hit_points.setter
    def max_hit_points(self, value):
        delta = value - self.__max_hit_points
        self.__max_hit_points = value
        self.__set_hit_points(self.__hit_points + delta)
    @property
    def hit_points(self):
        return self.__hit_points
    def __set_hit_points(self, value):
        self.__hit_points = min(max(0,value),self.__max_hit_points)

    def affect(self, source, effect, params):
        if effect == Effects.Damage: self.wound(params)
        elif effect == Effects.Heal: self.heal(params)

    def wound(self, points, critical_hit=False):
        if points <= 0 or self.is_dead: return False
        self.notify_observers_log("{} wounded {}".format(self.__class__.__name__,points))
        
        #Dead if massive damage, otherwise unconsious
        #10 - 20 = -10 - dead
        if (self.hit_points - points) <= -self.max_hit_points:
            self.__is_dead = True
            self.notify_observers_log("{} - DIED!".format(self.class_name))

        starting_health = self.hit_points
        self.__set_hit_points(self.hit_points - points)
        
        if self.is_unconscious:
            death_saves = 3
            if starting_health == 0:
                death_saves -= 1
                if critical_hit:
                    death_saves -= 1
            else:
                self.notify_observers_log("{} - UNCONSCIOUS!".format(self.class_name))
            #Roll saves
            saved = next((True for x in range(death_saves) if GameRules.roll_death_save(self)), False)
            if not saved:
                self.__is_dead = True
                self.notify_observers_log("{} - DIED!".format(self.class_name))

        return True

    def heal(self, points):
        if points < 1 or self.hit_points == self.max_hit_points or self.is_dead: return False
        self.__set_hit_points(self.hit_points + points)
        self.notify_observers_reply(ReplyHelpers.render_action_template(self.get_reply_key('healed'), points=min(points,self.max_hit_points-self.hit_points), max_hit_points=self.max_hit_points, hit_points=self.hit_points))
        return True

    def _start_battle(self): self.__is_in_battle = True
    def _end_battle(self): self.__is_in_battle = False

    @action(action=Actions.THROW)
    def throw(self, item, target):
        '''
        Returns True if hit, False if miss or can't throw
        TODO: May need a better return
        '''
        if not self.is_carrying(item):
            #You're not carrying {{item_prefix}} {{item_text}} to {{action}}.
            self.notify_observers_reply(ReplyHelpers.render_action_template('not_carrying', item_prefix=item.text_prefix, item_text=item.name, action='throw'))
            return False

        if not isinstance(item, weapons.Weapon) or not item.is_throwable:
            self.notify_observers_log("{} - weapon {} is not throwable".format(self.class_name, item.name))
            self.notify_observers_reply(ReplyHelpers.render_action_template('not_throwable', weapon_text=item.name))
            return False
        
        result = item.throw(self, target)
        #Maybe give if hit?
        self.drop(item.one_of())

        return result

    @action(action=Actions.STRIKE)
    def strike(self, defender):
        defender_name = defender.__class__.__name__
        attacker_name = self.__class__.__name__

        if not self.can_act:
            self.notify_observers_reply(ReplyHelpers.render_action_template(self.get_reply_key('stunned'), defender_name=defender_name, attacker_name=attacker_name))
            self.notify_observers_log("{} - stunned, unconscious or dead - can't attack".format(attacker_name))
            return False

        return self.get_equipped_weapon().strike(self, defender)

    @action(action=Actions.EAT)
    def eat(self, item):
        if not isinstance(item, items.Food):
            ReplyHelpers.render_action_template('eat_cannot', item_text=item.description)
            return False
        if not self.is_carrying(item):
            self.notify_observers_reply(ReplyHelpers.render_action_template('not_carrying', action=Actions.get_action_text(Actions.EAT), item_prefix=item.text_prefix, item_text=item.description))
            return False
        self.notify_observers_reply(ReplyHelpers.render_action_template('eat_food', item_text=item.description))
        if item.eat(self):
            self.get_rid_of_one(item)
            return True
        return False

    @action(action=Actions.CAST)
    def cast(self, spell, defender):
        return spell.cast(self, defender)

    @action(action=Actions.DRINK)
    def drink(self, item):
        if not isinstance(item, potions.Potion) and not isinstance(item, items.Drink):
            self.notify_observers_reply(ReplyHelpers.render_action_template('drink_cannot', item_prefix=item.text_prefix, item_text=item.description))
            return False

        if not self.is_carrying(item):
            self.notify_observers_reply(ReplyHelpers.render_action_template('not_carrying', action=Actions.get_action_text(Actions.DRINK), item_prefix=item.text_prefix, item_text=item.description))
            return False
        
        self.notify_observers_reply(ReplyHelpers.render_action_template(self.get_reply_key('drink'), item_prefix=item.text_prefix, item_text=item.description, attacker_name=self.name))
        if item.drink(self):
            self.get_rid_of_one(item)
            return True
        return False

    def skill_attack(self, skill, defender):
        defender_name = defender.__class__.__name__
        attacker_name = self.__class__.__name__
        if not self.has_skill(skill):
            self.notify_observers_log("{} - isn't proficient in this skill - can't attack".format(attacker_name))
            return False

        dmg = skill.damage(self)
        self.notify_observers_log("{} - used skill {} on {}! Damage {}".format(attacker_name, skill.__class__.__name__, defender_name, dmg))
        defender.wound(dmg)
        return True

    @property
    def level(self): return self.__level.level
    @property
    def proficiency_bonus(self): return self.__level.proficiency_bonus

    @action(action=Actions.EQUIP_WEAPON)
    def equip_weapon(self,weapon):
        if weapon == None: raise AttributeError()
        if not self.is_carrying(weapon):
            self.notify_observers_reply(ReplyHelpers.render_action_template('not_carrying', item_prefix=weapon.text_prefix, item_text=weapon.description, action='equip'))
            return False
        if not isinstance(weapon, weapons.Weapon):
            self.notify_observers_reply(ReplyHelpers.render_action_template(self.get_reply_key('equip_not_weapon'), item_text=weapon.description))
            return False
        self.__weapon = weapon
        if not isinstance(weapon, type(self.default_weapon)):
            self.notify_observers_reply(ReplyHelpers.render_action_template(self.get_reply_key('equip_weapon'), attacker_name=self.name, weapon_text=weapon.description))
        return True

    @action(action=Actions.EQUIP_ARMOR)
    def equip_armor(self, armr):
        if armr == None: raise AttributeError()
        if not self.is_carrying(armr):
            self.notify_observers_reply(ReplyHelpers.render_action_template('not_carrying', item_prefix=armr.text_prefix, item_text=armr.description, action='equip'))
            return False
        if not isinstance(armr, armor.Armor):
            self.notify_observers_reply(ReplyHelpers.render_action_template(self.get_reply_key('equip_not_armor'), item_text=armr.description))
            return False
        self.__armor = armr
        if not isinstance(armr, type(self.default_armor)):
            self.notify_observers_reply(ReplyHelpers.render_action_template(self.get_reply_key('equip_armor'), attacker_name=self.name, armor_text=armr.description))
        return True

    @property
    def default_weapon(self):
        return self.__default_weapon

    @property
    def default_armor(self):
        return self.__default_armor

    def __init__(self, character_class):
        super(Player,self).__init__(None)
        Observable.__init__(self)
        self.__hit_points = 0
        self.__max_hit_points = 0
        self.__mana_points = 0
        self.__max_mana_points = 0
        self.__attributes = {}
        self.__learned_spells = []
        self.__default_weapon = PlayerStats.get_weapon(self)
        self.__default_armor = PlayerStats.get_armor(self)
        self.__armor = None
        self.__weapon = None
        self.__character_class = character_class
        self.__experience = 0
        self.__level = Level()
        self.__is_stunned = False
        self.__is_in_battle = False
        self.__is_dead = False
        self.__is_looted = False
        self.__current_action = False
        self.__inventory = Inventory(self)

        attrs = PlayerStats.get_attributes(self)
        self.strength_base = attrs[PlayerAttributes.STRENGTH]
        self.dexterity_base = attrs[PlayerAttributes.DEXTERITY]
        self.constitution_base = attrs[PlayerAttributes.CONSITUTION]
        self.wisdom_base = attrs[PlayerAttributes.WISDOM]
        self.intelligence_base = attrs[PlayerAttributes.INTELLIGENCE]
        self.charisma_base = attrs[PlayerAttributes.CHARISMA]
        self.equip_weapon(self.__default_weapon)
        self.equip_armor(self.__default_armor)

        hp_dice = PlayerStats.get_hp_dice(self)
        hp_sides = PlayerStats.get_hp_sides(self)
        hp_bonus = PlayerStats.get_hp_bonus(self)
        self.max_hit_points = GameRules.determine_hit_points(hp_dice, hp_sides, hp_bonus)
        self.max_mana_points = self.character_class.get_mana_points(self)

        #for spell in self.character_class.get_spells(self.level):
        #    self.learn_spell(spell())

    def __get_bonuses(self,attr):
        val = 0
        #player modifiers
        val += self.get_bonus_value(attr)
        #equiped armor modifiers
        val += self.get_equipped_armor().get_bonus_value(attr)
        #equiped weapon modifiers
        val += self.get_equipped_weapon().get_bonus_value(attr)
        return val

    def __set_attribute(self, attr, value):
        if value: self.__attributes[attr] = value
    
    def get_equipped_weapon(self):
        return self.__weapon if not self.__weapon == None else self.__default_weapon

    def get_equipped_armor(self):
        return self.__armor if not self.__armor == None else self.__default_armor

    def is_weapon_proficient(self, weapon):
        return self.character_class.is_weapon_proficient(self, weapon)

    def determine_proficiency_bonus(self):
        """ Modifies attack and damage based on proficiency def eq the weapon"""
        return self.proficiency_bonus if self.character_class.is_weapon_proficient(self, self.get_equipped_weapon()) else 0

    def determine_spell_proficiency(self, spell):
        """ Modifies attack and damage based on proficiency with the weapon"""
        return self.proficiency_bonus if self.character_class.knows_spell(self, spell) else 0

    def get_defense(self):
        """ Determines current armor class - base and any modifiers """
        return GameRules.get_player_defense(self)

    def add_experience(self, exp):
        current_level = self.__level.level
        self.__experience += exp
        new_level = Level.get_level_by_exp(self.__experience)
        if current_level != new_level:
            self.__level.level = new_level

    def _set_encumbered(self):
        self.notify_observers_log("{} encumbered".format(self.class_name))
        self.add_bonus('ENCUMBERED',PlayerAttributes.DEXTERITY, -4)

    def _set_unencumbered(self):
        self.notify_observers_log("{} unencumbered".format(self.class_name))
        self.remove_bonus('ENCUMBERED')

    def is_carrying(self, item):
        return self.__inventory.contains(item)

    def get_item_by_name(self, item_text):
        for item in self.__inventory.items():
            if item.is_match(item_text): return item
        return None

    def get_item(self, item):
        for itm in self.__inventory.items():
            if itm.__class__ == item.__class__:
                return itm
        return False

    def has_skill(self, skill):
        return self.character_class.is_skill_proficient(self, skill)

    def can_picklock(self):
        return self.can_act and self.is_carrying(items.LockPick()) and self.has_skill(skills.LockPicking())

    @action(action=Actions.PICK_LOCK)
    def pick_lock(self, item):
        if not self.can_picklock():
            self.notify_observers_reply(ReplyHelpers.render_room_template('no_lockpick_ability'))
            return False
        self.remove_item(items.LockPick())
        return item.unlock(self)

    def learn_spell(self, spell):
        if not isinstance(spell, spells.Spell):
            self.notify_observers_reply(ReplyHelpers.render_action_template('not_spell', spell_name=spell.description))
            return False
        if self.level < spell.level:
            self.notify_observers_reply(ReplyHelpers.render_action_template('spell_too_hard', spell_name=spell.description))
            return False
        if not self.knows_spell(spell):
            self.__learned_spells.append(spell)
            self.notify_observers_reply(ReplyHelpers.render_action_template('spell_learned', spell_name=spell.description))
            return True
        else:
            self.notify_observers_reply(ReplyHelpers.render_action_template('spell_already_known', spell_name=spell.description))
            return False

    def knows_spell(self, spell):
        for spl in self.__learned_spells:
            if spl.__class__ == spell.__class__: return True
        return self.character_class.knows_spell(self, spell)

    def can_cast_spell(self, spell):
        if not self.can_act:
            self.notify_observers_reply(ReplyHelpers.render_action_template('cannot_act', condition=self.current_condition))
            return False
        if not self.knows_spell(spell):
            self.notify_observers_reply(ReplyHelpers.render_action_template('spell_not_proficient', spell_name=spell.description))
            return False
        if spell.level > self.level:
            self.notify_observers_reply(ReplyHelpers.render_action_template('spell_too_advanced', spell_name=spell.description))
            return False
        if not self.mana_points >= spell.level:
            self.notify_observers_reply(ReplyHelpers.render_action_template('spell_not_enough_mana', spell_name=spell.description))
            return False
        return True

    def loot_body(self, body):
        result = []
        if body.is_looted:
            self.notify_observers_reply(ReplyHelpers.render_action_template('already_looted', body_name=body.description))
            return False
        for item in body.inventory.items():
            body.__inventory.remove(item)
            self.__inventory.add(item)
            result.append(item)
        self.__is_looted = True
        return result

    def has_weapon_equipped(self):
        weapon = self.get_equipped_weapon()
        default = self.default_weapon
        return not isinstance(weapon, type(default))

    def has_armor_equipped(self):
        return not isinstance(self.get_equipped_armor(), type(self.default_armor))

    def pickup(self, item):
        if isinstance(item, items.Scroll):
            scroll = item
            self.learn_spell(scroll.spell)
        self.notify_observers_log("{} picked up {} {}".format(self.class_name, item.count, item.class_name))

        self.__inventory.add(item)

        #Equip weapon, if proficient and not equipped
        if not self.has_weapon_equipped() and isinstance(item, weapons.Weapon) and not isinstance(item, weapons.Arrow) \
            and self.character_class.is_weapon_proficient(self, item):
            self.equip_weapon(item)

        #Equip armor, if proficient and not equipped
        if not self.has_armor_equipped() and isinstance(item, armor.Armor) \
            and self.character_class.is_armor_proficient(self, item):
            self.equip_armor(item)
        return True

    def is_weapon_equipped(self, item):
        return self.get_equipped_weapon().__class__ == item.__class__
    def is_armor_equipped(self, item):
        return self.get_equipped_armor().__class__ == item.__class__

    def _check_equipped_items(self, item):
        '''
        Sets weapons to fists if the player no longer has the equipped weapon
        '''
        if not self.is_carrying(item):
            if self.is_weapon_equipped(item):
                #Hmmm looks like you may have thrown your last dagger :)
                self.__weapon = self.default_weapon

            if self.is_armor_equipped(item):
                self.__armor = self.default_armor

    def remove_item(self, item):
        result = self.__inventory.remove(item)
        self._check_equipped_items(item)
        return result

    def drop(self, item):
        if not self.is_carrying(item):
            self.notify_observers_log("Drop failed, {} not carrying {}".format(self.class_name, item.class_name))
            return False
        result = self.remove_item(item)
        self.notify_observers_log("{} dropped {} {}".format(self.class_name, item.count, item.class_name))
        return result

    def get_rid_of_one(self, item):
        itm = copy.copy(item)
        itm.count = 1
        result = self.remove_item(itm)
        if result:
            self.notify_observers_log("{} used up".format(item.class_name))
            return result
        else:
            self.notify_observers_log("Get rid of item failed, {} not carrying {}".format(self.class_name, item.class_name))
            return False

    def give(self, item, to_player):
        if not self.is_carrying(item):
            self.notify_observers_log("Give failed, {} not carrying {}".format(self.class_name, item.class_name))
            return False

        if not self.remove_item(item):
            self.notify_observers_log("Give failed, {} couldn't remove {}".format(self.class_name, item.class_name))
            return False

        to_player.__inventory.add(item)
        self.notify_observers_log("{} gave {} {} to {}".format(self.class_name, item.count, item.class_name, to_player.class_name))
        return True

class Thief(Player):
    def __init__(self): super(Thief, self).__init__(character_classes.Thief())
class Mage(Player):
    def __init__(self): super(Mage, self).__init__(character_classes.Mage())
class Fighter(Player):
    def __init__(self): super(Fighter, self).__init__(character_classes.Fighter())
class Ranger(Player):
    def __init__(self): super(Ranger, self).__init__(character_classes.Ranger())


class Monster(Player):
    @property
    def is_monster(self): return True

class UndeadMonster(Monster):
    @property
    def is_undead(self): return True

    def __init__(self, character_class):
        super(UndeadMonster, self).__init__(character_class)

class Goblin(Monster):
    def __init__(self): super(Goblin, self).__init__(character_classes.Goblin())

class Rat(Monster):
    def __init__(self): super(Rat, self).__init__(character_classes.Animal())

class ZombieRat(UndeadMonster):
    def __init__(self): super(ZombieRat, self).__init__(character_classes.Animal())

class PlayerStats(BaseStats):
    __PlayerAttributes = 1
    __WEAPON = 2
    __ARMOR = 3
    __HIT_POINTS = 4
    __ATTR_MODIFIERS = BaseStats._ATTR_MODIFIERS
    __SKILL_MODIFIERS = BaseStats._SKILL_MODIFIERS
    _STATS = {
        Thief: {
            __HIT_POINTS: [1,8,8], #1d8+8
            __PlayerAttributes: {
                PlayerAttributes.INTELLIGENCE: 8,
                PlayerAttributes.STRENGTH: 10,
                PlayerAttributes.DEXTERITY: 11,
                PlayerAttributes.CONSITUTION: 12,
                PlayerAttributes.WISDOM: 2,
                PlayerAttributes.CHARISMA: 2,
            },
            __ATTR_MODIFIERS: {
                'Faster Reaction': [PlayerAttributes.INITIATIVE, 2],
                'Throw bonus': [PlayerAttributes.THROW, 2]
              },
            __WEAPON: weapons.Fists(),
            __ARMOR: armor.BodyArmor()
        },
        Fighter: {
            __HIT_POINTS: [1,8,8], #1d8+8
            __PlayerAttributes: {
                PlayerAttributes.INTELLIGENCE: 8,
                PlayerAttributes.STRENGTH: 10,
                PlayerAttributes.DEXTERITY: 11,
                PlayerAttributes.CONSITUTION: 12,
                PlayerAttributes.WISDOM: 2,
                PlayerAttributes.CHARISMA: 2,
            },
            __ATTR_MODIFIERS: {
                'Faster Reaction': [PlayerAttributes.INITIATIVE, 2],
                'Throw bonus': [PlayerAttributes.THROW, 2]
              },
            __WEAPON: weapons.Fists(),
            __ARMOR: armor.BodyArmor()
        },
        Ranger: {
            __HIT_POINTS: [1,8,8], #1d8+8
            __PlayerAttributes: {
                PlayerAttributes.INTELLIGENCE: 8,
                PlayerAttributes.STRENGTH: 10,
                PlayerAttributes.DEXTERITY: 11,
                PlayerAttributes.CONSITUTION: 12,
                PlayerAttributes.WISDOM: 2,
                PlayerAttributes.CHARISMA: 2,
            },
            __ATTR_MODIFIERS: {
                'Faster Reaction': [PlayerAttributes.INITIATIVE, 2],
                'Throw bonus': [PlayerAttributes.THROW, 2]
              },
            __WEAPON: weapons.Fists(),
            __ARMOR: armor.BodyArmor()
        },
        Mage: {
            __HIT_POINTS: [1,6,6], #1d6+6
            __PlayerAttributes: {
                PlayerAttributes.INTELLIGENCE: 12,
                PlayerAttributes.STRENGTH: 8,
                PlayerAttributes.DEXTERITY: 11,
                PlayerAttributes.CONSITUTION: 10,
                PlayerAttributes.WISDOM: 8,
                PlayerAttributes.CHARISMA: 4,
            },
            __ATTR_MODIFIERS: {
                'Faster Reaction': [PlayerAttributes.INITIATIVE, 2]
              },
            __WEAPON: weapons.Fists(),
            __ARMOR: armor.BodyArmor()
        },
        Goblin: {
            __HIT_POINTS: [1,8,1], #1d8+1
            __PlayerAttributes: {
                PlayerAttributes.INTELLIGENCE: 5,
                PlayerAttributes.STRENGTH: 10,
                PlayerAttributes.DEXTERITY: 11,
                PlayerAttributes.CONSITUTION: 12,
                PlayerAttributes.WISDOM: 2,
                PlayerAttributes.CHARISMA: 2,
            },
            __ATTR_MODIFIERS: {
                'Faster Reaction': [PlayerAttributes.INITIATIVE, 2]
              },
            __WEAPON: weapons.Dagger(),
            __ARMOR: armor.LightArmor()
        },
        Rat: {
            __HIT_POINTS: [1,6,1], #1d6+1
            __PlayerAttributes: {
                PlayerAttributes.INTELLIGENCE: 2,
                PlayerAttributes.STRENGTH: 8,
                PlayerAttributes.DEXTERITY: 8,
                PlayerAttributes.CONSITUTION: 4,
                PlayerAttributes.WISDOM: 1,
                PlayerAttributes.CHARISMA: 1,
            },
            __ATTR_MODIFIERS: {
                'Faster Reaction': [PlayerAttributes.INITIATIVE, 2]
              },
            __WEAPON: weapons.Claws(),
            __ARMOR: armor.FurArmor()
        },
        ZombieRat: {
            __HIT_POINTS: [1,6,1], #1d6+1
            __PlayerAttributes: {
                PlayerAttributes.INTELLIGENCE: 2,
                PlayerAttributes.STRENGTH: 8,
                PlayerAttributes.DEXTERITY: 8,
                PlayerAttributes.CONSITUTION: 4,
                PlayerAttributes.WISDOM: 1,
                PlayerAttributes.CHARISMA: 1,
            },
            __ATTR_MODIFIERS: {
                'Faster Reaction': [PlayerAttributes.INITIATIVE, 2]
              },
            __WEAPON: weapons.Claws(),
            __ARMOR: armor.FurArmor()
        },
     }
    @staticmethod
    def get_attributes(monster): return PlayerStats._STATS[monster.__class__][PlayerStats.__PlayerAttributes]
    @staticmethod
    def get_weapon(monster): return PlayerStats._STATS[monster.__class__][PlayerStats.__WEAPON]
    @staticmethod
    def get_armor(monster): return PlayerStats._STATS[monster.__class__][PlayerStats.__ARMOR]
    @staticmethod
    def get_hp_dice(monster): return PlayerStats._STATS[monster.__class__][PlayerStats.__HIT_POINTS][0]
    @staticmethod
    def get_hp_sides(monster): return PlayerStats._STATS[monster.__class__][PlayerStats.__HIT_POINTS][1]
    @staticmethod
    def get_hp_bonus(monster): return PlayerStats._STATS[monster.__class__][PlayerStats.__HIT_POINTS][2]

