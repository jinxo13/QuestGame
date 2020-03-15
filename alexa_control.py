from flask_ask import Ask, request, session, question, statement
from flask import Flask
import logging, sys
import os
from questgame.interface.alexa.utils import ReplyHelpers, QuestGameReply
from questgame.interface.controller import LoadManager, GameManager
from questgame.players.players import Actions
from questgame.common import test_constants

logger = logging.getLogger()
#logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

def reply_current_intent(): return ReplyHelpers.reply(ask.request.intent.name)
class test_intent(object):
    def __call__(self, func):
        if not test_constants.UNITTEST_TEST_INTENTS:
            # Return the function unchanged, not decorated.
            return func
        return reply_current_intent

app = Flask(__name__)
ask = Ask(app, '/')

game_manager = GameManager()

def __set_query(state): session.attributes['query'] = state
def __get_query():
    if 'query' not in session.attributes.keys(): return 0
    return session.attributes['query']

def __query(text, reprompt='', query_state=None):
    if query_state is None:
        if __is_in_battle():
            __set_query(ReplyHelpers.QUERY_BATTLE)
        else:
            __set_query(ReplyHelpers.QUERY_WHAT)
    __set_query(query_state)

    if reprompt == '':
        if query_state == ReplyHelpers.QUERY_WHAT:
            reprompt = ReplyHelpers.render_common_template('what_reprompt')
        if query_state == ReplyHelpers.QUERY_BATTLE:
            reprompt = ReplyHelpers.render_common_template('battle_reprompt')
        if query_state == ReplyHelpers.QUERY_CLASS:
            reprompt = ReplyHelpers.render_common_template('choose_class')
    result = QuestGameReply(text, reprompt, query_state).get_alexa_reply()
    return result

def __is_in_battle():
    user_id =  session.user.userId
    if not game_manager.is_game_started(user_id):
        return False
    try:
        return game_manager.get_user(user_id).player.is_in_battle
    except:
        return False

def __continue_game():
    """Continues a current game"""
    user_id =  session.user.userId
    if not game_manager.is_game_started(user_id):
        return launch()
    quest_game_reply = game_manager.continue_game(user_id)
    __set_query(quest_game_reply.query_state)
    return quest_game_reply.get_alexa_reply()

def __do_action(action, item=None, amount=0):
    """Common action method"""
    print 'ACTION: {}, ITEM: {}'.format(action, item)
    session.attributes['action'] = action
    user_id = session.user.userId
    if not game_manager.is_game_started(user_id):
        return launch()
    quest_game_reply = game_manager.perform_action(user_id, action, item, amount)
    __set_query(quest_game_reply.query_state)
    return quest_game_reply.get_alexa_reply()

def __do_throw(item, target=None):
    """Common action method"""
    user_id = session.user.userId
    session.attributes['action'] = Actions.THROW
    session.attributes['target_text'] = target
    if not game_manager.is_game_started(user_id):
        return launch()
    quest_game_reply = game_manager.perform_throw(user_id, item, target)
    __set_query(quest_game_reply.query_state)
    return quest_game_reply.get_alexa_reply()

def __do_spell(spell, item=None):
    """Common action method"""
    user_id = session.user.userId
    session.attributes['action'] = Actions.CAST
    session.attributes['spell_text'] = spell
    if not game_manager.is_game_started(user_id):
        return launch()
    quest_game_reply = game_manager.perform_spell(user_id, spell, item)
    __set_query(quest_game_reply.query_state)
    return quest_game_reply.get_alexa_reply()

@ask.launch
def launch():
    if test_constants.UNITTEST_TEST_INTENTS: return ReplyHelpers.reply('launchIntent')
    
    user_id = session.user.userId
    if game_manager.is_game_started(user_id):
        return __continue_game()

    welcome_text = ReplyHelpers.render_common_template('welcome')
    #help_text = ReplyHelpers.render_common_template('help')
    
    #Look for saved games
    gm = LoadManager(user_id)
    if not gm.does_user_game_exist('test'):
        games_text = ReplyHelpers.render_common_template('no_games') + ' ' + ReplyHelpers.render_common_template('choose_class')
        return __query(welcome_text + ' ' + games_text, query_state=ReplyHelpers.QUERY_CLASS)
    else:
        games_text = ReplyHelpers.render_common_template('load_game')
        #If only one game load it
        game_manager.load_game(user_id, 'test')
        return __continue_game()

