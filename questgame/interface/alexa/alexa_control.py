from flask_ask import Ask, request, session, question, statement
from flask import Flask
import logging, sys
import os
from questgame.interface.alexa.utils import Helpers
from questgame.interface.controller import Actions, LoadManager, GameManager
from questgame.common import test_constants

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

def reply_current_intent(): return Helpers.reply(ask.request.intent.name)
class test_intent(object):
    def __call__(self, func):
        if not test_constants.UNITTEST_TEST_INTENTS:
            # Return the function unchanged, not decorated.
            return func
        return reply_current_intent

app = Flask(__name__)
ask = Ask(app, '/')

game_manager = GameManager()

QUERY_WHAT = 0
QUERY_EXIT_GAME = 1
QUERY_NEW_GAME = 2
QUERY_CLASS = 3

def __set_query(state): session.attributes['query'] = state
def __get_query():
    if 'query' not in session.attributes.keys(): return 0
    return session.attributes['query']

def __query_with_what(text):
    __set_query(QUERY_WHAT)
    return Helpers.query_with_what(text)
def __query(text, query_state):
    __set_query(query_state)
    return Helpers.query(text)

def __continue_game():
    """Continues a current game"""
    user_id =  session.user.userId
    if not game_manager.is_game_started(user_id):
        return launch()
    reply_text = game_manager.continue_game(user_id)
    return __query_with_what(reply_text)

def __do_action(action, item):
    """Common action method"""
    user_id = session.user.userId
    if not game_manager.is_game_started(user_id):
        return launch()
    reply_text = game_manager.perform_action(user_id, action, item)
    return __query_with_what(reply_text)

def __do_throw(item, target):
    """Common action method"""
    user_id = session.user.userId
    if not game_manager.is_game_started(user_id):
        return launch()
    reply_text = game_manager.perform_throw(user_id, item, target)
    return __query_with_what(reply_text)

def __do_spell(spell, item):
    """Common action method"""
    user_id = session.user.userId
    if not game_manager.is_game_started(user_id):
        return launch()
    reply_text = game_manager.perform_spell(user_id, spell, item)
    return __query_with_what(reply_text)

@ask.launch
def launch():
    if test_constants.UNITTEST_TEST_INTENTS: return Helpers.reply('launchIntent')
    
    user_id = session.user.userId
    if game_manager.is_game_started(user_id):
        return __continue_game()

    welcome_text = Helpers.render_common_template('welcome')
    help_text = Helpers.render_common_template('help')
    
    #Look for saved games
    gm = LoadManager(user_id)
    if not gm.does_user_exist():
        games_text = Helpers.render_common_template('no_games') + '. ' + Helpers.render_common_template('choose_class')
        return __query(welcome_text + '. ' + games_text, QUERY_CLASS).reprompt(games_text)
    else:
        games_text = Helpers.render_common_template('load_game')
        #If only one game load it
        game_manager.load_game(user_id, 'test')
        return __continue_game()

@ask.intent('StartGameIntent')
@test_intent()
def start(): return __query(Helpers.render_common_template('are_you_sure'), QUERY_NEW_GAME)

@ask.intent('SearchIntent')
@test_intent()
def search(sitem): return __do_action(Actions.SEARCH)

@ask.intent("WhereIntent")
@test_intent()
def where(): return __do_action(Actions.WHRERE)

@ask.intent('OpenIntent')
@test_intent()
def open(oitem): return __do_action(Actions.OPEN, oitem)

@ask.intent('CloseIntent')
@test_intent()
def close(oitem): return __do_action(Actions.CLOSE, oitem)

@ask.intent('PickLockIntent')
@test_intent()
def pick_lock(): return __do_action(Actions.PICK_LOCK)

@ask.intent('PushIntent')
@test_intent()
def push(item): return __do_action(Actions.PUSH, item)

@ask.intent('PullIntent')
@test_intent()
def pull(item): return __do_action(Actions.PULL, item)

@ask.intent('StrikeIntent')
@test_intent()
def strike(target): return __do_action(Actions.STRIKE, target)

@ask.intent('ShootIntent')
@test_intent()
def shoot(target): return __do_action(Actions.SHOOT, target)

@ask.intent('CastIntent')
@test_intent()
def cast(spell, target): return __do_spell(spell, target)

@ask.intent('ThrowIntent')
@test_intent()
def throw(titem, target): return __do_throw(item, target)

@ask.intent('AMAZON.YesIntent')
@test_intent()
def yes():
    query = __get_query()
    if query == QUERY_NEW_GAME:
        __set_query(QUERY_WHAT)
        #TODO
        return launch()

    elif query == QUERY_EXIT:
        bye_text = Helpers.render_common_template('bye')    
        return statement(bye_text)
    else:
        return __do_action(Actions.YES)
        
@ask.intent('AMAZON.NoIntent')
@test_intent()
def no():
    query = __get_query()
    if query in [QUERY_NEW_GAME, QUERY_EXIT]:
        __continue_game()
    return __do_action(Actions.NO)
    
@ask.intent('AMAZON.StopIntent')
@test_intent()
def stop(): return __query(Helpers.render_common_template('exit'), QUERY_EXIT_GAME)
    
@ask.intent('AMAZON.HelpIntent')
@test_intent()
def help():
    help_text = Helpers.render_common_template('help')
    return __query_with_what(help_text)

@ask.intent("CharacterIntent")
@test_intent()
def choose_char(name):
    if __get_query() == QUERY_CLASS:
        if name.lower() not in ['thief','mage','fighter','ranger']:
            reply_text = Helpers.render_common_template('unsure') + Helpers.render_common_template('choose_class')
            return __query(reply_text, QUERY_CLASS)

        player = game_manager.get_player(name.lower())
        reply_text = game_manager.start_new_game(session.user.userId, player)
        return __query_with_what(reply_text)

    if not game_manager.is_game_started(session.user.userId):
        return launch()
    reply_text = game_manager.continue_game(session.user.userId)
    return __query_with_what(reply_text)


@ask.intent('AMAZON.CancelIntent')
@test_intent()
def cancel(): return stop()

@ask.intent('DescribeItemIntent')
@test_intent()
def describe(ditem):
    if __get_query() == QUERY_CLASS:
        itm = ditem.lower()
        reply_text = ''
        if itm == 'mage': reply_text = Helpers.render_descr_template('descr_mage')
        elif itm == 'thief': reply_text = determine_reply(Helpers.render_descr_template('descr_thief'))
        elif itm == 'fighter': reply_text = determine_reply(Helpers.render_descr_template('descr_fighter'))
        elif itm == 'ranger': reply_text = determine_reply(Helpers.render_descr_template('descr_ranger'))

        reply_text += Helpers.render_common_template('choose_class')
        return __query(reply_text, QUERY_CLASS)

    return __do_action(Actions.DESCRIBE, ditem)

@ask.session_ended
def session_ended():
    return statement("")    

if __name__ == '__main__':
    app.run(debug=test_constants.ASK_RUN_WITH_DEBUG_ON)