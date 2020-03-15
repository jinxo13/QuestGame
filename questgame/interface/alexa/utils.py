from flask_ask import statement, question
import flask
from flask_ask.core import YamlLoader
import os
from questgame.common import errors, constants
import threading

class QuestGameReply(object):
    def __init__(self, prompt, reprompt='', query_state=None):
        prompt = '<speak>{}</speak>'.format(prompt)
        self.prompt = prompt
        if reprompt == '':
            reprompt = prompt
        else:
            reprompt = '<speak>{}</speak>'.format(reprompt)
        self.reprompt = reprompt
        self.query_state = query_state

    @property
    def prompt_text(self):
        return self.prompt.replace('<speak>','').replace('</speak>','')

    def get_alexa_reply(self):
        result = question(self.prompt).simple_card(title=constants.GAME_DISPLAY_NAME, content=self.prompt)
        if self.reprompt == '':
            return result
        else:
            return result.reprompt(self.reprompt)

class QuestGameNormalReply(QuestGameReply):
    def __init__(self, room, prompt):
        reprompt = ''
        query_state = ReplyHelpers.QUERY_WHAT
        if room.player.is_in_battle:
            prompt += ' ' + ReplyHelpers.render_common_template('battle_what')
            reprompt = ReplyHelpers.render_common_template('battle_reprompt')
            query_state = ReplyHelpers.QUERY_BATTLE
        else:
            prompt += ' ' + ReplyHelpers.render_common_template('what')
            reprompt = ReplyHelpers.render_common_template('what_reprompt')
        super(QuestGameNormalReply, self).__init__(prompt, reprompt, query_state)

class ReplyHelpers(object):
    """description of class"""

    QUERY_WHAT = 0
    QUERY_EXIT_GAME = 1
    QUERY_NEW_GAME = 2
    QUERY_CLASS = 3
    QUERY_BATTLE = 4
    QUERY_SELECT = 5

    TEMPLATE_ACTION=1
    TEMPLATE_ROOM=2
    TEMPLATE_DESCRIPTION=3
    TEMPLATE_COMMON=4

    __template_loaders = {}

    __template_folder = os.path.join('questgame','interface','alexa','templates')
    __DESCRIPTION_TEMPLATE = os.path.join(__template_folder,'descriptions.yaml')
    __COMMON_TEMPLATE = os.path.join(__template_folder,'common.yaml')
    __ACTION_TEMPLATE = os.path.join(__template_folder,'actions.yaml')
    __ROOM_TEMPLATE = os.path.join(__template_folder,'rooms.yaml')

    @staticmethod
    def render_descr_template(key, **context): return ReplyHelpers.render_template(ReplyHelpers.__DESCRIPTION_TEMPLATE, key, **context)
    @staticmethod
    def render_common_template(key, **context): return ReplyHelpers.render_template(ReplyHelpers.__COMMON_TEMPLATE, key, **context)
    @staticmethod
    def render_action_template(key, **context): return ReplyHelpers.render_template(ReplyHelpers.__ACTION_TEMPLATE, key, **context)
    @staticmethod
    def render_room_template(key, **context): return ReplyHelpers.render_template(ReplyHelpers.__ROOM_TEMPLATE, key, **context)

    @staticmethod
    def try_render_room_template(room, aitem, key, **context):
        room_key = room.name.lower()
        item_key = aitem.name.lower()
        if ReplyHelpers.has_template(ReplyHelpers.__ROOM_TEMPLATE, room_key+'_'+item_key+'_'+key):
            key = room_key+'_'+item_key+'_'+key
        elif ReplyHelpers.has_template(ReplyHelpers.__ROOM_TEMPLATE, item_key+'_'+key):
            key = item_key+'_'+key
        if ReplyHelpers.has_template(ReplyHelpers.__ROOM_TEMPLATE, key):
            return ReplyHelpers.render_template(ReplyHelpers.__ROOM_TEMPLATE, key, **context)
        raise errors.QuestGameError(errors.QuestGameError.NO_SUCH_TEMPLATE)

    @staticmethod
    def has_template(path, key):
        from alexa_control import app
        lock = threading.Lock()
        with lock:
            if path not in ReplyHelpers.__template_loaders.keys():
                ReplyHelpers.__template_loaders[path] = YamlLoader(app,path)
        try:
            app.jinja_loader = ReplyHelpers.__template_loaders[path]
            app.jinja_env.get_template(key)
            return True
        except:
            return False

    @staticmethod
    def render_template(path, key, **context):
        from alexa_control import app
        lock = threading.Lock()
        with lock:
            if path not in ReplyHelpers.__template_loaders.keys():
                ReplyHelpers.__template_loaders[path] = YamlLoader(app,path)
        app.jinja_loader = ReplyHelpers.__template_loaders[path]
        with app.app_context():
            return flask.render_template(key.replace(' ','_'), **context)

    @staticmethod
    def reply(text):
        s = statement(text).simple_card(title='QuestGame', content=text)
        s._response['shouldEndSession'] = False
        return s

    @staticmethod
    def build_list(seq, attribute):
        result = ''
        i = 0
        for item in seq:
            i += 1
            if i == len(seq):
                result += ' or the '
            elif i != 1:
                result += ', the '
            result += getattr(item, attribute)
        return result