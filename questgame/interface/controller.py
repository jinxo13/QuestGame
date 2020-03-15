from questgame.db import database
import logging
from questgame import rooms
from questgame.players.players import Thief, Mage, Fighter, Ranger, Player, Actions
from questgame.common.errors import QuestGameError

logger = logging.getLogger()

class UserState(object):
    def __init__(self, user, save_name):
        self.__user_id = user
        self.__lm = LoadManager(user)
        self.state = self.__lm.get_empty_state()
        self.__room = None
        self.__player = None
        self.__save_name = save_name
        self.__is_active = False

    @property
    def player(self): return self.__player
    @property
    def room(self): return self.__room
    @property
    def is_active(self): return self.__is_active

    def set_player(self, player): self.__player = player

    def set_room(self, room):
        self.__room = room
        room.user_id = self.__user_id

    def save_player(self):
        try:
            self.__lm.save_player(self.__save_name, self.__player.get_state())
        except Exception, e:
            logger.exception('message')
            raise QuestGameError(QuestGameError.SAVE_PLAYER_FAILED)
    def delete_game(self):
        result = self.__lm.delete_game(self.__save_name)
    def load_game(self):
        try:
            result = self.__lm.load_game(self.__save_name)
            if result is None:
                raise QuestGameError(QuestGameError.NO_SUCH_GAME)
            self.state = result
        except Exception, e:
            logger.exception('message')
            raise QuestGameError(QuestGameError.LOAD_FAILED)
        player_state = self.state[LoadManager.STATE_PLAYER]
        self.__player = Player.create_from_state(player_state)
        #TODO fix
        current_room = 'CellRoom'
        if current_room in self.state[LoadManager.STATE_ROOM]:
            room_state = self.state[LoadManager.STATE_ROOM][current_room]
            self.set_room(rooms.room.Room.create_from_state(room_state, self.__player))
        else:
            self.set_room(rooms.room.CellRoom(self.__player))

        self.__is_active = True

    def save_game(self):
        """Saves a users current game"""
        try:
            if not self.room is None:
                self.__lm.save_room(self.__save_name, self.room.name, self.room.get_state())
            self.__lm.save_game(self.__save_name, self.state)
            self.__lm.save_player(self.__save_name, self.__player.get_state())
            self.__is_active = True
        except Exception, e:
            logger.exception('message')
            raise QuestGameError(QuestGameError.SAVE_GAME_FAILED)

    def save_room(self):
        """Saves the state of the specified room"""
        try:
            self.__lm.save_room(self.__save_name, self.room.name, self.room.get_state())
            return True, None
        except Exception, e:
            logger.exception('message')
            return False, GameManager.UNKNOWN_ERROR

    def load_room(self, room_name):
        """Loads the state of the specified room"""
        try:
            return self.__lm.load_room(self.__save_name, room_name)
        except Exception, e:
            logger.exception('message')
            return False, GameManager.UNKNOWN_ERROR

