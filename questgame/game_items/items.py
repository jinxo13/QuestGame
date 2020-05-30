from questgame.common.rules import PlayerAttributes, GameRules, Effects, Size, Material
from questgame.common.base_classes import Bonuses, BaseStats, Observable, Serializable
from questgame.common.utils import Helpers
from questgame.game_items import spells
from questgame.interface.alexa.utils import ReplyHelpers
import copy

class Item(Bonuses, Observable, Serializable):

    @property
    def count(self):
        return self.__count

    @count.setter
    def count(self, value):
        if value < 0: value = 0
        self.__count = value

    @property
    def size(self): return Size.Medium

    @property
    def is_fragile(self): return False

    @property
    def difficulty_class(self):
        return self._get_stats().get_difficulty_class(self)

    @property
    def max_hit_points(self):
        hit_points = ItemStats.get_hit_points(self)
        return 1000000 if hit_points == -1 else hit_points

    @property
    def hit_points(self):
        return 1000000 if self.__hit_points == -1 else self.__hit_points

    def one_of(self):
        result = copy.copy(self)
        result.count = 1
        return result

    def __init__(self, count=1, stats=None):
        #Add any inital modifiers
        Observable.__init__(self)
        self.__hit_points = self.max_hit_points
        self.__count = count
        if stats:
            super(Item,self).__init__(stats)
        else:
            super(Item,self).__init__(ItemStats)

    def affect(self, source, effect, params):
        '''
        What happens from an effect from a spell or potion
        '''
        result = False
        if effect == Effects.Damage:
            result = self.damage(params)
            if result:
                self.notify_observers_reply(ReplyHelpers.render_action_template('destroyed', source_text=source.description, item_name=self.description))
    
        elif effect == Effects.Repair:
            result = self.repair(params)
            if result:
                self.notify_observers_reply(ReplyHelpers.render_action_template('repaired', source_text=source.description, item_name=self.description))
        
        else:
            self.notify_observers_reply(ReplyHelpers.render_action_template('no_effect', item_text=self.name, effect_item=source.description))
        
        return result

    def damage(self, amount):
        if amount < 0: return
        if self.count == 0: return #Nothing to damage
        if self.__hit_points == -1: return #Can't be damaged/repaired
        self.__hit_points = max(0, self.__hit_points - amount)

        if self.hit_points == 0:
            self.count -= 1
            self.__hit_points = self.max_hit_points
            return True
        else:
            return False

    def repair(self, amount):
        if amount < 0: return False
        if self.count == 0: return False#Nothing to repair
        if self.__hit_points == -1: return False#Can't be damaged/repaired
        self.__hit_points = min(self.__hit_points + amount, self.max_hit_points)
        return True

    @property
    def name(self): return self.__class__.__name__
    @property
    def description(self): return BaseStats.get_matches(self)[0]
    @property
    def description_plural(self): return self.description + 's'

    @property
    def text_prefix(self):
        """You find a dagger"""
        """You find an axe"""
        """You find an egg"""
        if self.description.lower()[0] in ['a','e','i','o','u']:
            return 'an'
        return 'a'
    @property
    def armor_class(self): return BaseStats.get_armor_class(self)
    @property
    def weight(self): return BaseStats.get_weight(self) * self.count
    @property
    def single_weight(self): return BaseStats.get_weight(self)
    @property
    def cost(self): return BaseStats.get_cost(self) * self.count

    def is_match(self, text):
        if text is None: return False
        for match in BaseStats.get_matches(self):
            if text.lower() == match or text.lower() == match+'s' or text.lower() == self.text_prefix + ' ' + match:
                return True
        return False

    def _get_stats(self): return ItemStats

class Edible(Item):
    @property
    def size(self): return Size.Small
    @property
    def is_fragile(self): return True

    def _effect(self, action, target):
        heal_points = ItemStats.get_heal_amount(self)
        if heal_points > 0:
            target.affect(self, Effects.Heal, heal_points)
        elif heal_points < 0:
            target.affect(self, Effects.Damage, -heal_points)        

class Food(Edible):
    def eat(self, player):
        if not player.is_carrying(self):
            self.notify_observers_reply(ReplyHelpers.render_action_template('not_carrying', item_prefix=self.text_prefix, item_text=self.description, action='eat'))
            return False
        if self.count == 0:
            self.notify_observers_reply(ReplyHelpers.render_action_template('nothing_to_eat', item_text=self.name))
            return False
        player.notify_observers_log("{} - eat {}".format(player.class_name, self.class_name))
        self.count -= 1
        self._effect('eat', player)
        return True
    
