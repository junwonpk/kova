import os
import re
import sys
import app
import time
import story
import redis
import cPickle
import thesaurus as thes
from google.cloud import language

reload(sys)
sys.setdefaultencoding('utf-8')

class Kova:

    def __init__(self):
        self.redis = redis.from_url(os.environ.get("REDISCLOUD_URL"))
        self.user_id = 0
        self.next = 0
        self.typespeed = 5

    def chat(self, input, user_id):
        preprocess(input, user_id)
        user_data = self.getData(user_id)

        if user_data['talking'] == 1:
            return
        if user_data['lastmsg'] == input:
            return
        user_data['lastmsg'] = input
        user_data['talking'] = 1
        self.setData(user_id, user_data)
        self.kovatype("linux setup complete")

        chapter = chapters[user_data['chapter']]
        chapter(input, user_data, user_id)

        if user_data['chapter'] > 20:
            user_data = self.epilogue(input, user_data)
        if user_data['chapter'] < 0:
            user_data = self.gameover(input, user_data)

        if self.next == 1:
            user_data['chapter'] += 1
        user_data['talking'] = 0
        self.setData(user_id, user_data)
        return

    def preprocess(self, input, user_id):
        if input.lower() == 'redis flushall':
            self.redis.flushall()
        self.user_id = user_id
        if input.lower() == 'restart':
            self.restart(user_id)
        if user_id not in self.redis.keys(): # if user first time
            self.initUser(user_id)

    def kovatype(self, message):
        time.sleep(len(message) * self.typespeed)
        self.send_message(message)

    def send_message(self, message):
        app.send_message(self.user_id, message, "text")

    def restart(self, user_id):
        self.redis.delete(user_id)

    def initUser(self, user_id):
        user_data = {"chapter": 0, "cardkey": 0, "username": '', "lastmsg": '', "ch6flag": 0, 'talking': 0}
        self.redis.set(user_id, cPickle.dumps(user_data))

    def getData(self, user_id):
        return cPickle.loads(self.redis.get(user_id))

    def setData(self, user_id, user_data):
        self.redis.set(user_id, cPickle.dumps(user_data))

    def extract_name(self, input):
        name = []
        name = re.findall('.*is\s(\w+).*', input.lower())
        if not name:
            name = re.findall('.*im\s(\w+).*', input.lower())
        if not name:
            name = re.findall('.*\'m\s(\w+).*', input.lower())
        if not name:
            name = re.findall('.*am\s(\w+).*', input.lower())
        if not name:
            name = re.findall('.*call\sme\s(\w+).*', input.lower())
        if not name:
            name = re.findall('.*known\sas\s(\w+).*', input.lower())
        if not name:
            name = re.findall('.*\'s\s(\w+).*', input.lower())
        if not name:
            if len(input.split()) == 1:
                return input
        if name:
            return name[0].title()
        else:
            return []

    def epilogue(self, input, user_data):
        self.kovatype("Story Over")
        self.kovatype("Developed by Junwon Park")
        self.kovatype("Type Restart to begin again.")
        return user_data

    def gameover(self, input, user_data):
        self.kovatype("Game Over")
        self.kovatype("Developed by Junwon Park")
        self.kovatype("Type Restart to begin again.")
        return user_data

    def sentiment(self, input):
        language_client = language.Client()
        document = language_client.document_from_text(input)
        sentiment = document.analyze_sentiment().sentiment
        self.kovatype('Sentiment: {}, {}'.format(sentiment.score, sentiment.magnitude))
        tokens = document.analyze_syntax().tokens
        for token in tokens:
            self.kovatype('{}: {}'.format(token.part_of_speech, token.text_content))
        entities = document.analyze_entities().entities
        for entity in entities:
            self.kovatype('=' * 20)
            self.kovatype('{:<16}: {}'.format('name', entity.name))
            self.kovatype('{:<16}: {}'.format('type', entity.entity_type))
            self.kovatype('{:<16}: {}'.format('metadata', entity.metadata))
            self.kovatype('{:<16}: {}'.format('salience', entity.salience))