@ask.intent('StartGameIntent')
@test_intent()
def start(): return __query(ReplyHelpers.render_common_template('are_you_sure'), query_state=ReplyHelpers.QUERY_NEW_GAME)

@ask.intent('SearchIntent')
@test_intent()
def search(sitem): return __do_action(Actions.SEARCH, sitem)

@ask.intent('WhereIntent')
@test_intent()
def where(): return __do_action(Actions.WHERE)

@ask.intent('SelectItemIntent')
@test_intent()
def select_item(ditem):
    if not __get_query() == ReplyHelpers.QUERY_SELECT:
        return __query(ReplyHelpers.render_common_template('unsure'))

    #perform the last action with the supplied item
    action = None
    spell_text = None
    target_text = None
    #TODO: Make get with default
    if 'action' in session.attributes.keys():
        action = int(session.attributes['action'])
    if 'spell_text' in session.attributes.keys():
        spell_text = session.attributes['spell_text']
    if 'target_text' in session.attributes.keys():
        target_text = session.attributes['target_text']
    
    if action is None:
        return __query(ReplyHelpers.render_common_template('unsure'))
    elif action == Actions.CAST:
        return __do_spell(spell_text, ditem)
    elif action == Actions.THROW:
        return __do_throw(ditem, target_text)
    else:
        return __do_action(action, ditem)

@ask.intent('WhatCanIDoIntent')
@test_intent()
def what(): return __do_action(Actions.WHAT)

@ask.intent('MoneyIntent')
@test_intent()
def money(): return __do_action(Actions.MONEY)

@ask.intent('PickupIntent')
@test_intent()
def pickup(ditem): return __do_action(Actions.PICKUP, ditem)

@ask.intent('BuyIntent')
@test_intent()
def buy(ditem): return __do_action(Actions.BUY, ditem, amount=1)

@ask.intent('SellIntent')
@test_intent()
def sell(ditem): return __do_action(Actions.SELL, ditem, amount=1)

@ask.intent('WhatCanIBuyIntent')
@test_intent()
def what_buy(): return __do_action(Actions.WHAT_BUY)

@ask.intent('DropIntent')
@test_intent()
def drop(ditem): return __do_action(Actions.DROP, ditem)

@ask.intent('EatIntent')
@test_intent()
def eat(ditem): return __do_action(Actions.EAT, ditem)

@ask.intent('OpenIntent')
@test_intent()
def open(oitem): return __do_action(Actions.OPEN, oitem)

@ask.intent('CloseIntent')
@test_intent()
def close(oitem): return __do_action(Actions.CLOSE, oitem)

@ask.intent('LockIntent')
@test_intent()
def lock(oitem): return __do_action(Actions.LOCK, oitem)

@ask.intent('UnlockIntent')
@test_intent()
def unlock(oitem): return __do_action(Actions.UNLOCK, oitem)

@ask.intent('PickLockIntent')
@test_intent()
def pick_lock(oitem): return __do_action(Actions.PICK_LOCK, oitem)

@ask.intent('PushIntent')
@test_intent()
def push(item): return __do_action(Actions.PUSH, item)

@ask.intent('PullIntent')
@test_intent()
def pull(item): return __do_action(Actions.PULL, item)

@ask.intent('StrikeIntent')
@test_intent()
def strike(): return __do_action(Actions.STRIKE)

@ask.intent('StrikeTargetIntent')
@test_intent()
def strike_target(target): return __do_action(Actions.STRIKE, target)

@ask.intent('ShootIntent')
@test_intent()
def shoot(): return __do_action(Actions.SHOOT)

@ask.intent('ShootTargetIntent')
@test_intent()
def shoot_target(target): return __do_action(Actions.SHOOT, target)

