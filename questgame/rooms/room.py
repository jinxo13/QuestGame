from questgame.interface.alexa.utils import ReplyHelpers, QuestGameNormalReply, QuestGameReply
from questgame.game_items import items, standard_items, weapons, armor, potions, spells
from questgame.common.base_classes import Observable, Observer
import json
from questgame.common.utils import Helpers
from questgame.common.base_classes import BaseStats
from questgame.common.rules import GameRules
from questgame.players import players
from questgame.players.players import Actions

class Keys:
    CELLROOM_DOOR_KEY = 1

class Direction:
    NORTH = 1
    EAST = 2
    SOUTH = 3
    WEST = 4

class RoomItem(Observable):
    @property
    def description(self):
        try:
            return RoomStats.get_matches(self.room, self.name)[0]
        except:
            return self.name
    def get_state(self):
        result = {}
        result['class'] = self.__class__.__name__
        result['module'] = self.__module__
        result['state'] = json.dumps(self.__state)
        result['name'] = self.__name
        return result

    def throw_strike(self, weapon, attacker):
        #Hit by thrown object
        #TODO: Determine if hit then action
        return True

    def cast(self, spell, caster):
        #Hit by thrown object
        #TODO: Determine if hit then action
        return True

    @staticmethod
    def create_from_state(room, state):
        cls = Helpers.class_for_name(state['module'],state['class'])
        inst = cls(room, state['name'])
        inst.__state = json.loads(state['state'])
        return inst

    @property
    def name(self): return self.__name
    @property
    def save_state(self): return self.__save_state
    @property
    def is_hidden(self): return self._get_state('is_hidden')
    def set_found(self): self._set_state('is_hidden', False)

    def _set_state(self, key, value): self.__state[key] = value
    def _get_state(self, key): return self.__state[key]

    def __init__(self, room, name, is_hidden=False, save_state=True):
        self.__name = name
        self.room = room
        self.room.add_item(self)
        self.__state = {}
        self.__state['is_hidden'] = is_hidden
        self.__save_state = save_state

    def is_match(self, text):
        return text in RoomStats.get_matches(self.room, self.name)

class SearchableItem(RoomItem):
    @property
    def is_empty(self): return len(self.__items) == 0
    def __init__(self, room, name, items=[], is_hidden=False):
        RoomItem.__init__(self, room, name, is_hidden)
        self.__items = []
        for itm in items:
            self.__items.append(itm)

    def get_state(self):
        result = RoomItem.get_state(self)
        result['items'] = []
        for item in self.__items:
            result['items'].append(item.get_state())
        return result

    @staticmethod
    def create_from_state(room, state):
        inst = RoomItem.create_from_state(room, state)
        inst.__items = []
        for item_state in state['items']:
            inst.__items.append(items.Item.create_from_state(item_state))
        return inst

    def search(self):
        result = self.__items
        self.__items = []
        return result

    def add_item(self, item):
        if item not in self.__items:
            self.__items.append(item)
            self.notify_observers_log('Item {} added to {}'.format(item.name, self.name))

    def remove_item(self, item):
        if item in self.__items:
            self.__items.remove(item)
            self.notify_observers_log('Item {} removed from {}'.format(item.name, self.name))

class RoomOpenableItem(RoomItem, standard_items.OpenableItem):
    
    def __init__(self, room, name, is_open = False, key_id=None, lock_resistance=10, spell_resistance=10, is_hidden=False):
        standard_items.OpenableItem.__init__(self, key_id=key_id, is_open=is_open, spell_resistance=spell_resistance, lock_resistance=lock_resistance)
        RoomItem.__init__(self, room, name, is_hidden)
    
    def get_state(self):
        self._set_state('is_open',self._is_open)
        self._set_state('has_been_opened',self._has_been_opened)
        self._set_state('is_locked',self._is_locked)
        self._set_state('key_id',self._key_id)
        self._set_state('spell_resistance',self._spell_resistance)
        self._set_state('lock_resistance',self._lock_resistance)
        return RoomItem.get_state(self)

    @staticmethod
    def create_from_state(room, state):
        inst = RoomItem.create_from_state(room, state)
        inst._key_id = inst._get_state('key_id')
        inst._is_locked = inst._get_state('is_locked')
        inst._spell_resistance = inst._get_state('spell_resistance')
        inst._lock_resistance = inst._get_state('lock_resistance')
        inst._is_open = inst._get_state('is_open')
        inst._has_been_opened = inst._get_state('has_been_opened')
        return inst

class Chest(RoomOpenableItem, SearchableItem):
    """Yip it's a chest...."""
    def __init__(self, room, name='chest', items=[], key_id=None, is_hidden=False, spell_resistance=10, lock_resistance=10):
        SearchableItem.__init__(self, room=room, name=name, items=items, is_hidden=is_hidden)
        RoomOpenableItem.__init__(self, room=room, name=name, key_id=key_id, spell_resistance=spell_resistance, lock_resistance=lock_resistance, is_open=False)

