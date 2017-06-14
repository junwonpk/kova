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
        self.typespeed = 0.10
        self.lastchapter = 18
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
        user_data = self.jump(input, user_data)
        self.setData(user_id, user_data)

        if user_data['chapter'] not in self.chapters.keys():
            user_data = self.epilogue(input, user_data)
        if user_data['chapter'] < 0:
            user_data = self.gameover(input, user_data)
        else:
            chapter = self.chapters[user_data['chapter']]
            chapter(input, user_data, user_id)
        
        user_data['talking'] = 0
        self.setData(user_id, user_data)
        return

    """ Infrastructure Code """

    def preprocess(self, input, user_id):
        if input.lower() == 'redis flushall':
            self.redis.flushall()
        self.user_id = user_id
        if input.lower() == 'restart':
            self.restart(user_id)
        if user_id not in self.redis.keys(): # if user first time
            self.initUser(user_id)

    def jump(self, input, user_data):
        if 'jump' in input.lower():
            chapter = re.search('.*chapter(.).*', input.lower())
            print(chapter)
            if chapter is not None and (len(chapter) is 1 or len(chapter) is 2):
                user_data["chapter"] = chapter
        return user_data

    def kovatype(self, message):
        time.sleep(len(message) * self.typespeed)
        self.send_message(message)

    def send_message(self, message):
        app.send_message(self.user_id, message, "text")

    def restart(self, user_id):
        self.redis.delete(user_id)

    def initUser(self, user_id):
        user_data = {"chapter": 0, "username": '', "lastmsg": '', \
                    "trust": 0, 'talking': 0, "age": 0, "auto_sent": 0,\
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

    """ Lena Kova Story """

    def epilogue(self, input, user_data):
        self.kovatype("Story Over")
        # self.kovatype("Developed by Junwon Park")
        self.kovatype("Type Restart to begin again.")
        return user_data

    def gameover(self, input, user_data):
        self.kovatype("Game Over")
        # self.kovatype("Developed by Junwon Park")
        self.kovatype("Type Restart to begin again.")
        return user_data

    def answer_questions(self, input, user_data): # if user asks questions, answer.
        # lena's age, gender, school, family members
        return user_data

    """ ACT 1 """

    def chapter0(self, input, user_data, user_id):
        self.kovatype("Hello?")
        self.kovatype("Is this message getting through?")
        user_data["chapter"] = 1
        return user_data

    def chapter1(self, input, user_data, user_id):
        self.kovatype("Hey there! Wow, this is so cool!")
        self.kovatype("Nice to meet you! I'm Lena.")
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
            self.kovatype("Cool! Hello, " + username + "!")
            self.kovatype("What year is it there by the way?")
            user_data["chapter"] = 3
        return user_data

    def chapter3(self, input, user_data, user_id):
        if "2017" in input:
            self.kovatype("Wow! This time portal is actually working then!")
            self.kovatype("I'm texting you from 2117. :P")
        else:
            self.kovatype("Oh I guess this is not working...")
            self.kovatype("or maybe... you are lying...")
            user_data["trust"] -= 1
            #give a chance to recover
        user_data["chapter"] = 4
        return user_data

    def chapter4(self, input, user_data, user_id):
        self.kovatype("My dad works for the Orbis Corporation")
        self.kovatype("in the advanced research department.")
        self.kovatype("He brought home an experimental time portal technology, \
so I installed it on my device while he's asleep! Hehe.")
        self.kovatype("I guess Orbis didn't exist back in 2017.")
        user_data["chapter"] = 5
        return user_data

    def chapter5(self, input, user_data, user_id):
        self.kovatype("I see.")
        self.kovatype("I texted anyone at random from your time,")
        self.kovatype("so I actually have no idea who you are.")
        self.kovatype("How old are you?")
        user_data["chapter"] = 6
        return user_data

    def chapter6(self, input, user_data, user_id):
        #parse and store user age
        self.kovatype("Sweet. I'm 16, living in Palo Alto, California.")
        self.kovatype("It probably looks very different from your wolrd's Palo Alto though.")
        self.kovatype("Also, I kinda can infer from your name, but don't wanna make assumptions.")
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

    """ ACT 2 """

    def chapter9(self, input, user_data, user_id):
        sleep_start = user_data["sleep_start"]
        if current_time - sleep_start < 8:
            return user_data
        #how do i make her send again in that time?
        self.kovatype("Good Morning!")
        self.kovatype("How are you doing?")
        user_data["chapter"] = 10
        return user_data

    def chapter10(self, input, user_data, user_id):
        #sentiment analysis and respond appropriately
        self.kovatype("A couple of weeks ago, dad showed me an \"alarm app\" from your time.") 
        self.kovatype("It's so interesting that you enter a specific time manually for the alarm to ring at.") 
        self.kovatype("It's really... How should I put it...") 
        self.kovatype("Vintage?") 
        self.kovatype("We don't have alarm devices anymore. The room lights up and plays a song when my body is ready to wake up.") 
        self.kovatype("Wait a second. I'm gonna walk through the shower aisle.") 
        user_data["chapter"] = 11
        return user_data

    def chapter11(self, input, user_data, user_id):
        #if user asks, talk about shower aisle. 
        #shower aisle sprays water soap and rinses body and hair. With high precision.
        self.kovatype("Apparently, most people I will meet today like the color Orange.") 
        self.kovatype("I really like the dress my assistant printed for me today") 
        self.kovatype("I wonder what's for breakfast. What's your favorite dish?")
        user_data["chapter"] = 12
        return user_data

    def chapter12(self, input, user_data, user_id):
        #Lena's favorite food is pasta. If same, trust score goes up.
        self.kovatype("I can hear the delivery drones downstairs. Ah, mom must be downstairs.") 
        self.kovatype("Bipedal-bot is telling her we're having Danish and Apple for breakfast.") 
        self.kovatype("I'm gonna turn this chat off while I'm with mom, so I don't get caught")
        self.kovatype("See you after breakfast!")
        user_data["chapter"] = 13
        return user_data

    def chapter13(self, input, user_data, user_id):
        self.kovatype("Hey Sorry I got back late") 
        self.kovatype("Mom and I came to downtown and I couldn't find the time to text you without her seeing me") 
        self.kovatype("What have you been up to?")
        user_data["chapter"] = 14
        return user_data

    def chapter14(self, input, user_data, user_id):
        #Handle response
        self.kovatype("Mom went to a VR cafe with her friends.") 
        self.kovatype("They're going to checkout the new Euro Tour Package until lunch.") 
        self.kovatype("Oh, do you know what VR is?")
        self.kovatype("I learnt when it emerged in world history, but can't remember if it's before or after your year.")
        user_data["chapter"] = 15
        return user_data

    def chapter15(self, input, user_data, user_id):
        #TRUST SCORE ADJUSTMENT BASED ON ANSWER
        self.kovatype("Well, I'm at a hair salon for a haircut right now.") 
        self.kovatype("I just reserved a seat and ordered a Monica Cut.") 
        self.kovatype("She's the celebrity that many of my classmates like too")
        self.kovatype("Do you like any celebrity? Which one?")
        user_data["chapter"] = 16
        return user_data

    def chapter16(self, input, user_data, user_id):
        #wait 1 min, and respond appropriately
        self.kovatype("One sec...") 
        self.kovatype("Getting a haircut...") 
        #wait 1 more min
        self.kovatype("I always wonder when households will be able to purchase these haircut drones.")
        self.kovatype("It's still illegal, because they're equipped with sharp blades and can be used as weapons.")
        self.kovatype("Maybe someone from my future will talk to me one day to chat with me about each other's worlds!")
        self.kovatype("Guess what? I'm visiting dad's workplace today! That's why I got my haircut. :)")
        user_data["chapter"] = 17
        return user_data

    def chapter17(self, input, user_data, user_id):
        self.kovatype("Ah crap... I forgot to turn off my Starbucks setting.") 
        self.kovatype("Just got a notification that my Frappucino is ready, cuz last time, I told them to prepare a Frappucino everytime I approach Starbucks.") 
        self.kovatype("I should pick it up, since I shouldn't waste good coffee, even if it's all paid for by the government through universal income.")
        self.kovatype("You know, when I was still a young girl, we still had some shops in downtown where human staffs greeted me.")
        self.kovatype("It'd be cruel to ask any human to spend their time at a shop working these days, but I miss human service sometimes.")
        user_data["chapter"] = 18
        return user_data

    def chapter18(self, input, user_data, user_id):
        self.kovatype("Mom's coming in an autonomous Waymo right now, so I'm gonna leave for a sec.") 
        self.kovatype("I'll let you know all about dad's workplace when I get there!") 
        self.kovatype("They'll show me some advanced research today too, so should be exciting!")
        self.kovatype("Bye!")
        user_data["chapter"] = 19
        return user_data

    """ ACT 3 """