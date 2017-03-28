from flask_ask import Ask, request, session, question, statement
import unittest
import json
from flask import Flask, render_template
from alexa_control import app
import logging, sys
from alexa_test_helpers import AlexaRequest, AlexaResponse

#root = logging.getLogger()
#root.setLevel(logging.DEBUG)
#ch = logging.StreamHandler(sys.stdout)
#ch.setLevel(logging.DEBUG)
#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#ch.setFormatter(formatter)
#root.addHandler(ch)

logging.getLogger('flask_ask').setLevel(logging.DEBUG)

class Test_alexa_interface(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        app.config['ASK_VERIFY_REQUESTS'] = False
        app.config['TESTING'] = True

    def test__ALEXA_start_game(self):
        request = AlexaRequest(self.app, user_id='fred', application_id='quest_game')
        request.set_intent('StartGameIntent')
        response = request.post()
        print response.data
        with app.app_context():
            self.assertEqual(render_template('are_you_sure'), response.get_output_text())

        #Pass session_id to continue session
        request.set_intent('AMAZON.YesIntent')
        response = request.post(request.session_id)
        print response.data
        self.assertTrue('welcome to' in response.get_output_text().lower())

        #Prompt based on starting a new game, different when you have a saved game
        self.assertTrue('the first thing we need' in response.get_output_text().lower())
        self.assertTrue('the first thing we need' in response.get_reprompt_text().lower())
        return request

    def test__ALEXA_character_reponse(self):
        request = self.test__ALEXA_start_game()
        request.set_intent('CharacterIntent')
        request.set_slots([request.create_slot('name','mage')])
        response = request.post(request.session_id)
        print response.data
        resp = response.get_output_text().lower()
        self.assertEqual(resp,'you chose a mage', resp)

if __name__ == '__main__':
    unittest.main()
