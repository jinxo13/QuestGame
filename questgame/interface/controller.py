from questgame.db import database
import logging
from questgame import rooms
from questgame.players.players import Player, character_classes
from questgame.common.errors import QuestGameError

logger = logging.getLogger()

class Actions(object):
    PUSH = 0
    PULL = 1
    SEARCH = 2
    OPEN = 3
    CLOSE= 4
    LOCK = 5
    UNLOCK = 6
    CAST = 7
    THROW = 8
    PICK_LOCK = 9
    WHERE = 10
    YES = 11
    NO = 12
    DESCRIBE = 13
    STRIKE = 14
    SHOOT = 15

class UserState(object):
    def __init__(self, user, save_name):
        self.__user_id = user
        self.__lm = LoadManager(user)
        self.state = self.__lm.get_empty_state()
        self.room = None
        self.__player = None
        self.__save_name = save_name
        self.__is_active = False

    @property
    def player(self): return self.__player
    @property
    def is_active(self): return self.__is_active

    def set_player(self, player): self.__player = player

    def save_player(self):
        try:
            self.__lm.save_player(self.__save_name, self.__player.get_state())
        except Exception, e:
            logger.exception('message')
            raise QuestGameError(QuestGameError.SAVE_PLAYER_FAILED)

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
        self.room = rooms.CellRoom()
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
            self.__lm.save_room(self.__save_name, room.name, room.state)
            return True, None
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

    def is_game_started(self, user_id): return user_id in self.__user_states.keys()

    def get_player(name_text):
        player = None
        if name.lower() == 'thief': player = Player(character_classes.Thief())
        elif name.lower() == 'mage': player = Player(character_classes.Mage())
        else: player = Player(character_classes.Thief())
        return player


    def get_user(self, user, save_name=None):
        if not user in self.__user_states.keys():
            if save_name is None:
                raise QuestGameError(QuestGameError.MISSING_SAVE_GAME_NAME)
            self.__user_states[user] = UserState(user, save_name)
        return self.__user_states[user]

    def continue_game(self, user_id):
        if not self.is_game_started(user_id):
            #Need to load a game
            raise NotImplementedError()
        user = self.get_user(user_id)
        return user.room.enter()

    def load_game(self, user_id, save_name):
        user = self.get_user(user_id, save_name)
        user.load_game()

    def start_new_game(self, user_id, player):
        """Starts a new game"""
        try:
            user = self.get_user(user_id, 'test')
            user.set_player(player)
            user.save_game()
            user.room = rooms.CellRoom()
            return user.room.start()
        except QuestGameError, e: raise e
        except Exception, e:
            logger.exception('message')
            raise QuestGameError(QuestGameError.START_NEW_GAME_FAILED)

    def perform_spell(self, user_id, spell_text, item_text=None):
        """Perform a spell"""
        room = self.get_user().room
        return room.cast(spell_text, item_text)

    def perform_throw(self, user_id, item_text, target_text):
        """Throw your toys"""
        room = self.get_user().room
        return room.throw(item_text, target_text)

    def perform_action(self, user_id, action, item_text=None):
        """Perform an action"""
        room = self.get_user().room
        if action == Actions.PULL: return room.pull(item_text)
        elif action == Actions.PUSH: return room.push(item_text)
        elif action == Actions.SEARCH: return room.search(item_text)
        elif action == Actions.CAST: raise NotImplementedError('Cast is not implemented in perform_action. Call perform_spell instead.')
        elif action == Actions.CLOSE: return room.close(item_text)
        elif action == Actions.OPEN: return room.open(item_text)
        elif action == Actions.DESCRIBE: return room.describe(item_text)
        elif action == Actions.LOCK: return room.lock(item_text)
        elif action == Actions.NO: return room.reply_no()
        elif action == Actions.YES: return room.reply_yes()
        elif action == Actions.PICK_LOCK: return room.pick_lock(item_text)
        elif action == Actions.SHOOT: return room.shoot(item_text)
        elif action == Actions.STRIKE: return room.strike(item_text)
        return helpers.render_common_template('no_action')

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

    def does_user_exist(self):
        db = database.db(self.__user)
        return db.does_user_exist()

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
        return db.get_item('{}.{}.{}'.format(save_name, LoadManager.STATE_ROOM, room_name))

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