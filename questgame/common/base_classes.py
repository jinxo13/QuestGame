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
    _AC_CLASS = 104
    _SKILL_MODIFIERS = 105
    _NAME_MATCHES = 106

    @staticmethod
    def get_name(item): return item._get_stats()._STATS[item.__class__][BaseStats._NAME]
    @staticmethod
    def get_ac_class(item):
        if BaseStats._AC_CLASS in item._get_stats()._STATS[item.__class__].keys():
            return item._get_stats()._STATS[item.__class__][BaseStats._AC_CLASS]
        else:
            return item._get_stats().get_ac_class(item)
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

