import json

class AlexaResponse(object):
    @property
    def data(self):
        """Returned response data"""
        return self.__response.data
    def __init__(self, response):
        self.__response = response
        self.__data = json.loads(response.data)
    #Helper methods
    def get_output_text(self):
        if 'text' in self.__data['response']['outputSpeech']:
            return self.__data['response']['outputSpeech']['text']
        else:
            return self.__data['response']['outputSpeech']['ssml'].replace('<speak>','').replace('</speak>','')
    def get_reprompt_text(self): return self.__data['response']['reprompt']['outputSpeech']['text']

class AlexaRequest(object):
    @property
    def session_id(self):
        """This requests session id. Pass to the request post to continue the session"""
        return '{}'.format(self.__session_id)
    @property
    def last_response(self):
        """The last response received for this session"""
        return self.__last_response

    def set_intent(self, value): self.__request['request']['intent']['name'] = value
    def set_slots(self, slots):
        slot_data = {}
        for i in range(len(slots)):
            var = slots[i].keys()[0]
            slot_data[var] = slots[i][var]
        self.__request['request']['intent']['slots'] = slot_data
    def post(self, session_id = False):
        if not session_id or session_id != self.session_id:
            self.__set_session_attributes({})
        request_data = self.__get_request_json(session_id)
        response = self.app.post("/", data=request_data, content_type='application/json')
        data = json.loads(response.data)
        self.__set_session_attributes(data['sessionAttributes'])
        self.__last_response = AlexaResponse(response)
        return self.__last_response
    #Helpers
    def create_slot(self, variable_name, value): return {variable_name: { "name": variable_name, "value": value }}

    def __init__(self, app, user_id='yyyy', application_id='xxxx'):
        self.app = app
        self.__request_id = 0
        self.__session_id = 0
        self.__new_session = False
        self.__request = {
             "request": {
                "intent": {
                  "name": "CharacterIntent",
                  "slots": {}
                },
                "locale": "en-US",
                "requestId": "",
                "timestamp": "2017-03-26T21:03:31Z",
                "type": "IntentRequest"
              },
              "session": {
                "application": {
                  "applicationId": ""
                },
                "attributes": {},
                "new": False,
                "sessionId": "",
                "user": {
                  "userId": ""
                }
              },
              "version": "1.0"
              }
        self.__set_application_id(application_id)
        self.__set_user_id(user_id)
    #Private methods
    def __set_session_id(self, value):
        self.__session_id = value
        self.__request['session']['sessionId'] = value
    def __get_new_request_id(self):
        self.__request_id += 1
        return '{}'.format(self.__request_id)
    def __get_new_session_id(self):
        self.__session_id = int(self.__session_id) + 1
        return '{}'.format(self.__session_id)
    def __set_user_id(self, value): self.__request['session']['user']['userId'] = value
    def __set_application_id(self, value): self.__request['session']['application']['applicationId'] = value
    def __set_request_id(self, value): self.__request['request']['requestId'] = value
    def __set_session_attributes(self, value): self.__request['session']['attributes'] = value
    def __set_new_session(self, value): self.__request['session']['new'] = value
    def __get_request_json(self, session_id = None):
        self.__set_request_id(self.__get_new_request_id())
        if session_id:
            self.__set_session_id(session_id)
            self.__set_new_session(True)
        else:
            self.__set_session_id(int(self.__get_new_session_id()))
            self.__set_new_session(False)
        return json.dumps(self.__request)