class GameManager(object):
    NO_SUCH_GAME = 'no such game'
    UNKNOWN_ERROR = 'an unexpected error occurred'
    NOT_PLAYING = 'user is not currently playing'

    """Managers interactions and state"""

    def __init__(self):
        self.__user_states = {}

    def user_exit(self, user_id):
        if user_id in self.__user_states.keys():
            del self.__user_states[user_id]

    def is_game_started(self, user_id):
        """User is currently playing"""
        return user_id in self.__user_states.keys()

    def create_player(self, name_text):
        player = None
        if name_text.lower() == 'thief': player = Thief()
        elif name_text.lower() == 'mage': player = Mage()
        elif name_text.lower() == 'fighter': player = Fighter()
        elif name_text.lower() == 'ranger': player = Ranger()
        else: player = Thief()
        return player

    def get_user(self, user, save_name=None):
        if not user in self.__user_states.keys():
            if save_name is None:
                raise QuestGameError(QuestGameError.MISSING_SAVE_GAME_NAME)
            self.__user_states[user] = UserState(user, save_name)
        return self.__user_states[user]

    def continue_game(self, user_id):
        user = self.get_user(user_id)
        return user.room.enter()

    def delete_game(self, user_id, save_name):
        user = self.get_user(user_id, save_name)
        user.delete_game()
        del self.__user_states[user_id]

    def load_game(self, user_id, save_name):
        user = self.get_user(user_id, save_name)
        user.load_game()

    def start_new_game(self, user_id, player):
        """Starts a new game"""
        try:
            user = self.get_user(user_id, 'test')
            user.set_player(player)
            user.save_game()
            user.set_room(rooms.CellRoom(player))
            return user.room.start()
        except QuestGameError, e: raise e
        except Exception, e:
            logger.exception('message')
            raise QuestGameError(QuestGameError.START_NEW_GAME_FAILED)

    def perform_spell(self, user_id, spell_text, item_text=None):
        """Perform a spell"""
        user = self.get_user(user_id)
        room = user.room
        result = room.do_action(Actions.CAST, item_text, spell_text=spell_text)
        user.save_player()
        user.save_room()
        return result

    def perform_throw(self, user_id, item_text, target_text):
        """Throw your toys"""
        user = self.get_user(user_id)
        room = user.room
        result = room.do_action(Actions.THROW, item_text, target_text=target_text)
        user.save_player()
        user.save_room()
        return result

    def perform_action(self, user_id, action, item_text=None, amount=0):
        """Perform an action"""
        user = self.get_user(user_id)
        room = user.room
        result = room.do_action(action, item_text, amount=amount)
        user.save_player()
        user.save_room()
        return result

class LoadManager(object):
    """description of class"""
    STATE_ROOM = 'room_state'
    STATE_DOOR = 'door_state'
    STATE_PLAYER = 'player_state'
    __STATES = [STATE_DOOR, STATE_PLAYER, STATE_ROOM]
    
    def get_empty_state(self):
        result = {}
        for s in LoadManager.__STATES:
            result[s] = {}
        return result

    def __init__(self, user):
        self.__user = user

    def does_user_game_exist(self, save_name):
        db = database.db(self.__user)
        if not db.does_user_exist(): return False
        return not self.load_game(save_name) is None

    def delete_game(self, save_name):
        db = database.db(self.__user)
        db.delete_item(save_name)

    def save_game(self, save_name, game_state):
        db = database.db(self.__user)
        db.put_item(save_name, {})
        for state in LoadManager.__STATES:
            db.put_item('{}.{}'.format(save_name, state), game_state[state])

    def save_state(self, save_name, state_name, state):
        if state_name not in LoadManager.__STATES: raise NameError
        db = database.db(self.__user)
        db.put_item('{}.{}'.format(save_name, state_name), state)

    def save_room(self, save_name, room_name, state):
        db = database.db(self.__user)
        db.put_item('{}.{}.{}'.format(save_name, LoadManager.STATE_ROOM, room_name), state)

    def load_room(self, save_name, room_name):
        db = database.db(self.__user)
        result = self.load_state(save_name, LoadManager.STATE_ROOM)
        if result is None or room_name not in result.keys(): return None
        return result[room_name]

    def save_player(self, save_name, state):
        db = database.db(self.__user)
        db.put_item('{}.{}'.format(save_name, LoadManager.STATE_PLAYER), state)

    def load_player(self, save_name):
        db = database.db(self.__user)
        return db.get_item('{}.{}'.format(save_name, LoadManager.STATE_PLAYER))

    def load_state(self, save_name, state_name):
        if state_name not in LoadManager.__STATES: raise NameError('The specified load/save state type [{}] does not exist'.format(state_name))
        db = database.db(self.__user)
        return db.get_item('{}.{}'.format(save_name, state_name))

    def load_game(self, save_name):
        result = {}
        db = database.db(self.__user)
        for state in LoadManager.__STATES:
            result[state] = self.load_state(save_name, state)
        if result[LoadManager.STATE_ROOM] is None:
            #no such saved game
            return None
        return result