class Door(RoomOpenableItem):
    def __init__(self, room, name, is_open = False, key_id = None, lock_resistance = 10, spell_resistance = 10, is_hidden = False):
        super(Door, self).__init__(room, name, is_open, key_id, lock_resistance, spell_resistance, is_hidden)

    def open(self, player):
        if self.is_open:
            self.notify_observers_reply(ReplyHelpers.render_room_template('door_already_open'))
            return
        return RoomOpenableItem.open(self, player)

    def on_open(self, player):
        self.room.exit(self) 
        self.close(player, reply=False)

class Floor(RoomItem):
    def __init__(self, room):
        super(Floor, self).__init__(room, 'floor', save_state=False)
class Walls(RoomItem):
    def __init__(self, room):
        super(Walls, self).__init__(room, 'walls', save_state=False)

class Room(Observable):
    """Describes a place/room"""
    @property
    def name(self): return self.__class__.__name__
    @property
    def player(self): return self.__player
    @property
    def is_floor_searched(self): return self._get_state('floor_searched') == True
    @property
    def is_room_searched(self): return self._get_state('room_searched') == True

    def get_state(self):
        result = {}
        result['class'] = self.__class__.__name__
        result['module'] = self.__module__
        result['items'] = []
        result['floor_items'] = []
        result['monsters'] = []
        result['state'] = json.dumps(self.__state)
        for item in self._room_items:
            if item.save_state:
                result['items'].append(item.get_state())
        for item in self._floor_items: 
            result['floor_items'].append(item.get_state())
        for item in self._monsters:
            result['monsters'].append(item.get_state())
        return result

    @staticmethod
    def create_from_state(state, player):
        cls = Helpers.class_for_name(state['module'],state['class'])
        inst = cls(player,load_from_state=True)
        for item_state in state['items']:
            cls = Helpers.class_for_name(item_state['module'],item_state['class'])
            inst._room_items.append(cls.create_from_state(inst, item_state))
        for item_state in state['floor_items']:
            cls = Helpers.class_for_name(item_state['module'],item_state['class'])
            inst._floor_items.append(cls.create_from_state(item_state))
        for item_state in state['monsters']:
            inst._monsters.append(players.Player.create_from_state(item_state))
        inst.__state = json.loads(state['state'])
        return inst

    def get_to_room(self, door):
        return RoomStats.get_to_room_by_door(self, door)

    def exit(self, door):
        new_room_cls = self.get_to_room(door)
        from alexa_control import game_manager
        user = game_manager.get_user(self.user_id)
        room_state = user.load_room(new_room_cls.__name__)
        if room_state:
            new_room = Room.create_from_state(room_state, self.player)
        else:
            new_room = new_room_cls(self.player)
        user.save_room()
        user.set_room(new_room)
        door.notify_observers_reply(new_room.enter().prompt_text)

    def buy(self, item, amount):
        #Buy an item
        floor_text = self.__get_room_text()[1]
        return ReplyHelpers.render_room_template('buy_cannot', floor_text=floor_text)

    def sell(self, item, amount):
        #Buy an item
        floor_text = self.__get_room_text()[1]
        return ReplyHelpers.render_room_template('sell_cannot', floor_text=floor_text)

    def whats_for_sale(self):
        #Buy an item
        floor_text = self.__get_room_text()[1]
        return ReplyHelpers.render_room_template('sale_cannot', floor_text=floor_text)

    def reply_no(self):
        floor_text = self.__get_room_text()[1]
        return ReplyHelpers.render_room_template('no', floor_text=floor_text)

    def reply_yes(self):
        floor_text = self.__get_room_text()[1]
        return ReplyHelpers.render_room_template('yes', floor_text=floor_text)

    def __list_items_reply(self, items, pickup=False, player=None):
        result = ''
        i = 0
        for item in items:
            i += 1
            if i == 1:
                result += ' ' + ReplyHelpers.render_room_template('found_items',item=item.text_prefix + ' ' + item.description)
            elif i == len(items):
                result += ' and {} {}.'.format(item.text_prefix, item.description)
            else:
                result += ', {}'.format(item.description)
        if pickup:
            with Observer(player) as ob:
                for item in items:
                    player.pickup(item)
            result += self.__build_reply(ob)
        if i==0:
            result += ' ' + ReplyHelpers.render_room_template('found_nothing')
        return result

    def on_search_floor(self): pass
    def on_search_room(self): pass
    def on_search_item(self, item, found_items): pass

    def __search_floor(self):
        #item = self.get_room_item_by_name('floor')
        self.on_search_floor()
        floor_text = self.__get_room_text()[1]
        result = ReplyHelpers.render_room_template('search_item',item=floor_text)
        result += ' ' + self.__list_items_reply(self._floor_items, pickup=True, player=self.player)
            
        mon_results = self.__check_for_bodies()
        self._set_state('floor_searched', True)
        return result + ' ' + mon_results

    def search(self, item=None, item_text=None):
        #Search floor
        if isinstance(item, Floor): return self.__search_floor()
        
        #Search room or walls
        if (item_text is None or item_text in ['room','area']) or isinstance(item, Walls):
            self._set_state('room_searched', True)
            self.on_search_room()
            floor_items = ''
            if len(self._floor_items) > 0:
                floor_text = self.__get_room_text()[1]
                floor_items = ReplyHelpers.render_room_template('items_on_floor',floor_text=floor_text)
            return ReplyHelpers.render_room_template('{}_search'.format(self.name.lower())) + ' ' + floor_items + ' ' + self.__check_for_bodies()
        
        #Search bodies
        if isinstance(item, players.Player):
            monster = item
            if monster.is_looted:
                return ReplyHelpers.render_action_template('monster_looted',monster_name=monster.class_name)
            found_items = self.player.loot_body(monster)
            result = ReplyHelpers.render_room_template('search_item',item=monster.class_name)
            result += ' ' + self.__list_items_reply(found_items, pickup=False)

        #Search items
        elif isinstance(item, SearchableItem):
            found_items = item.search()
            result = ReplyHelpers.render_room_template('search_item',item=item.description)
            result += ' ' + self.__list_items_reply(found_items, pickup=True, player=self.player)
        else:
            return ReplyHelpers.render_room_template('item_not_searchable')

        self.on_search_item(item, found_items)
        return result

    def __check_for_bodies(self):
        monster_count, monster_names = self.get_dead_monsters_list()
        floor_text = self.__get_room_text()[1]
        mon_results = ''
        if monster_count > 1:
            mon_results = ReplyHelpers.render_room_template('dead_bodies', floor_text=floor_text, monster_names=monster_names)
        elif monster_count == 1:
            mon_results = ReplyHelpers.render_room_template('dead_body', floor_text=floor_text, monster_names=monster_names)
        return mon_results

    def enter(self):
        self.player._end_battle()
        monster_result = self.__check_for_monster()
        body_result = self.__check_for_bodies()
        if monster_result != '':
            reply_text = ReplyHelpers.render_room_template('{}_enter'.format(self.name.lower())) + ' ' + monster_result
        else:
            reply_text = ReplyHelpers.render_room_template('{}_enter'.format(self.name.lower())) + ' ' + body_result
        return QuestGameNormalReply(self, reply_text)

    def get_room_item_by_name(self, name):
        for item in self._room_items:
            if item.name == name: return item
        for item in self._floor_items:
            if item.name == name: return item
        return None

    def get_room_item_by_text(self, item_text):
        for item in self._room_items:
            if item.is_match(item_text): return item
        for item in self._floor_items:
            if item.is_match(item_text): return item
        #Match any bodies
        for m in self.get_dead_monsters():
            if m.is_match(item_text): return m
        return None

    def add_monster(self, monster):
        self._monsters.append(monster)
        self.notify_observers_log('Monster {} added to {}'.format(monster.__class__.__name__, self.name))

    def add_item(self, item):
        item.room = self
        self._room_items.append(item)
        self.notify_observers_log('Item {} added to {}'.format(item.__class__.__name__, self.name))

    def get_item(self, name):
        for item in self._room_items:
            if item.name == name: return item
        return None

    def remove_item(self, item):
        if item in self._room_items:
            self._room_items.remove(item)
            self.notify_observers_log('Item {} removed from {}'.format(item.__class__.__name__, self.name))

    def add_floor_item(self, item):
        self._floor_items.append(item)
        self.notify_observers_log('Item {} added to floor of {}'.format(item.__class__.__name__, self.name))

    def remove_floor_item(self, item):
        if item in self._floor_items:
            self._floor_items.remove(item)
            self.notify_observers_log('Item {} removed from floor of {}'.format(item.__class__.__name__, self.name))

    def _add_action_override(self, action, item_name, new_action):
        key = str(action)+'_'+item_name
        self.__action_overrides[key] = new_action

    def get_action_override(self, action, item):
        if item is None or not isinstance(item, RoomItem): return action
        key = str(action)+'_'+item.name
        if key in self.__action_overrides:
            return self.__action_overrides[key]
        return action

    def __init__(self, player):
        super(Room, self).__init__()
        self._room_items = []
        self._floor_items = []
        self._monsters = []
        self.__player = player
        self.__action_overrides = {}
        self.__state = {}
        self._set_state('floor_searched', False)
        self._set_state('room_searched', False)
        self.user_id = ''
        self.save_game = ''

    def _set_state(self, key, value): self.__state[key] = value
    def _get_state(self, key): return self.__state[key]

    def what_can_user_do(self):

        if self.player.is_in_battle:
            return ReplyHelpers.render_common_template('what')

        result = ''
        room_text, floor_text = self.__get_room_text()

        #1. Search dead body
        monster_count, monster_names = self.get_dead_monsters_list(not_looted=True, divider='or')
        if monster_count >= 1:
            result = ReplyHelpers.render_room_template('search_dead_bodies', floor_text=floor_text, monster_names=monster_names)

        #2. Search room
        elif not self.is_room_searched:
            result = ReplyHelpers.render_room_template('search_room', room=room_text)
        
        else:
            #3. Search items
            for item in self._room_items:
                if item.is_hidden: continue
                if isinstance(item, standard_items.OpenableItem):
                    if item.has_been_opened: continue
                    result = ReplyHelpers.render_room_template('room_options', option='open', item=item.description)
                    break

                elif isinstance(item, SearchableItem):
                    if item.is_empty: continue
                    result = ReplyHelpers.render_room_template('room_options', option='search', item=item.description)
                    break
        if result == '':
            result = ReplyHelpers.render_room_template('room_no_options', room_text=room_text)
        return result

    def open(self, item):
        if isinstance(item, RoomOpenableItem):
            with Observer(item) as ob:
                item.open(self.__player)
                return self.__build_reply(ob)
        else:
            return ReplyHelpers.try_render_room_template(self, item, 'open_cannot')

    def pull(self, item):
        with Observer(item) as ob:
            item.pull(self.__player)
            return self.__build_reply(ob)

    def push(self, item):
        with Observer(item) as ob:
            item.push(self.__player)
            return self.__build_reply(ob)

    def close(self, item):
        with Observer(item) as ob:
            item.close(self.__player)
            return self.__build_reply(ob)

    def pickup(self, item):
        with Observer(item) as ob:
            if self.__player.pickup(item):
                self._floor_items.remove(item)
            return ReplyHelpers.render_room_template('pickup_item', item=item.description) + ' ' + self.__build_reply(ob)

    def drop(self, item):
        if self.__player.drop(item):
            self._floor_items.append(item)
        return ReplyHelpers.render_room_template('drop_item', item=item.description)

    def describe(self, item):
        if isinstance(item, players.Monster):
            monster = item
            return ReplyHelpers.render_descr_template('descr_{}'.format(monster.class_name.lower()), hit_points=monster.hit_points)
        return ReplyHelpers.render_descr_template('descr_{}'.format(item.name.lower()))

    def eat(self, item):
        if not isinstance(item, items.Food):
            return ReplyHelpers.render_action_template('eat_cannot', item_text=item.description)
        with Observer(self.player) as ob:
            self.player.eat(item)
            return self.__build_reply(ob)

    def drink(self, item):
        with Observer(self.player) as ob:
            self.player.drink(item)
            return self.__build_reply(ob)

    def unlock(self, item):
        with Observer(item) as ob:
            key = item.get_key()
            if self.__player.is_carrying(key):
                item.unlock_with_key(self.__player)
            elif self.__player.can_picklock():
                item.unlock_with_pick(self.__player)
            elif self.__player.can_cast_spell(spells.UnlockSpell()):
                item.unlock_with_spell(spells.UnlockSpell(), self.__player)
            else:
                return ReplyHelpers.render_room_template('nothing_to_unlock_item', item=item.description)
            return self.__build_reply(ob)

    def lock(self, item):
        with Observer(item) as ob:
            key = item.get_key()
            if self.__player.is_carrying(key):
                item.lock_with_key(self.__player)
            elif self.__player.can_cast_spell(spells.LockSpell()):
                item.lock_with_spell(spells.LockSpell(), self.__player)
            else:
                return ReplyHelpers.render_room_template('nothing_to_lock_item', item=item.description)
            return self.__build_reply(ob)

    def strike(self, target):
        with Observer(self.player) as ob:
            self.player.strike(target)
            #TODO: This doesn't look right
            if not target.is_dead:
                target.strike(self.player)
            return self.__build_reply(ob)

    def shoot(self, target):
        with Observer(self.player) as ob:
            self.player.shoot(target)
            #TODO: This doesn't look right
            if not target.is_dead:
                target.strike(self.player)
            return self.__build_reply(ob)

    def cast(self, spell_text, target):
        spell = spells.SpellStats.get_spell_by_text(spell_text)
        if not spell:
            return ReplyHelpers.render_action_template('spell_cannot')

        with Observer(self.player) as ob:
            if not self.player.can_cast_spell(spell):
                return ReplyHelpers.render_action_template('spell_cannot_cast',spell_name=spell.description) + self.__build_reply(ob)
        
            result = ''
            self.player.cast(spell, target)
        
            #You attacked a poor monster
            if isinstance(target, players.Monster):
                target.strike(self.player)
            result += ' ' + self.__build_reply(ob)
            return result

    def where(self):
        return ReplyHelpers.render_room_template('{}_enter'.format(self.name.lower()))

    def throw(self, item, target_text):
        
        with Observer(self.player) as ob:
            if not self.player.is_carrying(item):
                self.player.notify_observers_reply('not_carrying', template=ReplyHelpers.TEMPLATE_ACTION, action=Actions.get_action_text(Actions.THROW), item_prefix=item.text_prefix, item_text=item.description)
                return self.__build_reply(ob)

        target = None
        if target_text is None:
            target = self.get_next_monster()
        else:
            for m in self.get_monsters():
                if m.is_match(target_text):
                    target = m
                    break
        #Ok probably room item
        if not target:
            target = self.get_room_item_by_text(target_text)
        if not target:
            return ReplyHelpers.render_action_template('no_such_target', item_text=item.description)

        #Either throw at a room item or a monster
        is_monster = isinstance(target, players.Monster)
        is_player = isinstance(target, players.Player) and not is_monster
        is_weapon = isinstance(item, weapons.Weapon)
        is_item = isinstance(target, items.Item) or isinstance(target, RoomItem)

        floor_text = self.__get_room_text()[1]
        with Observer(self.player) as ob:
            is_hit = self.player.throw(item, target)

            if is_hit and is_item:
                self.player.notify_observers_reply('throw_item_hit', template=ReplyHelpers.TEMPLATE_ACTION, item_text=item.description, target_text=target.description, floor_text=floor_text)
            elif is_item:
                self.player.notify_observers_reply('throw_item_miss', template=ReplyHelpers.TEMPLATE_ACTION, item_text=item.description, target_text=target.description, floor_text=floor_text)

            if is_hit and is_monster and is_weapon:
                #Hit and lodged in monster
                if not GameRules.is_thrown_item_lost():
                    target.pickup(item)
            elif is_hit and is_player:
                #Hit and lodged in player
                pass
            else:
                #Miss or hit and on floor
                if not GameRules.is_thrown_item_lost():
                    self.add_floor_item(item.one_of())

            if is_monster and is_weapon and not target.is_dead:
                target.strike(self.player)

            return self.__build_reply(ob)

    def count_money(self):
        carried_gold = self.__player.inventory.get_item(items.Gold())
        carried_silver = self.__player.inventory.get_item(items.Silver())
        carried_copper = self.__player.inventory.get_item(items.Copper())
        if carried_gold + carried_silver + carried_copper > 0:
            result = ReplyHelpers.render_action_template('money_have')
        else:
            result = ReplyHelpers.render_action_template('money_none')
        if carried_gold > 0:
            result += ' ' + ReplyHelpers.render_action_template('money_count', type='gold', amount=carried_gold)
        if carried_silver > 0:
            result += ReplyHelpers.render_action_template('money_count', type='silver', amount=carried_silver)
        if carried_copper > 0:
            result += ReplyHelpers.render_action_template('money_count', type='copper', amount=carried_copper)
        return result

    def pick_lock(self, item):
        #TODO:
        #if item is None:
        #    return ReplyHelpers.render_room_template('query_picklock') + ' ' + self.build_openable_items()
        with Observer(item) as ob:
            item.unlock_with_pick(self.__player)
            return self.__build_reply(ob)

    def __get_room_text(self):
        room_text = 'room'
        floor_text = 'floor'
        if not issubclass(self.__class__, IndoorRoom):
            room_text = 'area'
            floor_text = 'ground'
        return room_text, floor_text
    def _add_monster(self, monster):
        self._monsters.append(monster)

    def get_next_monster(self):
        for m in self._monsters:
            if not m.is_dead: return m
        return None

    def get_dead_monsters_list(self, not_looted=False, divider=','):
        monster_names = ''
        i = 0
        dead_monsters = self.get_dead_monsters(not_looted)
        for m in dead_monsters:
            if not_looted and m.is_looted:
                continue
            i+=1
            if i>1:
                if len(dead_monsters) == i:
                    monster_names += ' and {}.'.format(m.description)
                else:
                    monster_names += '{} {}'.format(divider, m.description)
            else:
                monster_names = m.description
        return i, monster_names

    def get_dead_monsters(self, not_looted=False):
        result = []
        for m in self._monsters:
            if m.is_dead: result.append(m)
        return result

    def get_alive_monsters(self):
        result = []
        for m in self._monsters:
            if not m.is_dead: result.append(m)
        return result

    def get_monsters(self):
        result = []
        result.extend(self._monsters)
        return result

    def __is_openable_action(self, action, spell_text):
        openable_spells = Helpers.apply_on_all([spells.OpenSpell(), spells.CloseSpell(), spells.LockSpell(), spells.UnlockSpell()],'is_match',text=spell_text)
        return action in Actions.OPENABLE_ACTIONS or (action == Actions.CAST and True in openable_spells)

    def __is_unlock_action(self, action, spell_text):
        return action in (Actions.UNLOCK, Actions.PICK_LOCK) or (action == Actions.CAST and spells.UnlockSpell().is_match(spell_text))
    def __is_lock_action(self, action, spell_text):
        return action == Actions.LOCK or (action == Actions.CAST and spells.LockSpell().is_match(spell_text))
    def __is_open_action(self, action, spell_text):
        return action == Actions.OPEN or (action == Actions.CAST and spells.OpenSpell().is_match(spell_text))
    def __is_close_action(self, action, spell_text):
        return action == Actions.CLOSE or (action == Actions.CAST and spells.CloseSpell().is_match(spell_text))
    def __is_lock_action(self, action, spell_text):
        return action == Actions.LOCK or (action == Actions.CAST and spells.LockSpell().is_match(spell_text))

    def do_action(self, action, item_text, spell_text=None, target_text=None, amount=0):
        
        if self.player.is_in_battle and action not in Actions.ALLOWED_BATTLE_ACTIONS:
            reply_text = ReplyHelpers.render_action_template('battle_invalid_action', monster=self.get_next_monster().description)
            return QuestGameNormalReply(self, reply_text)

        item = None
        if not action in Actions.NO_ITEM_ACTIONS or item_text is not None:
            #Try and find a matching item
               
            if not item_text is None:

                if self.player.is_in_battle and action in Actions.ATTACK_ACTIONS:
                    #Look for matching monster
                    for m in self.get_monsters():
                        if m.is_match(item_text):
                            item = m
                            break
                    if item is None:
                        reply_text = ReplyHelpers.render_action_template('no_monster_to_battle')
                        return QuestGameNormalReply(self, reply_text)

                elif action == Actions.DESCRIBE:
                    #Could be in room or on player
                    item = self.get_room_item_by_text(item_text)
                    if item is None:
                        item = self.player.get_item_by_name(item_text)
                    if item is None:
                        #Look for matching monster
                        for m in self.get_monsters():
                            if m.is_match(item_text):
                                item = m
                                break
                    if item is None:
                        room_text = self.__get_room_text()[0]
                        reply_text = ReplyHelpers.render_room_template('no_such_room_item', room=room_text, action=Actions.get_action_text(action))
                        return QuestGameNormalReply(self, reply_text)

                elif action in Actions.PLAYER_ITEM_ACTIONS:
                    #Try items held by  player
                    item = self.player.get_item_by_name(item_text)
                    if item is None:
                        reply_text = ReplyHelpers.render_action_template('not_carrying_unknown', action=Actions.get_action_text(action))
                        return QuestGameNormalReply(self, reply_text)

                else:
                    #Item is in the room
                    item = self.get_room_item_by_text(item_text)
                    if item is None and not action in Actions.NO_ITEM_ACTIONS:
                        room_text = self.__get_room_text()[0]
                        reply_text = ReplyHelpers.render_room_template('no_such_room_item', room=room_text, action=Actions.get_action_text(action))
                        return QuestGameNormalReply(self, reply_text)

            if item is None:
                if self.player.is_in_battle and action in Actions.ATTACK_ACTIONS:
                    item = self.get_next_monster()
                    if item is None:
                        reply_text = ReplyHelpers.render_action_template('no_monster_to_battle')
                        return QuestGameNormalReply(self, reply_text)

                elif self.__is_openable_action(action, spell_text):
                    #Openable item
                    openable_items = []
                    for itm in self._room_items:
                        if not isinstance(itm, RoomOpenableItem):
                            continue
                        if (self.__is_lock_action(action, spell_text) and not itm.is_locked) or \
                            (self.__is_unlock_action(action, spell_text) and itm.is_locked) or \
                            (self.__is_open_action(action, spell_text) and not itm.is_open) or \
                            (self.__is_close_action(action, spell_text) and itm.is_open):
                            openable_items.append(itm)
                    if len(openable_items) == 1:
                        item = openable_items[0]
                    else:
                        reply_text = ReplyHelpers.render_room_template('select_openable_item', action=Actions.get_action_text(action), item_list=ReplyHelpers.build_list(openable_items, 'description'))
                        return QuestGameReply(reply_text, query_state=ReplyHelpers.QUERY_SELECT)

                    if item is None:
                        #Matching failed
                        reply_text = ReplyHelpers.render_room_template('no_item_provided', action=Actions.get_action_text(action))
                        return QuestGameNormalReply(self, reply_text)

                    #No item found
                    reply_text = ReplyHelpers.render_action_template('not_carrying', action=Actions.get_action_text(action), item_prefix=item.text_prefix, item_text=item.description)
                    return QuestGameNormalReply(self, reply_text)

        action = self.get_action_override(action, item)

        #Either no item required, item is carried by player, or item in room
        result_text = ''
        if action == Actions.PULL: result_text = self.pull(item)
        elif action == Actions.PUSH: result_text = self.push(item)
        elif action == Actions.SEARCH: result_text = self.search(item, item_text)
        elif action == Actions.CAST: result_text = self.cast(spell_text, item)
        elif action == Actions.THROW: result_text = self.throw(item, target_text)
        elif action == Actions.CLOSE: result_text = self.close(item)
        elif action == Actions.OPEN: result_text = self.open(item)
        elif action == Actions.LOCK: result_text = self.lock(item)
        elif action == Actions.UNLOCK: result_text = self.unlock(item)
        elif action == Actions.DESCRIBE: result_text = self.describe(item)
        elif action == Actions.NO: result_text = self.reply_no()
        elif action == Actions.YES: result_text = self.reply_yes()
        elif action == Actions.PICK_LOCK: result_text = self.pick_lock(item)
        elif action == Actions.SHOOT: result_text = self.shoot(item)
        elif action == Actions.STRIKE: result_text = self.strike(item)
        elif action == Actions.WHAT: result_text = self.what_can_user_do()
        elif action == Actions.PICKUP: result_text = self.pickup(item)
        elif action == Actions.DROP: result_text = self.drop(item)
        elif action == Actions.DRINK: result_text = self.drink(item)
        elif action == Actions.WHERE: result_text = self.where()
        elif action == Actions.EAT: result_text = self.eat(item)
        elif action == Actions.MONEY: result_text = self.count_money()
        elif action == Actions.BUY: result_text = self.buy(item_text, amount)
        elif action == Actions.SELL: result_text = self.sell(item_text, amount)
        elif action == Actions.WHAT_BUY: result_text = self.whats_for_sale()
        else:
            result_text = ReplyHelpers.render_common_template('no_action')
        
        return QuestGameNormalReply(self, result_text + ' ' + self.__check_for_monster())

    def __check_for_monster(self):
        #Has a monster appeared?
        monster = self.get_next_monster()
        result = ''
        if monster is None:
            self.player._end_battle()
        else:
            #Yikes a monster!
            if not self.player.is_in_battle:
                self.player._start_battle()
                with Observer(self.player) as ob:
                    if GameRules.roll_initiative_check(monster) > GameRules.roll_initiative_check(self.player):
                        #Monster strikes first
                        result = ReplyHelpers.render_action_template('monster_detects_you',monster_name=monster.class_name)
                        monster.strike(self.player)
                    else:
                        #Player gets to attack first
                        result = ReplyHelpers.render_action_template('monster_detected',monster_name=monster.class_name)
                    result += ' ' + self.__build_reply(ob)
        return result

    def __build_reply(self, ob):
        result = ''
        for reply in ob.replies:
            if Helpers.is_string(reply):
                result += ' ' + reply
                continue
            args = reply['args']
            key = reply['key']
            item = None
            if 'item' in args.keys():
                item_name = args['item']
                item = self.get_room_item_by_name(item_name)
            template = args['template']
            if 'attacker_name' in args.keys():
                if args['attacker_name'].lower() in ['thief','ranger','fighter','mage']:
                    key = 'player_'+key
                else:
                    key = 'monster_'+key
            if template == ReplyHelpers.TEMPLATE_ACTION:
                result += ' ' + ReplyHelpers.render_action_template(key, **args)
            elif template == ReplyHelpers.TEMPLATE_ROOM:
                if item:
                    result += ' ' + ReplyHelpers.try_render_room_template(self, item, key, **args)
                else:
                    result += ' ' + ReplyHelpers.render_room_template(key, **args)
            elif template == ReplyHelpers.TEMPLATE_COMMON:
                result += ' ' + ReplyHelpers.render_common_template(key, **args)
            elif template == ReplyHelpers.TEMPLATE_DESCRIPTION:
                result += ' ' + ReplyHelpers.render_descr_template(key, **args)
        return result

