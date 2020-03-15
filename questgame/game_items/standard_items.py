﻿from questgame.common.base_classes import Observable
from questgame.game_items.items import Item
from questgame.game_items import spells, items
from questgame.players import skills
from questgame.common.rules import GameRules
from questgame.interface.alexa.utils import ReplyHelpers
import copy

class Inventory(object):
    """Player inventory"""
    def __init__(self, player):
        self.__contents = []
        self.__weight = 0.0
        self.__count = 0
        self.__money = 0
        self.__player = player
    
    @property
    def money(self): return round(self.__money,2)

    def __get_money(self):
        amount = round(self.__money,2)
        gold_count = amount // 1
        silver_count = round((amount - gold_count)*10,2) // 1
        copper_count = round((amount - gold_count - silver_count/10)*100,2) // 1
        return items.Gold(gold_count), items.Silver(silver_count), items.Copper(copper_count)

    @property
    def items(self):
        result = []
        for itm in self.__contents:
            result.append(itm)
        gold, silver, copper = self.__get_money()
        if gold.count != 0: result.append(gold)
        if silver.count != 0: result.append(silver)
        if copper.count != 0: result.append(copper)
        return result

    def contains(self, item):
        return not self.get_item(item) is None

    def find_ammo(self, ammo_class):
        best_ammo = None
        for itm in self.__contents:
            if isinstance(itm, ammo_class):
                if best_ammo is None:
                    best_ammo = itm
                else:
                    if itm.cost > best_ammo.cost:
                        best_ammo = itm
        if best_ammo: return best_ammo
        return None

    @property
    def weight(self):
        return round(self.__weight,3)

    @property
    def count(self): return self.__count

    def get_item(self, item):
        for itm in self.items:
            if itm.__class__ == item.__class__: return itm
        return None

    def count_items(self,item):
        itm = self.get_item(item)
        if itm is None: return 0
        return itm.count

    def remove_money(self, amount):
        start_state = self.__player.is_encumbered
        gold, silver, copper = self.__get_money()
        self.__weight = min(0.0, self.__weight - gold.weight - silver.weight - copper.weight)
        self.__count = min(0.0, self.__count - gold.count - silver.count - copper.count)
        self.__money = self.__money - amount
        gold, silver, copper = self.__get_money()
        self.__weight = self.__weight + gold.weight + silver.weight + copper.weight
        self.__count = self.__count + gold.count + silver.count + copper.count
        end_state = self.__player.is_encumbered
        if (start_state != end_state): self.__player._set_encumbered()
        return True

    def add_money(self, amount):
        return self.remove_money(-amount)

    def add(self, item):
        if isinstance(item, items.Money):
            self.add_money(item.cost)
            return True

        start_state = self.__player.is_encumbered
        itm = self.get_item(item)
        if itm is None:
            #Take a copy
            #itm = copy.copy(item)
            itm = item.create_from_state(item.get_state())
            self.__contents.append(itm)
        else:
            itm.count = itm.count + item.count
        self.__weight += item.weight
        self.__count += item.count
        end_state = self.__player.is_encumbered
        if (start_state != end_state): self.__player._set_encumbered()
        return True

    def remove(self, item):
        if isinstance(item, items.Money):
            return self.remove_money(item.cost)

        if not self.contains(item):
            #No item to remove
            return False

        start_state = self.__player.is_encumbered
        itm = self.get_item(item)
        amount = min(itm.count, item.count)
        self.__weight -= itm.single_weight * amount
        self.__count -= amount
        itm.count -= amount
        if itm.count == 0:
            self.__contents.remove(itm)
        end_state = self.__player.is_encumbered
        if (start_state != end_state): self.__player._set_unencumbered()
        return True

