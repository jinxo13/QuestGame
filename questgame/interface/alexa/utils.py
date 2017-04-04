from flask_ask import statement, question
import flask
from flask_ask.core import YamlLoader
import os

class Helpers(object):
    """description of class"""

    __template_loaders = {}

    __template_folder = 'templates'

    @staticmethod
    def render_descr_template(key, **context): return Helpers.render_template(os.path.join(Helpers.__template_folder,'descriptions.yaml'), key, **context)
    @staticmethod
    def render_common_template(key, **context): return Helpers.render_template(os.path.join(Helpers.__template_folder,'common.yaml'), key, **context)
    @staticmethod
    def render_action_template(key, **context): return Helpers.render_template(os.path.join(Helpers.__template_folder,'actions.yaml'), key, **context)
    @staticmethod
    def render_room_template(key, **context): return Helpers.render_template(os.path.join(Helpers.__template_folder,'rooms.yaml'), key, **context)

    @staticmethod
    def render_template(path, key, **context):
        from alexa_control import app
        if path not in Helpers.__template_loaders.keys():
            Helpers.__template_loaders[path] = YamlLoader(app,path)
        app.jinja_loader = Helpers.__template_loaders[path]
        with app.app_context():
            return flask.render_template(key, **context)

    @staticmethod
    def reply(text):
        s = statement(text).simple_card(title='QuestGame', content=text)
        s._response['shouldEndSession'] = False
        return s

    @staticmethod
    def query(text): return question(text).simple_card(title='QuestGame', content=text)

    @staticmethod
    def query_with_what(text): return Helpers.query(text+'. '+Helpers.render_common_template('what'))
