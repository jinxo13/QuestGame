class Observable(object):
    def __init__(self):
        self.__observers = []
    
    def register_observer(self, observer):
        self.__observers.append(observer)
    
    def notify_observers(self, *args, **kwargs):
        for observer in self.__observers:
            observer.notify(self, *args, **kwargs)

class Observer(object):
    def __init__(self, observable):
        observable.register_observer(self)
    
    def notify(self, observable, *args, **kwargs):
        if args[0] == 'LOG':
            print(args[1])

class BaseStats(object):
    _NAME = 100
    _WEIGHT = 101
    _COST = 102
    _ATTR_MODIFIERS = 103
    _AC_CLASS = 104
    _SKILL_MODIFIERS = 105

    @staticmethod
    def get_name(item): return item._get_stats()[item.__class__][BaseStats._NAME]
    @staticmethod
    def get_ac_class(item):
        if BaseStats._AC_CLASS in item._get_stats()[item.__class__].keys():
            return item._get_stats()[item.__class__][BaseStats._AC_CLASS]
        else:
            return 0
    @staticmethod
    def get_weight(item): return item._get_stats()[item.__class__][BaseStats._WEIGHT]
    @staticmethod
    def get_cost(item): return item._get_stats()[item.__class__][BaseStats._COST]
    @staticmethod
    def get_skill_modifiers(item):
        if BaseStats._SKILL_MODIFIERS in item._get_stats()[item.__class__].keys():
            return item._get_stats()[item.__class__][BaseStats._SKILL_MODIFIERS]
        else: return {}
    @staticmethod
    def get_attribute_modifiers(item):
        if BaseStats._ATTR_MODIFIERS in item._get_stats()[item.__class__].keys():
            return item._get_stats()[item.__class__][BaseStats._ATTR_MODIFIERS]
        else: return {}


class Modifiers(object):
    @property
    def class_name(self): return self.__class__.__name__

    def __init__(self, stats):
        self.__modifiers = {}
        if stats:
            mods = stats.get_attribute_modifiers(self)
            for key in mods:
                self.add_modifier('ATTR_'+key, mods[key][0], mods[key][1])
            mods = stats.get_skill_modifiers(self)
            for key in mods:
                self.add_modifier('SKILLS_'+key, mods[key][0], mods[key][1])

    def add_modifier(self,id,attr,adjustment):
        adj = {}
        adj['key'] = attr
        adj['value'] = adjustment
        self.__modifiers[id] = adj

    def get_modifiers(self): return self.__modifiers

    def remove_modifier(self,id):
        if id in self.__modifiers.keys():
            del self.__modifiers[id]

    def get_modifier_value(self,attr):
        val = 0
        for k in self.__modifiers:
            adj = self.__modifiers[k]
            if (adj['key'] == attr):
                val = val + adj['value']
        return val