class Drink(Edible):
    def drink(self, player):
        if not player.is_carrying(self):
            self.notify_observers_reply(ReplyHelpers.render_action_template('not_carrying', item_prefix=self.text_prefix, item_text=self.description, action='drink'))
            return False
        if self.count == 0:
            self.notify_observers_reply(ReplyHelpers.render_action_template('nothing_to_drink', item_text=self.name))
            return False
        player.notify_observers_log("{} - drank {}".format(player.class_name, self.class_name))
        self.count -= 1
        self._effect('drink', player)
        return True

class Money(Item):
    @property
    def size(self): return Size.Small
    def is_fragile(self): return False

class Gold(Money):  pass
class Silver(Money):  pass
class Copper(Money):  pass

class StrengthRing(Item): pass
class LockPick(Item): pass
class StaleBread(Food): pass
class NightBerry(Food): pass
class Beer(Drink): pass
class Scroll(Item):
    '''
    When picked up player learns the spell
    '''
    @property
    def size(self): return Size.Small
    def is_fragile(self): return True
    @property
    def spell(self): return self.__spell
    @property
    def description(self): return BaseStats.get_matches(self.__spell)[0] + ' scroll'
    @property
    def cost(self): return BaseStats.get_cost(self.__spell)
    def __init__(self, spell):
        super(Scroll, self).__init__()
        self.__spell = spell

class Key(Item):
    @property
    def id(self): return ItemStats.get_key_id(self)
    def __init__(self):
        super(Key, self).__init__()
    @property
    def size(self): return Size.Small
    def is_fragile(self): return True

class CellRoomKey(Key): pass
class WeaponsRoomKey(Key): pass

class ItemStats(BaseStats):
    _ARMOR_CLASS = BaseStats._ARMOR_CLASS
    _WEIGHT = BaseStats._WEIGHT
    _COST = BaseStats._COST
    _NAME = BaseStats._NAME
    _ATTR_MODIFIERS = BaseStats._ATTR_MODIFIERS
    _SKILL_MODIFIERS = BaseStats._SKILL_MODIFIERS
    _NAME_MATCHES = BaseStats._NAME_MATCHES
    _HEAL_AMOUNT = 1
    _MATERIAL = BaseStats._MATERIAL

    _STATS = {
        StrengthRing: { _NAME_MATCHES: ['strength ring','ring'], _WEIGHT: 0.1, _COST: 5, _ATTR_MODIFIERS: {'BONUS':[PlayerAttributes.STRENGTH,2]}, _MATERIAL: Material.Steel },
        CellRoomKey: { _NAME_MATCHES: ['key'], _WEIGHT: 0.1, _COST: 0, _MATERIAL: Material.Steel },
        WeaponsRoomKey: { _NAME_MATCHES: ['key'], _WEIGHT: 0.1, _COST: 0, _MATERIAL: Material.Steel },
        LockPick: { _NAME_MATCHES: ['lock pick','lockpick'], _WEIGHT: 0.1, _COST: 0, _MATERIAL: Material.Steel },
        StaleBread: { _NAME_MATCHES: ['stale bread','bread'], _HEAL_AMOUNT: 1, _WEIGHT: 0.1, _COST: 0, _MATERIAL: Material.Food },
        NightBerry: { _NAME_MATCHES: ['might berry'], _HEAL_AMOUNT: -10, _WEIGHT: 0.1, _COST: 0, _MATERIAL: Material.Food },
        Beer: { _NAME_MATCHES: ['beer'], _HEAL_AMOUNT: 0, _WEIGHT: 0.1, _COST: 0, _MATERIAL: Material.Glass },
        Scroll:  { _NAME_MATCHES: ['scroll','magic scroll'], _WEIGHT: 0.1, _COST: 0, _MATERIAL: Material.Paper },
        Gold:  { _NAME_MATCHES: ['gold', 'gold coins', 'coins', 'coin'], _WEIGHT: 0.001, _COST: 1, _MATERIAL: Material.Gold },
        Silver:  { _NAME_MATCHES: ['silver', 'silver coins', 'coins', 'coin'], _WEIGHT: 0.001, _COST: 0.1, _MATERIAL: Material.Silver },
        Copper:  { _NAME_MATCHES: ['copper', 'copper coins', 'coins', 'coin'], _WEIGHT: 0.001, _COST: 0.01, _MATERIAL: Material.Copper },
        }

    _KEYS = {
        CellRoomKey: 1,
        WeaponsRoomKey: 2,
        }

    @staticmethod
    def get_key_id(key):
        return ItemStats._KEYS[key.__class__]
    @staticmethod
    def get_key(id):
        for k in ItemStats._KEYS.keys():
            if ItemStats._KEYS[k] == id: return k()
        return None

    @staticmethod
    def get_heal_amount(item):
        if not ItemStats._HEAL_AMOUNT in ItemStats._STATS[item.__class__]: return 0
        return ItemStats._STATS[item.__class__][ItemStats._HEAL_AMOUNT]
