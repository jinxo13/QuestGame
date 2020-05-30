import jsonpickle
from questgame.common.rules import Difficulty, Material, Size, Defaults

class Serializable(object):
    def get_state(self):
        return jsonpickle.encode(self)
    @staticmethod
    def create_from_state(state):
        return jsonpickle.decode(state)

class Observable(object):
    def __init__(self):
        self.__observers = []
    
    def register_observer(self, observer):
        self.__observers.append(observer)
    
    def deregister_observer(self, observer):
        if observer in self.__observers:
            self.__observers.remove(observer)

    def notify_observers_reply(self, msg):
        for observer in self.__observers:
            observer.notify('REPLY', msg)

    def notify_observers_log(self, msg):
        for observer in self.__observers:
            observer.notify('LOG', msg)

class Observer(object):
    '''
    Observer class used to be notified of any events from the observable object
    '''
    def __init__(self, observable):
        self.__observable = observable
        observable.register_observer(self)
        self.replies = []
    
    def __enter__(self):
        return self

    def clear(self): self.replies = []

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__observable.deregister_observer(self)

    def notify(self, medium, msg):
        if medium == 'LOG':
            print(msg)
        if medium == 'REPLY':
            self.replies.append(msg)

class BaseStats(object):
    _NAME = 100
    _WEIGHT = 101
    _COST = 102
    _ATTR_MODIFIERS = 103
    _ARMOR_CLASS = 104
    _SKILL_MODIFIERS = 105
    _NAME_MATCHES = 106
    _DIFFICULTY_CLASS = 107
    _MATERIAL = 108

    _HIT_POINTS = {
        #[fragile, resilient] -1 = unbreakable
        Size.Tiny: [2, 5],
        Size.Small: [3, 10],
        Size.Medium: [4, 18],
        Size.Large: [5, 27],
        Size.Huge: [50, -1],
        Size.Gargantuan: [100, -1]
    }

    _AC_TYPES = {
        8: [Material.Food],
        11: [Material.Cloth, Material.Paper, Material.Rope],
        13: [Material.Crystal, Material.Glass, Material.Ice],
        15: [Material.Wood, Material.Bone, Material.Copper],
        17: [Material.Stone, Material.Gold],
        19: [Material.Iron, Material.Steel, Material.Silver],
        21: [Material.Mithral],
        23: [Material.Adamantine]
    }
    @staticmethod
    def get_hit_points(item):
        val = BaseStats._HIT_POINTS[item.size][0 if item.is_fragile else 1]
        return val

    @staticmethod
    def get_name(item): return item._get_stats()._STATS[item.__class__][BaseStats._NAME]
    @staticmethod
    def get_armor_class(item):
        item_stats = item._get_stats()
        #Find specific value
        if BaseStats._ARMOR_CLASS in item_stats._STATS[item.__class__].keys():
            return item_stats._STATS[item.__class__][BaseStats._ARMOR_CLASS]
        else:
            #Fallback on material
            if BaseStats._MATERIAL in item_stats._STATS[item.__class__].keys():
                material = item_stats._STATS[item.__class__][BaseStats._MATERIAL]
                return next(key for key in BaseStats._AC_TYPES.keys() if material in BaseStats._AC_TYPES[key])
        return Defaults.ArmorClassBase

    @staticmethod
    def get_difficulty_class(item):
        item_stats = item._get_stats()
        if BaseStats._DIFFICULTY_CLASS in item_stats._STATS[item.__class__].keys():
            return item_stats._STATS[item.__class__][BaseStats._DIFFICULTY_CLASS]
        else:
            return Difficulty.Easy
    
    @staticmethod
    def get_weight(item): return float(item._get_stats()._STATS[item.__class__][BaseStats._WEIGHT])
    @staticmethod
    def get_cost(item): return float(item._get_stats()._STATS[item.__class__][BaseStats._COST])
    @staticmethod
    def get_skill_modifiers(item):
        if BaseStats._SKILL_MODIFIERS in item._get_stats()._STATS[item.__class__].keys():
            return item._get_stats()._STATS[item.__class__][BaseStats._SKILL_MODIFIERS]
        else: return {}
    @staticmethod
    def get_attribute_modifiers(item):
        if BaseStats._ATTR_MODIFIERS in item._get_stats()._STATS[item.__class__].keys():
            return item._get_stats()._STATS[item.__class__][BaseStats._ATTR_MODIFIERS]
        else: return {}
    @staticmethod
    def get_matches(item):
        return item._get_stats()._STATS[item.__class__][BaseStats._NAME_MATCHES]


class Bonuses(object):
    @property
    def class_name(self): return self.__class__.__name__

    def __init__(self, stats):
        self.__bonuses = {}
        if stats:
            mods = stats.get_attribute_modifiers(self)
            for key in mods:
                self.add_bonus('ATTR_'+key, mods[key][0], mods[key][1])
            mods = stats.get_skill_modifiers(self)
            for key in mods:
                self.add_bonus('SKILLS_'+key, mods[key][0], mods[key][1])

    def add_bonus(self,id,attr,adjustment):
        adj = {}
        adj['key'] = attr
        adj['value'] = adjustment
        self.__bonuses[id] = adj

    def get_bonuses(self): return self.__bonuses

    def remove_bonus(self,id):
        if id in self.__bonuses.keys():
            del self.__bonuses[id]

    def get_bonus_value(self,attr):
        matched = filter(lambda x: x['key'] == attr, self.__bonuses.values())
        return sum(map(lambda x: x['value'], matched))

