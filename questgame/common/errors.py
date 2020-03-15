class QuestGameError(Exception):
    
    NO_SUCH_GAME = 0
    SAVE_GAME_FAILED = 1
    LOAD_FAILED = 2
    SAVE_PLAYER_FAILED = 3
    START_NEW_GAME_FAILED = 4
    MISSING_SAVE_GAME_NAME = 5

    NO_SUCH_TEMPLATE = 20
    
    """description of class"""
    def __init__(self, *args):
        return super(QuestGameError, self).__init__(*args)

