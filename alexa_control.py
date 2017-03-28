from flask_ask import Ask, request, session, question, statement
from flask import Flask, render_template
from db.save_load_game import GameManager
import logging

from interface.alexa.utils import Helpers

app = Flask(__name__)
ask = Ask(app, '/')

STATE_START = 1
STATE_LOAD_GAME = 2
STATE_CREATE_CHARACTER = 3
STATE_QUERY_NEW_GAME = 4
STATE_QUERY_EXIT = 5

def set_state(state): session.attributes['state'] = state
def get_state():
    if 'state' not in session.attributes.keys(): return 0
    return session.attributes['state']

def query_with_what(text): return Helpers.query(text+'. '+render_template('what'))
def query(text): return Helpers.query(text)
    
@ask.launch
def launch():
    user_id = session.user.userId
    welcome_text = render_template('welcome')
    
    help_text = render_template('help')
    
    #Look for saved games
    gm = GameManager(user_id)
    if not gm.does_user_exist():
        set_state(STATE_CREATE_CHARACTER)
        games_text = render_template('no_games') + '. ' + render_template('choose_class')
    else:
        set_state(STATE_LOAD_GAME)
        games_text = render_template('load_game')
    return query(welcome_text + '. ' + games_text).reprompt(games_text)

@ask.intent('LaunchIntent')
def launch2():
    return launch()
    
@ask.intent('StartGameIntent')
def start():
    set_state(STATE_QUERY_NEW_GAME)
    return query(render_template('are_you_sure'))

@ask.intent('AMAZON.YesIntent')
def yes():
    state = get_state()
    if state == STATE_QUERY_NEW_GAME:
        return launch()
    elif state == STATE_QUERY_EXIT:
        bye_text = render_template('bye')    
        return statement(bye_text)
    else:
        return query('You said yes')
        
@ask.intent('AMAZON.NoIntent')
def no():
    return query('You said no')
    
@ask.intent('AMAZON.StopIntent')
def stop():
    set_state(STATE_QUERY_EXIT)
    return query('Are you sure you want to exit the game?')
    
@ask.intent('AMAZON.HelpIntent')
def help():
    help_text = render_template('help')    
    return query_with_what(help_text)

def unsure():
    text = None
    if get_state() == STATE_CREATE_CHARACTER:
        text = render_template('no_games')
    if text:
        return query('I didn''t understand that. You can say help for options. '+text)
    return query_with_what('I didn''t understand that. You can say help for options.')
    
@ask.intent("WhereIntent")
def where():
    where_text = render_template('where') 
    return query_with_what(where_text)

@ask.intent("CharacterIntent")
def choose_char(name):
    if name.lower() not in ['thief','mage','fighter','ranger']:
        return unsure()
    return statement('You chose a {}'.format(name))

@ask.intent('AMAZON.CancelIntent')
def cancel(): return stop()

@ask.intent('DescribeItemIntent')
def describe(item):
    itm = item.lower()
    if itm == 'mage': return determine_reply(render_template('descr_mage'))
    elif itm == 'thief': return determine_reply(render_template('descr_thief'))
    elif itm == 'fighter': return determine_reply(render_template('descr_fighter'))
    elif itm == 'ranger': return determine_reply(render_template('descr_ranger'))

    return query_with_what('you asked to describe a {}'.format(itm))

@ask.session_ended
def session_ended():
    return statement("")    

def determine_reply(text):
    """ Reply based on game state """
    qst = render_template('what')
    if get_state() == STATE_CREATE_CHARACTER:
        qst = render_template('choose_class')
    return query(text + '. .' + qst)
    
if __name__ == '__main__':
    app.run()
    #app.run(debug=True)