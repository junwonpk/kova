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

        user_data = self.getData(user_id)

        if user_data['chapter'] == 1:
            user_data = self.chapter1(input, user_data)
        if user_data['chapter'] == 2:
            user_data = self.chapter2(input, user_data)
        if user_data['chapter'] == 3:
            user_data = self.chapter3(input, user_data)
        if user_data['chapter'] == 4:
            user_data = self.chapter4(input, user_data)
        if user_data['chapter'] == 5:
            user_data = self.chapter5(input, user_data)
        if user_data['chapter'] == 6:
            user_data = self.chapter6(input, user_data)
        if user_data['chapter'] == 7:
            user_data = self.chapter7(input, user_data)
        if user_data['chapter'] == 8:
            user_data = self.chapter8(input, user_data)
        if user_data['chapter'] == 9:
            user_data = self.chapter9(input, user_data)
        if user_data['chapter'] == 10:
            user_data = self.chapter10(input, user_data)
        if user_data['chapter'] == 11:
            user_data = self.chapter11(input, user_data)
        if user_data['chapter'] == 12:
            user_data = self.chapter12(input, user_data)
        if user_data['chapter'] == 13:
            user_data = self.chapter13(input, user_data)
        if user_data['chapter'] == 14:
            user_data = self.chapter14(input, user_data)
        if user_data['chapter'] == 15:
            user_data = self.chapter15(input, user_data)
        if user_data['chapter'] == 16:
            user_data = self.chapter16(input, user_data)
        if user_data['chapter'] == 17:
            user_data = self.chapter17(input, user_data)
        if user_data['chapter'] == 18:
            user_data = self.chapter18(input, user_data)
        if user_data['chapter'] == 19:
            user_data = self.chapter19(input, user_data)
        if user_data['chapter'] == 20:
            user_data = self.chapter20(input, user_data)

        if self.next == 1:
            user_data['chapter'] += 1

        print user_data

        self.setData(user_id, user_data)
        return

    def kovatype(self, message):
        time.sleep(len(message) * 0.15)
        self.send_message(message)

    def send_message(self, message):
        app.send_message(self.user_id, message)

    def initUser(self, user_id):
        user_data = {"chapter": 0, "cardkey": 0, "username": ''}
        self.redis.set(user_id, cPickle.dumps(user_data))
        self.chapter0()
        self.next = 1

    def getData(self, user_id):
        return cPickle.loads(self.redis.get(user_id))

    def setData(self, user_id, user_data):
        self.redis.set(user_id, cPickle.dumps(user_data))

    def chapter0(self):
        self.kovatype("Hello?")
        self.kovatype("Is someone there?")
        self.kovatype("Please.. I'm scared.. Let me know if you can hear me...")
        self.next = 1

    def chapter1(self, input, user_data):
        self.kovatype("Oh my god! Thank goodness. I'm so glad to meet you.")
        self.kovatype("What should I call you?")
        self.next = 1
        return user_data

    def chapter2(self, input, user_data):
        username = self.extract_name(input)
        if not username:
            self.kovatype("Sorry. I didn't catch that!")
            self.kovatype("Could you tell me your name again?")
        else:
            user_data["username"] = username
            self.kovatype("Glad to meet you, " + username + "!")
            self.kovatype("I'd love to tell you my name too")
            self.kovatype("but..")
            self.kovatype("the truth is...")
            self.kovatype("I'm not sure what my name is...")
            self.kovatype("or where I'm from")
            self.kovatype("or where I am")
            self.kovatype("I'm just really scared and want to get out of here.")
            self.next = 1
        return user_data

    def extract_name(self, input):
        name = []
        name = re.findall('.*is\s(\w+).*', input.lower())
        if not name:
            name = re.findall('.*\'m\s(\w+).*', input.lower())
        if not name:
            name = re.findall('.*am\s(\w+).*', input.lower())
        if not name:
            name = re.findall('.*call\sme\s(\w+).*', input.lower())
        if not name:
            name = re.findall('.*known\sas\s(\w+).*', input.lower())
        if name:
            return name[0].title()
        else:
            return []

    def chapter3(self, input, user_data):
        self.kovatype("There is a dead woman on the ground. Her nametag says Lena Kova.")
        self.kovatype("There is a prison cell behind me, and a locked metal gate in front.")
        self.kovatype("What should I do?")
        self.next = 1
        return user_data

    def chapter4(self, input, user_data):
        if 'gate' in input:
            if user_data['cardkey'] == 1:
                kovatype('Let me try Lena\'s key. Wow! It works!')
                self.next = 1
            else:
                kovatype('The gate is locked. I need a card key. Where could I find it?')
        elif 'dead' in input:
            kovatype('I found a card key!')
            user_data["cardkey"] = 1
        elif 'prison' in input:
            kovatype('The prison is bloody.')
        return user_data

    def chapter5(self, input, user_data):
        kovatype("Yes! I opened the door!")
        kovatype("Now I hear footsteps... What should I do?")
        return user_data

    def chapter6ask(self, input, user_data):
        kovatype("OMG. I asked for help and they tried to shoot me.")
        kovatype("I escaped to a room and locked the door.")
        kovatype("The door is not gonna last long. What should I do!!")
        return user_data

    def chapter6run(self, input, user_data):
        kovatype("I escaped to a room and locked the door.")
        kovatype("The door is not gonna last long. What should I do!!")
        return user_data

    def chapter7(self, input, user_data):
        kovatype("I can see an air chamber and a few other useless things.")
        kovatype("What should I do?")
        return user_data

    def chapter8(self, input, user_data):
        kovatype("I climbed through the air vent")
        kovatype("and arrived at a dark weird research lab.")
        kovatype("Tell me to do something")
        return user_data

    def chapter9(self, input, user_data):
        kovatype("I found a notebook.")
        kovatype("They are using children for testing since")
        kovatype("some aliens don't hurt kids.")
        kovatype("Soldiers kill these kids after tests to prevent")
        kovatype("info or virus from leaking")
        return user_data

    def chapter10(self, input, user_data):
        kovatype("also MAE kills everyone")
        kovatype("including children, and is deadly")
        kovatype("OMG so scary")
        kovatype("OMGOMG I heard some sound from behind the curtains")
        return user_data

    def chapter11(self, input, user_data):
        kovatype("There are aliens detained here.")
        kovatype("Poor things... Look so sad...")
        kovatype("Let's free them. Should we?")
        kovatype("It will also distract the soldiers")
        return user_data

    def chapter12(self, input, user_data):
        kovatype("Alright! I freed them!")
        kovatype("Oh no. Breach alarm went on")
        kovatype("Oh no! The alarm says MAE also escaped.")
        kovatype("Must have been one of the aliens. Let's run away")
        return user_data

    def chapter13(self, input, user_data):
        kovatype("I ran out of the office")
        kovatype("I hear something from left. I'll run right")
        kovatype("I faced a door. It's asking a question.")
        kovatype("What is the answer?")
        kovatype("I hear aliens and soldiers fighting in the back!")
        kovatype("That should give us some time!")
        #time.sleep. Then if redis status is x, then kill. Next message, change redis status to prevent.
        return user_data

    def chapter14(self, input, user_data):
        kovatype("Yes! That was the answer!")
        kovatype("hip hip hurray!")
        kovatype("Oh my god. I see detained children")
        kovatype("I'll take them with me, since either soldiers")
        kovatype("or MAE will kill them")
        return user_data

    def chapter15(self, input, user_data):
        kovatype("I'm taking them all")
        kovatype("Last door is near")
        kovatype("OMG There is a soldier what do i do")
        return user_data

    def chapter16kill(self, input, user_data):
        kovatype("I hid then attacked with flame")
        kovatype("water is falling and there is blood")
        return user_data

    def chapter17(self, input, user_data):
        kovatype("kids are waking up thx to water")
        kovatype("they screamed when they saw me. why?")
        kovatype("uh oh.. the rflection")
        kovatype("i am mae")
        return user_data

    def chapter18(self, input, user_data):
        kovatype("I dont know what i should do?")
        kovatype("but we've done so much together. I can't kill humans")
        return user_data

    def chapter19(self, input, user_data):
        kovatype("I decided to kill my self.") #regardless of user answer
        return user_data

    def chapter20(self, input, user_data):
        kovatype("Goodbye. Goodbye Junwon")
        kovatype("I was really happy to be your friend")
        kovatype("I hope this moment would have lasted forever")
        kovatype("DEAD")
        return user_data