@ask.intent('CastTargetIntent')
@test_intent()
def cast_target(spell, target): return __do_spell(spell, target)

@ask.intent('CastIntent')
@test_intent()
def cast(spell): return __do_spell(spell)

@ask.intent('ThrowTargetIntent')
@test_intent()
def throw_target(titem, target): return __do_throw(titem, target)

@ask.intent('ThrowIntent')
@test_intent()
def throw(titem): return __do_throw(titem)

@ask.intent('AMAZON.YesIntent')
@test_intent()
def yes():
    query = __get_query()
    if query == ReplyHelpers.QUERY_NEW_GAME:
        __set_query(ReplyHelpers.QUERY_WHAT)
        user_id = session.user.userId

        gm = LoadManager(user_id)
        if gm.does_user_game_exist('test'):
            game_manager.delete_game(user_id,'test')
        return launch()

    elif query == ReplyHelpers.QUERY_EXIT_GAME:
        bye_text = ReplyHelpers.render_common_template('bye')    
        return statement(bye_text)
    else:
        return __do_action(Actions.YES)
        
@ask.intent('AMAZON.NoIntent')
@test_intent()
def no():
    query = __get_query()
    if query in [ReplyHelpers.QUERY_NEW_GAME, ReplyHelpers.QUERY_EXIT_GAME]:
        __continue_game()
    return __do_action(Actions.NO)
    
@ask.intent('AMAZON.StopIntent')
@test_intent()
def stop(): return __query(ReplyHelpers.render_common_template('exit'), query_state=ReplyHelpers.QUERY_EXIT_GAME)
    
@ask.intent('AMAZON.HelpIntent')
@test_intent()
def help():
    help_text = ReplyHelpers.render_common_template('help')
    return __query(help_text)

@ask.intent('HelpIntent')
@test_intent()
def help_area(area):
    try:
        help_text = ReplyHelpers.render_common_template('help_{}'.format(area))
    except:
        help_text = ReplyHelpers.render_common_template('help_not_found') + ' ' + ReplyHelpers.render_common_template('help')
    return __query(help_text)

@ask.intent("CharacterIntent")
@test_intent()
def choose_char(name):
    if __get_query() == ReplyHelpers.QUERY_CLASS:
        if name.lower() not in ['thief','mage','fighter','ranger']:
            reply_text = ReplyHelpers.render_common_template('unsure') + ' ' + ReplyHelpers.render_common_template('choose_class')
            return __query(reply_text, query_state=ReplyHelpers.QUERY_CLASS)

        player = game_manager.create_player(name.lower())
        reply_text = ReplyHelpers.render_common_template('chose_char',cls=name.lower())
        reply_text += ' ' + game_manager.start_new_game(session.user.userId, player).prompt_text
        return __query(reply_text)

    if not game_manager.is_game_started(session.user.userId):
        return launch()
    reply_text = game_manager.continue_game(session.user.userId)
    return __query(reply_text)


@ask.intent('AMAZON.CancelIntent')
@test_intent()
def cancel(): return stop()

@ask.intent('DescribeItemIntent')
@test_intent()
def describe(ditem):
    if __get_query() == ReplyHelpers.QUERY_CLASS:
        itm = ditem.lower()
        reply_text = ''
        if itm == 'mage': reply_text = ReplyHelpers.render_descr_template('descr_mage')
        elif itm == 'thief': reply_text = ReplyHelpers.render_descr_template('descr_thief')
        elif itm == 'fighter': reply_text = ReplyHelpers.render_descr_template('descr_fighter')
        elif itm == 'ranger': reply_text = ReplyHelpers.render_descr_template('descr_ranger')
        
        reply_text += ' ' + ReplyHelpers.render_common_template('choose_class')
        return __query(reply_text, query_state=ReplyHelpers.QUERY_CLASS)

    return __do_action(Actions.DESCRIBE, ditem)

@ask.session_ended
def session_ended():
    user_id = session.user.userId
    game_manager.user_exit(user_id)
    return statement("")    

if __name__ == '__main__':
    app.run(debug=test_constants.ASK_RUN_WITH_DEBUG_ON)