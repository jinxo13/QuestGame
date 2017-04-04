from questgame.interface.alexa.utils import Helpers
from questgame.game_items import items, standard_items

class Room(object):
    """Describes a place/room"""
    @property
    def name(self): return self.__class__.__name__

    def get_state(self): return {}

    def __init__(self):
        pass
    #Actions
    def search(self): raise NotImplementedError()
    def pull(self, room_item):
        if type(room_item) is standard_items.Chest:
            return Helpers.render_action_template('pull_chest')
        else:
            return Helpers.render_action_template('pull_cannot')
        

class CellRoom(Room):
    def items(self): return ['loose_stone']
    def start(self): return Helpers.render_room_template('cellroom_start')
    def search(self): return Helpers.render_room_template('cellroom_search')
    def enter(self): return Helpers.render_room_template('cellroom_enter')
    def pull(self, room_item):
        if room_item is str and room_item == 'loose_stone':
            result = Helpers.render_room_template('cellroom_pull_stone')
            return result
        return Room.pull(self, room_item)

