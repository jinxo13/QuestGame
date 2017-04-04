from questgame.common.base_classes import Observable
from questgame.game_items.items import Item
from questgame.game_items import spells

class Inventory(object):
    """Player inventory"""
    def __init__(self, player):
        self.__contents = {}
        self.__weight = 0
        self.__count = 0
        self.__player = player
    
    def contains(self, item):
        for cls in self.__contents.keys():
            if cls == item.__class__:
                for itm in self.__contents[cls]:
                    if itm == item:
                        return True
                        break
                break
                return False
        return False


    def find_ammo(self, ammo_class):
        best_ammo_class = None
        for cls in self.__contents.keys():
            if issubclass(cls, ammo_class):
                if best_ammo_class is None:
                    best_ammo_class = cls
                else:
                    if cls().cost > best_ammo_class().cost:
                        best_ammo_class = cls
        if best_ammo_class: return self.__contents[best_ammo_class]
        return None

    @property
    def weight(self): return self.__weight
    @property
    def count(self): return self.__count

    def count_items(self,cls):
        if not cls in self.__contents.keys(): return 0
        return len(self.__contents[cls])

    def add(self, item):
        start_state = self.__player.is_encumbered
        if not item.__class__ in self.__contents.keys():
            self.__contents[item.__class__] = []
        
        items = self.__contents[item.__class__]
        if not item in items:
            items.append(item)
            self.__weight += item.weight
            self.__count += 1
            end_state = self.__player.is_encumbered
            if (start_state != end_state): self.__player._set_encumbered()
            return True
        else:
            return False

    def remove(self, item):
        if not item.__class__ in self.__contents.keys(): return False
        start_state = self.__player.is_encumbered

        items = self.__contents[item.__class__]
        if item in items:
            items.remove(item)
            self.__weight -= item.weight
            self.__count -= 1
            end_state = self.__player.is_encumbered
            if (start_state != end_state): self.__player._set_unencumbered()
            return True

class Chest(Observable):
    """Yip it's a chest...."""
    @property
    def is_locked(self): return self.__locked
    @property
    def is_open(self): return self.__open
    @property
    def is_trapped(self): return self.__trap is not None
    @property
    def spell_resistance(self): return self.__spell_resistance
    @property
    def trap(self): return self.__trap

    def __init__(self, key_id=None, spell_resistance=10):
        super(Chest, self).__init__()
        self.__contents = []
        self.__key_id = key_id
        self.__locked = (key_id is not None)
        self.__spell_resistance = spell_resistance
        self.__open = False
        self.__trap = None

    def add_item(self, item):
        if item not in self.__contents:
            self.__contents.append(item)
            self.notify_observers('LOG','Item {} added to chest'.format(item.__class__.__name__))

    def list_items(self):
        return self.__contents

    def remove_item(self, item):
        if item in self.__contents:
            self.__contents.remove(item)
            self.notify_observers('LOG','Item {} removed from chest'.format(item.__class__.__name__))

    def set_trap(self, trap):
        self.__trap = trap
        self.notify_observers('LOG','Trap {} set on chest'.format(trap.__class__.__name__))

    def check_trapped(self, player):
        pass

    def unlock_with_key(self, key, player):
        if not self.is_locked:
            self.notify_observers('LOG','Chest is not locked')
            return
        if key.id == self.__key_id:
            self.__locked = False
            self.notify_observers('LOG','Chest is unlocked')
        else:
            #Wrong key
            self.notify_observers('LOG','Wrong key used for chest')

    def unlock_with_spell(self, spell, player):
        if not self.is_locked:
            self.notify_observers('LOG','Chest is not locked')
            return
        if spell.__class__ == spells.UnlockSpell:
            self.__locked = False
            self.notify_observers('LOG','Chest is unlocked')
        else:
            #Wrong spell
            self.notify_observers('LOG','Wrong spell used for chest')

    def lock_with_key(self, key, player):
        if self.is_locked:
            self.notify_observers('LOG','Chest is already locked')
            return
        if self.is_open:
            self.notify_observers('LOG',"Chest can't be locked it's open")
            return

        if key.id == self.__key_id:
            self.__locked = True
            self.notify_observers('LOG','Chest is locked')
        else:
            self.notify_observers('LOG','Wrong key used for chest')

    def lock_with_spell(self, spell, player):
        if self.is_locked:
            self.notify_observers('LOG','Chest is already locked')
            return
        if self.is_open:
            self.notify_observers('LOG',"Chest can't be locked it's open")
            return
        if spell.__class__ == spells.LockSpell:
            self.__locked = True
            self.notify_observers('LOG','Chest is locked')
        else:
            self.notify_observers('LOG','Wrong spell used for chest')

    def open(self, player):
        if self.is_open:
            self.notify_observers('LOG','Chest is already open')
            return
        
        if self.is_locked:
            self.notify_observers('LOG','Chest is locked')
            return
        
        if self.is_trapped:
            self.__trap.trigger(player)

        self.__open = True

    def close(self, player):
        if not self.is_open:
            self.notify_observers('LOG','Chest is already closed')
            return
        self.__open = False