class IndoorRoom(Room):
    def __init__(self, player):
        super(IndoorRoom, self).__init__(player)
        Floor(self)
        Walls(self)

class StoreRoom(Room):
    def __init__(self, player, item_classes):
        self.__item_classes = item_classes
        self.__items = []
        self.__unlimited = []
        super(StoreRoom, self).__init__(player)
    
    def is_unlimited(self, item):
        return item.__class__ in self.__unlimited

    def store_item(self, item, is_unlimited=False):
        self.__add_item(item)
        if is_unlimited and item.__class__ not in self.__unlimited:
            self.__unlimited.append(item.__class__)

    def can_sell(self, item):
        for cls in self.__item_classes:
            if isinstance(item, cls): return True
        return False

    def __add_item(self, item):
        found = False
        for itm in self.__items:
            if itm.__class__ == item.__class__:
                itm.add(item.count)
                found = True
                break
        if not found:
            itm = item.create_from_state(item.get_state(), 0)
            itm.add(item.count)
            self.__items.append(itm)

    def __remove_item(self, item):
        if self.is_unlimited(item): return
        for itm in self.__items:
            if itm.__class__ == item.__class__:
                itm.remove(item.count)
                if itm.count == 0: self.__items.remove(itm)
                break

    def buy(self, item_text, amount=1):
        #Store has item to sell
        item = None
        for itm in self.__items:
            if itm.is_match(item_text):
                item = itm.one_of()
                break

        if item == None:
            return ReplyHelpers.render_action_template('buy_no_item')
        
        item.add(amount-1)

        description = item.description
        if item.count > 1:
            description = item.description_plural

        #Can afford items
        if self.player.money < item.cost:
            return ReplyHelpers.render_action_template('buy_no_money', item_text=description)

        #Buy items
        self.player.inventory.remove_money(item.cost)
        self.__remove_item(item)
        self.player.pickup(item)
        return ReplyHelpers.render_action_template('buy_item', item_text=description)

    def sell(self, item_text, amount=1):
        item = self.player.get_item_by_name(item_text)
        if item is None:
            return ReplyHelpers.render_action_template('not_carrying_unknown', action=Actions.get_action_text(Actions.SELL))
        
        item = item.one_of()
        item.add(amount-1)

        if not self.can_sell(item):
            return ReplyHelpers.render_action_template('sell_no_item', item_prefix=item.text_prefix, item_text=item.description)

        #Has item to sell
        itm = self.player.inventory.get_item(item)
        if itm is None:
            return ReplyHelpers.render_action_template('not_carrying', action=Actions.get_action_text(Actions.SELL), item_prefix=item.text_prefix, item_text=item.description)
        
        if itm.count < item.count:
            return ReplyHelpers.render_action_template('not_carrying_enough', action=Actions.get_action_text(Actions.SELL), item_text=item.description_plural)

        description = item.description
        if item.count > 1:
            description = item.description_plural

        #Sell items
        self.player.drop(item)
        self.player.inventory.add_money(item.cost)
        self.__add_item(item)
        return ReplyHelpers.render_action_template('sell_item', item_text=description)

    def whats_for_sale(self):
        if len(self.__items) > 0:
            result = ReplyHelpers.render_room_template('sale_items')
        else:
            result = ReplyHelpers.render_room_template('sale_no_items')

        for item in self.__items:
            if self.is_unlimited(item):
                result += ' {}.'.format(item.description_plural)
            elif item.count > 1:
                result += ' {} {}.'.format(item.count, item.description_plural)
            else:
                result += ' {} {}.'.format(item.text_prefix, item.description)
        return result

