from flask_ask import Ask, request, session, question, statement
from jinja2 import ChoiceLoader
import unittest
import json
from flask import Flask
from alexa_control import app
from questgame.interface.alexa.utils import ReplyHelpers
import logging, sys
from alexa_test_helpers import AlexaRequest, AlexaResponse
import os
from alexa_client import AlexaClient
from alexa_agent.agent import tts
import filecmp
from questgame.common import test_constants, constants

#root = logging.getLogger()
#root.setLevel(logging.DEBUG)
#ch = logging.StreamHandler(sys.stdout)
#ch.setLevel(logging.DEBUG)
#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#ch.setFormatter(formatter)
#root.addHandler(ch)

logging.getLogger('flask_ask').setLevel(logging.DEBUG)

TTS_DIR =  os.path.join(os.getcwd(),'tmp','tts')

class Test_alexa_interface(unittest.TestCase):
    
    def text_to_wav(self, text, save_to):
        return tts('{} - ASK'.format(save_to), text)

    def ask(self, save_to, text):
        filename = tts('{} - ASK'.format(save_to), text)
        input = filename
        save_to = os.path.join(TTS_DIR, '{} - RESP.mp3'.format(save_to))
        self.alexa_client.ask(input, save_to=save_to)
        print("Response saved to {}".format(save_to))
        return save_to

    def check_utterance(self, text, resp_file, input_file):
        check_dir = 'ActualResponses'
        if test_constants.UNITTEST_TEST_INTENTS:
            check_dir = 'TestIntentResponses'
        saved_resp = self.ask(input_file, text)
        compare_resp = os.path.join(TTS_DIR,check_dir,'{} - RESP.mp3'.format(resp_file))
        return filecmp.cmp(saved_resp, compare_resp)

    def test_Create_Response(self):
        self.text_to_wav("Hi. This is Alexa. Hungry ones it is dinner time!.",'dinner_time')
        self.text_to_wav("Hi. This is Alexa. Dinner is served!.",'dinner_time2')
        return True

    def test__ALEXA_REMOTE_utterances(self):
        #request = AlexaRequest(self.app, user_id='fred', application_id='quest_game')
        #request.set_intent('SearchIntent')
        #request.create_slot('sitem','room')
        #response = request.post()

        self.ask('welcome1','open {}'.format(constants.GAME_INVOKE))
        #self.ask('choose','a thief')
        #self.ask('describe_mage', 'describe mage')
        #self.ask('describe_thief', 'describe thief')
        #self.ask('describe_ranger', 'describe ranger')
        #self.ask('describe_fighter', 'describe fighter')
        #self.ask('cast_spell', 'cast open at door')
        #self.ask('open_door', 'open door')
        #self.ask('open_chest', 'open chest')
        #self.ask('close_door', 'open door')
        #self.ask('pick_lock', 'pick lock')
        #self.ask('search_body', 'search dead body')
        #self.ask('search_room', 'search room')
        #self.ask('describe_dagger', 'describe dagger')
        self.ask('describe_rat', 'describe rat')

    def test__ALEXA_REMOTE_intent_response(self):
        #Check skill test server running
        #self.assertTrue(is_skill_test_server_running(),'Skill Test Server is running')

        test_constants.UNITTEST_TEST_INTENTS = True
        f = open('\\\\{}\\pihome\\quest_game\\src\\common\\test_constants.py'.format(constants.SKILL_TEST_SERVER), 'w')
        f.write("UNITTEST_DB_LOCAL = True\r\n")
        f.write("UNITTEST_TEST_INTENTS = True\r\n")
        f.write("ASK_RUN_WITH_DEBUG_ON = True\r\n")
        f.close()
        
        #Test utterances
        try:
            self.assertTrue(self.check_utterance('open {}'.format(constants.GAME_INVOKE),resp_file='welcome',input_file='welcome1'))
            self.assertTrue(self.check_utterance('new game',resp_file='start',input_file='start1'))
            self.assertTrue(self.check_utterance('start new game',resp_file='start',input_file='start2'))
            self.assertTrue(self.check_utterance('stop',resp_file='stop',input_file='stop1'))
            self.assertTrue(self.check_utterance('exit',resp_file='exit',input_file='exit1'))
            self.assertTrue(self.check_utterance('fred',resp_file='not_in_game',input_file='not_in_game'))
        finally:
            #Revert change
            test_constants.UNITTEST_TEST_INTENTS = False
            f = open('\\\\{}\\pihome\\quest_game\\src\\common\\test_constants.py'.format(constants.SKILL_TEST_SERVER), 'w')
            f.write("UNITTEST_DB_LOCAL = True\r\n")
            f.write("UNITTEST_TEST_INTENTS = False\r\n")
            f.write("ASK_RUN_WITH_DEBUG_ON = True\r\n")
            f.close()

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        app.config['ASK_VERIFY_REQUESTS'] = False
        app.config['TESTING'] = True
        self.alexa_client = AlexaClient()

    def test__ALEXA_LOCAL_start_game(self):
        request = AlexaRequest(self.app, user_id='fred', application_id='quest_game')
        request.set_intent('StartGameIntent')
        response = request.post()
        print(response.data)
        self.assertEqual(ReplyHelpers.render_descr_template('are_you_sure'), response.get_output_text())

        #Pass session_id to continue session
        request.set_intent('AMAZON.YesIntent')
        response = request.post(request.session_id)
        print(response.data)
        self.assertTrue(ReplyHelpers.render_descr_template('welcome') in response.get_output_text())

        #Prompt based on starting a new game, different when you have a saved game
        #self.assertTrue(ReplyHelpers.render_descr_template('no_games') in response.get_output_text())
        #self.assertTrue(ReplyHelpers.render_descr_template('no_games') in response.get_reprompt_text())

        #Describe Thief
        request.set_intent('DescribeItemIntent')
        request.set_slots([request.create_slot('ditem','thief')])
        response = request.post(request.session_id)
        print(response.get_output_text())
        self.assertTrue(ReplyHelpers.render_descr_template('descr_thief') in response.get_output_text())

        return request

    def test__ALEXA_LOCAL_character_reponse(self):
        request = self.test__ALEXA_LOCAL_start_game()
        request.set_intent('CharacterIntent')
        request.set_slots([request.create_slot('name','mage')])
        response = request.post(request.session_id)
        print(response.data)
        self.assertTrue(ReplyHelpers.render_action_template('char_choice',char='mage') in response.get_output_text())

if __name__ == '__main__':
    unittest.main()
