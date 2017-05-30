import os
import re
import sys
import app
import time
import redis
import cPickle
from google.cloud import language

reload(sys)
sys.setdefaultencoding('utf-8')

class Kova:

    def __init__(self):
        self.redis = redis.from_url(os.environ.get("REDISCLOUD_URL"))
        self.user_id = 0
        self.next = 0
        self.typespeed = 0.05
        self.chapters = {0:self.chapter0, 1:self.chapter1, 2:self.chapter2,
                        3:self.chapter3, 4:self.chapter4, 5:self.chapter5,
                        6:self.chapter6, 7:self.chapter7, 8:self.chapter8}

    def chat(self, input, user_id):
        self.preprocess(input, user_id)
        user_data = self.getData(user_id)

        if user_data['talking'] == 1:
            return
        if user_data['lastmsg'] == input:
            return
        user_data['lastmsg'] = input
        user_data['talking'] = 1
        self.setData(user_id, user_data)

        chapter = self.chapters[user_data['chapter']]
        chapter(input, user_data, user_id)
        
        chapter == NULL:
            user_data = self.epilogue(input, user_data)
        if user_data['chapter'] < 0:
            user_data = self.gameover(input, user_data)

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
        user_data = {"chapter": 0, "username": '', "lastmsg": '', \
                    "trust": 0, 'talking': 0, "age": 0, "auto_sent": 0\
                    "curr_sent": 0}
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
        if not name and len(input.split()) == 1:
            return input.title()
        if name:
            return name[0].title()
        else:
            return []

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

    """
        Lena Kova Story Below
    """

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

    def answer_questions(self, input, user_data): # if user asks questions, answer.
        # lena's age, gender, school, family members
        return user_data

    def chapter0(self, input, user_data, user_id):
        self.kovatype("Hello?")
        self.kovatype("Is this message getting through?")
        user_data["chapter"] = 1
        return user_data

    def chapter1(self, input, user_data, user_id):
        self.kovatype("Hey there! Wow, this is so cool!")
        self.kovatype("I'm Lena. Nice to meet ya!")
        self.kovatype("What should I call you?")
        user_data["chapter"] = 2
        return user_data

    def chapter2(self, input, user_data, user_id):
        username = self.extract_name(input)
        if not username:
            self.kovatype("Huh? I'm not sure what you mean.")
            self.kovatype("I mean, what's your name?")
        if username:
            user_data["username"] = username
            self.kovatype("Cool! Nice to meet you, " + username + "!")
            self.kovatype("Which year are you living in?")
            user_data["chapter"] = 3
        return user_data

    def chapter3(self, input, user_data, user_id):
        if "2017" in input:
            self.kovatype("Wow! This time portal is working then!")
            self.kovatype("I'm texting you from 2117. :P")
        else:
            self.kovatype("Oh I guess this is not working...")
            self.kovatype("or maybe you lied.")
            user_data["trust"] -= 1;
        user_data["chapter"] = 4
        return user_data

    def chapter4(self, input, user_data, user_id):
        self.kovatype("My dad works for the Foundry Corporation")
        self.kovatype("in the advanced research department.")
        self.kovatype("He brought home an experimental time portal technology, so I installed it on my device while he's asleep! Hehe.")
        self.kovatype("I guess Foundry didn't exist back in 2017.")
        user_data["chapter"] = 5
        return user_data

    def chapter5(self, input, user_data, user_id):
        self.kovatype("Alright.")
        self.kovatype("I texted anyone at random from your time,")
        self.kovatype("so I actually have no idea who you are.")
        self.kovatype("How old are you?")
        user_data["chapter"] = 6
        return user_data

    def chapter6(self, input, user_data, user_id):
        #parse and store user age
        self.kovatype("Sweet. I'm 16. Living in Palo Alto, California.")
        self.kovatype("Probably looks very different from your wolrd's Palo Alto though.")
        self.kovatype("I kinda can infer from your name, but don't wanna make assumptions.")
        self.kovatype("What gender do you identify with?")
        user_data["chapter"] = 7
        return user_data

    def chapter7(self, input, user_data, user_id):
        #parse and store user gender
        self.kovatype("Nice nice. Good to have a [GENDER] friend from a hundred years ago!")
        self.kovatype("What is it like to live in a world without automation?")
        self.kovatype("You still do your chores by hand, right?")
        self.kovatype("It must really suck...")
        self.kovatype("What do you think about your world?")
        user_data["chapter"] = 8
        return user_data

    def chapter8(self, input, user_data, user_id):
        #parse and store user gender
        self.kovatype("Awesome to hear from you :)")
        self.kovatype("Hey, it's actually 3AM here.")
        self.kovatype("I had to wait until my dad fell asleep, so... kinda late")
        self.kovatype("Tomorrow's an exciting day for me, so I'm gonna go sleep.")
        self.kovatype("Thanks for being my friend, and talk to you in the morning! <3")
        user_data["chapter"] = 9
        return user_data