class CellRoom(IndoorRoom):
    def __init__(self, player, load_from_state=False):
        super(CellRoom, self).__init__(player)

        self._add_action_override(Actions.OPEN,'loose_stone',new_action=Actions.PULL)
        self._add_action_override(Actions.PICKUP,'loose_stone',new_action=Actions.PULL)
        self._add_action_override(Actions.PULL,'door',new_action=Actions.OPEN)

        if not load_from_state:
            RoomOpenableItem(self, 'loose_stone', is_hidden=True)
            if player.is_mage: itms = [weapons.Staff(), armor.Robe()]
            elif player.is_thief: itms = [weapons.Dagger(), armor.LightArmor()]
            elif player.is_fighter: itms = [weapons.LongSword(), armor.HeavyArmor()]
            elif player.is_ranger: itms = [weapons.LongBow(), armor.LightArmor(), weapons.WoodArrow(10)]
            SearchableItem(self, 'straw', itms)
            Door(self, 'door', is_open=False, key_id=Keys.CELLROOM_DOOR_KEY, spell_resistance=5, lock_resistance=5)
            RoomItem(self, 'barred_window')
            self.add_floor_item(items.StaleBread())
            self._set_state('hidden_item_taken', False)

    def start(self):
        reply_text = ReplyHelpers.render_room_template('cellroom_start')
        return QuestGameNormalReply(self, reply_text)
    
    def on_search_room(self):
        self.get_room_item_by_name('loose_stone').set_found()

    def on_search_item(self, item, found_items):
        if item.name == 'straw' and len(found_items) > 0:
            rat = players.Rat()
            rat.inventory.add(items.StrengthRing())
            rat.inventory.add(items.LockPick())
            self._add_monster(rat)
    
    def pull(self, item):
        if item.name == 'loose_stone':
            result = ReplyHelpers.render_room_template('cellroom_pull_stone')
            if self._get_state('hidden_item_taken'):
                result += ' ' + ReplyHelpers.render_room_template('cellroom_pull_stone_empty')
            else:
                item._has_been_opened = True
                hidden_item = items.LockPick()
                if self.player.__class__ == players.Mage:
                    hidden_item = items.Scroll(spells.UnlockSpell())
                self.player.pickup(hidden_item)
                self._set_state('hidden_item_taken',True)
                result += ' ' + ReplyHelpers.render_room_template('cellroom_pull_stone_full',item_text=hidden_item.description)
        else:
            result = Room.pull(self, item)
        return result