class OpenableItem(Observable):
    @property
    def has_been_opened(self): return self._has_been_opened
    @property
    def name(self): return self.__class__.__name__
    @property
    def is_locked(self): return self._is_locked
    @property
    def is_open(self): return self._is_open
    @property
    def is_trapped(self): return self.__trap is not None
    @property
    def spell_resistance(self): return self._spell_resistance
    @property
    def lock_resistance(self): return self._lock_resistance
    @property
    def trap(self): return self.__trap

    def set_locked(self, locked):
        self._is_locked = locked

    def get_key(self):
        return items.ItemStats.get_key(self._key_id)

    def __init__(self, key_id=None, spell_resistance=10, lock_resistance=10, is_open=False):
        super(OpenableItem, self).__init__()
        self._key_id = key_id
        self._is_locked = (key_id is not None)
        self._spell_resistance = spell_resistance
        self._lock_resistance = lock_resistance
        self._is_open = is_open
        self._has_been_opened = is_open
        self.__trap = None

    def set_trap(self, trap):
        self.__trap = trap
        self.notify_observers_log('Trap {} set on {}'.format(trap.class_name, self.name))

    def check_trapped(self, player):
        pass

    def unlock_with_key(self, key, player):
        if not self.is_locked:
            self.notify_observers_log('{} is not locked'.format(self.name))
            return
        if key.id == self._key_id:
            self._is_locked = False
            self.notify_observers_log('{} is unlocked'.format(self.name))
        else:
            #Wrong key
            self.notify_observers_log('Wrong key used for {}'.format(self.name))

    def unlock_with_pick(self, player):
        if not self.is_locked:
            self.notify_observers_log('{} is not locked'.format(self.name))
            self.notify_observers_reply(ReplyHelpers.render_room_template('not_locked', item=self.name))
            return
        if not player.can_picklock():
            self.notify_observers_reply(ReplyHelpers.render_room_template('no_lockpick_ability'))
        else:
            #pick lock
            skill_roll = GameRules.roll_skill_check(player, skills.LockPicking())
            if skill_roll.total >= self.lock_resistance:
                self._is_locked = False
                self.notify_observers_reply(ReplyHelpers.render_room_template('picklock_success', item=self.name))
            else:
                self.notify_observers_reply(ReplyHelpers.render_room_template('picklock_fail', item=self.name))

    def unlock_with_spell(self, spell, player):
        if not self.is_locked:
            self.notify_observers_log('{} is not locked'.format(self.name))
            self.notify_observers_reply(ReplyHelpers.render_room_template('not_locked', item=self.name))
            return
        if spell.__class__ == spells.UnlockSpell:
            self._is_locked = False
            self.notify_observers_log('{} is unlocked'.format(self.name))
            self.notify_observers_reply(ReplyHelpers.render_room_template('spell_success', action='unlocked', target_name=self.name))
        else:
            #Wrong spell
            self.notify_observers_log('Wrong spell used for {}'.format(self.name))

    def lock_with_key(self, key, player):
        if self.is_locked:
            self.notify_observers_log('{} is already locked'.format(self.name))
            self.notify_observers_reply(ReplyHelpers.render_room_template('already_locked', item=self.name))
            return
        if self.is_open:
            self.notify_observers_log("{} can't be locked it's open".format(self.name))
            return

        if key.id == self._key_id:
            self._is_locked = True
            self.notify_observers_log('{} is locked'.format(self.name))
        else:
            self.notify_observers_log('Wrong key used for {}'.format(self.name))

    def lock_with_spell(self, spell, player):
        if self.is_locked:
            self.notify_observers_log('{} is already locked'.format(self.name))
            self.notify_observers_reply(ReplyHelpers.render_room_template('already_locked', item=self.name))
            return
        if self.is_open:
            self.notify_observers_log("{} can't be locked it's open".format(self.name))
            return
        if spell.__class__ == spells.LockSpell:
            self._is_locked = True
            self.notify_observers_log('{} is locked'.format(self.name))
        else:
            self.notify_observers_log('Wrong spell used for {}'.format(self.name))

    def open_with_spell(self, spell, player):
        if spell.__class__ != spells.OpenSpell:
            self.notify_observers_log('Wrong spell used for {}'.format(self.name))
        else:
            return self.open(player, using_spell=True)

    def open(self, player, using_spell=False):
        if self.is_open:
            self.notify_observers_log('{} is already open'.format(self.name))
            self.notify_observers_reply(ReplyHelpers.render_room_template('already_open', item=self.name))
            self.on_open(player)
            return
        
        if self.is_locked:
            self.notify_observers_log('{} is locked'.format(self.name))
            if using_spell:
                self.notify_observers_reply(ReplyHelpers.render_room_template('locked_spell', item=self.name))
            else:
                self.notify_observers_reply(ReplyHelpers.render_room_template('locked', item=self.name))
            return
        
        if self.is_trapped:
            self.__trap.trigger(player)

        self._is_open = True
        self._has_been_opened = True
        self.notify_observers_reply(ReplyHelpers.render_room_template('open', item=self.name))
        self.on_open(player)

    def close_with_spell(self, spell, player):
        return self.close(player, using_spell=True)

    def close(self, player, using_spell=False, reply=True):
        if not self.is_open:
            self.notify_observers_log( '{} is already closed'.format(self.name))
            self.notify_observers_reply(ReplyHelpers.render_room_template('already_closed', item=self.name))
            return
        if reply:
            if using_spell:
                self.notify_observers_reply(ReplyHelpers.render_room_template('close', item=self.name))
            else:
                self.notify_observers_reply(ReplyHelpers.render_room_template('close', item=self.name))
        self._is_open = False
        self.on_close(player)

    def on_open(self, player): return True
    def on_close(self, player): return True
    def on_lock(self, player): return True
    def on_unlock(self, player): return True



