from flask_ask import statement, question

class Helpers(object):
    """description of class"""

    @staticmethod
    def reply(text):
        s = statement(text).simple_card(title='QuestGame', content=text)
        s._response['shouldEndSession'] = False
        return s

    @staticmethod
    def query(text):
        return question(text).simple_card(title='QuestGame', content=text)