class WeaponsRoom(StoreRoom):
    def __init__(self, player, load_from_state=False):
        super(WeaponsRoom, self).__init__(player, [weapons.Weapon, armor.Armor])

        if not load_from_state:
            door = Door(self, 'door', is_open=False, key_id=items.WeaponsRoomKey().id, spell_resistance=5, lock_resistance=5)
            door.set_locked(False)

class LinkedRoom(object):
    def __init__(self, from_room_cls, direction, to_room_cls, door_name=None):
        self.from_room_cls = from_room_cls
        self.to_room_cls = to_room_cls
        self.direction = direction
        self.door_name = door_name

class RoomStats(object):
    _MATCHES = 1
    _NAME = 2
    _CLASS = 3
    _ITEMS = 4
    _KEY = 5

    _STATS = {
        Room: {
            'floor': ['floor','ground'],
            'walls': ['walls']
            },
        CellRoom: {
            'door': ['door', 'large door', 'wooden door'],
            'loose_stone': ['loose stone', 'stone'],
            'straw': ['straw'],
            'barred_window': ['barred window','window']
            },
        WeaponsRoom: {
            'door': ['door', 'large door', 'wooden door']
            }
        }
    @staticmethod
    def get_matches(room, name):
        if name in RoomStats._STATS[room.__class__]:
            return RoomStats._STATS[room.__class__][name]
        if name in RoomStats._STATS[Room]:
            return RoomStats._STATS[Room][name]
        return []

    ################## MAP Details ###################
    _MAP = {
            LinkedRoom(from_room_cls=CellRoom, direction=Direction.EAST, to_room_cls=WeaponsRoom, door_name='door'),
            LinkedRoom(from_room_cls=WeaponsRoom, direction=Direction.WEST, to_room_cls=CellRoom, door_name='door'),
        }
    
    @staticmethod
    def get_to_room_by_direction(from_room, direction):
        for linked_room in RoomStats._MAP:
            if linked_room.from_room_cls == from_room.__class__ and linked_room.direction == direction:
                return linked_room.to_room_cls

    @staticmethod
    def get_to_room_by_door(from_room, door):
        for linked_room in RoomStats._MAP:
            if linked_room.from_room_cls == from_room.__class__ and door.is_match(linked_room.door_name):
                return linked_room.to_room_cls
        return None

