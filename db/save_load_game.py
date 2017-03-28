from db import database

class GameManager(object):
    """description of class"""
    STATE_ROOM = 'room_state'
    STATE_DOOR = 'door_state'
    STATE_PLAYER = 'player_state'
    __STATES = [STATE_DOOR, STATE_PLAYER, STATE_ROOM]
    
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
        for state in GameManager.__STATES:
            db.put_item('{}.{}'.format(save_name, state), game_state[state])

    def save_state(self, save_name, state_name, state):
        if state_name not in GameManager.__STATES: raise NameError
        db = database.db(self.__user)
        db.put_item('{}.{}'.format(save_name, state_name), state)

    def save_room(self, save_name, room_name, state):
        db = database.db(self.__user)
        db.put_item('{}.{}.{}'.format(save_name, STATE_ROOM, room_name), state)

    def load_room(self, save_name, room_name):
        db = database.db(self.__user)
        return db.get_item('{}.{}.{}'.format(save_name, STATE_ROOM, room_name))

    def load_state(self, save_name, state_name):
        if state_name not in GameManager.__STATES: raise NameError
        db = database.db(self.__user)
        return db.get_item('{}.{}'.format(save_name, state_name))

    def load_game(self, save_name):
        result = {}
        db = database.db(self.__user)
        for state in GameManager.__STATES:
            result[state] = self.load_state(save_name, state)
        return result
