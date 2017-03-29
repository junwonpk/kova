import os
import re
import app
import time
import redis
import cPickle

class Kova:

    def __init__(self):
        self.redis = redis.from_url(os.environ.get("REDISCLOUD_URL"))
        self.user_id = 0
        self.next = 0

    def chat(self, input, user_id):
        #debugging
        if input == 'redis flushall':
            self.redis.flushall()
        #debugging

        self.user_id = user_id
        if user_id not in self.redis.keys(): # if user first time talking
            self.initUser(user_id)
            return

        user_data = self.getData(user_id)

        if user_data['chapter'] == 1:
            self.chapter1()

        if self.next == 1:
            user_data['chapter'] += 1

        self.setData(user_id, user_data)
        return

    def kovatype(self, message):
        time.sleep(len(message) * 0.15)
        self.send_message(message)

    def send_message(self, message):
        app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
        ctx = app.app.test_request_context('/')
        ctx.push()
        app.send_message(self.user_id, message)

    def initUser(self, user_id):
        user_data = {'chapter': 0, 'cardkey': 0, 'username': ''}
        self.redis.set(user_id, cPickle.dumps(user_data))
        self.chapter0()

    def getData(self, user_id):
        return cPickle.loads(self.redis.get(user_id))

    def setData(self, user_id, user_data):
        self.redis.set(user_id, cPickle.dumps(user_data))

    def chapter0(self):
        self.kovatype("Hello?")
        self.kovatype("Is someone there?")
        self.kovatype("Please.. I'm scared.. Let me know if you can hear me...")
        self.next = 1

    def chapter1(self):
        self.kovatype("Oh my god! Thank goodness. I'm so glad to meet you.")
        self.kovatype("What should I call you?")
        self.next = 1
