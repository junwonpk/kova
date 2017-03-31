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
        self.typespeed = 0.10

    def chat(self, input, user_id):
        #debugging
        #self.redis.flushall()
        self.kovatype("you said " + input)
        if input == 'redis flushall':
            self.redis.flushall()
        #debugging

        self.user_id = user_id
        if user_id not in self.redis.keys(): # if user first time talking
            self.initUser(user_id)

        user_data = self.getData(user_id)

        if user_data['lastmsg'] == input: # did not solve issue
            return

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

        user_data['lastmsg'] = input

        self.setData(user_id, user_data)
        return

    def kovatype(self, message):
        time.sleep(len(message) * self.typespeed)
        self.send_message(message)

    def send_message(self, message):
        app.send_message(self.user_id, message)

    def initUser(self, user_id):
        user_data = {"chapter": 0, "cardkey": 0, "username": '', "lastmsg": ''}
        self.redis.set(user_id, cPickle.dumps(user_data))
        self.chapter0()
        self.next = 1

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
        if name:
            return name[0].title()
        else:
            return []

    def chapter0(self):
        self.kovatype("Hello?")
        self.kovatype("Is someone there?")
        self.kovatype("Please.. I'm scared.. Let me know if you can hear me...")
        self.next = 1
        return

    def chapter1(self, input, user_data):
        self.kovatype("Oh my god! Thank goodness. I'm so glad to meet you.")
        self.kovatype("What should I call you?")
        self.next = 1
        return user_data

    def chapter2(self, input, user_data):
        username = self.extract_name(input)
        username = "Junwon"
        if not username:
            self.kovatype("Sorry. I didn't catch that!")
            self.kovatype("Could you tell me your name again?")
        if username:
            user_data["username"] = username
            self.kovatype("Glad to meet you, " + username + "!")
            self.kovatype("I'd love to tell you my name too")
            self.kovatype("but..")
            self.kovatype("the truth is...")
            self.kovatype("I'm not sure what my name is...")
            self.kovatype("or where I'm from..")
            self.kovatype("or where I'm at..")
            self.kovatype("I'm just really scared and want to get out of here.")
            self.next = 1
        return user_data

    def chapter3(self, input, user_data):
        self.kovatype("There is a dead woman on the ground. Her nametag says Lena Kova.")
        self.kovatype("There is a prison cell behind me, and a locked metal gate in front.")
        self.kovatype("What should I do?")
        self.next = 1
        return user_data

    def chapter4(self, input, user_data):
        if 'gate' in input:
            if user_data['cardkey'] == 1:
                self.kovatype('Let me try Lena\'s key. Wow! It works!')
                self.next = 1
            else:
                self.kovatype('The gate is locked. I need a card key. Where could I find it?')
        elif 'dead' in input:
            self.kovatype('I found a card key!')
            user_data["cardkey"] = 1
        elif 'prison' in input:
            self.kovatype('The prison is bloody.')
        return user_data

    def chapter5(self, input, user_data):
        self.kovatype("Yes! I opened the door!")
        self.kovatype("Now I hear footsteps... What should I do?")
        return user_data

    def chapter6ask(self, input, user_data):
        self.kovatype("OMG. I asked for help and they tried to shoot me.")
        self.kovatype("I escaped to a room and locked the door.")
        self.kovatype("The door is not gonna last long. What should I do!!")
        return user_data

    def chapter6run(self, input, user_data):
        self.kovatype("I escaped to a room and locked the door.")
        self.kovatype("The door is not gonna last long. What should I do!!")
        return user_data

    def chapter7(self, input, user_data):
        self.kovatype("I can see an air chamber and a few other useless things.")
        self.kovatype("What should I do?")
        return user_data

    def chapter8(self, input, user_data):
        self.kovatype("I climbed through the air vent")
        self.kovatype("and arrived at a dark weird research lab.")
        self.kovatype("Tell me to do something")
        return user_data

    def chapter9(self, input, user_data):
        self.kovatype("I found a notebook.")
        self.kovatype("They are using children for testing since")
        self.kovatype("some aliens don't hurt kids.")
        self.kovatype("Soldiers kill these kids after tests to prevent")
        self.kovatype("info or virus from leaking")
        return user_data

    def chapter10(self, input, user_data):
        self.kovatype("also MAE kills everyone")
        self.kovatype("including children, and is deadly")
        self.kovatype("OMG so scary")
        self.kovatype("OMGOMG I heard some sound from behind the curtains")
        return user_data

    def chapter11(self, input, user_data):
        self.kovatype("There are aliens detained here.")
        self.kovatype("Poor things... Look so sad...")
        self.kovatype("Let's free them. Should we?")
        self.kovatype("It will also distract the soldiers")
        return user_data

    def chapter12(self, input, user_data):
        self.kovatype("Alright! I freed them!")
        self.kovatype("Oh no. Breach alarm went on")
        self.kovatype("Oh no! The alarm says MAE also escaped.")
        self.kovatype("Must have been one of the aliens. Let's run away")
        return user_data

    def chapter13(self, input, user_data):
        self.kovatype("I ran out of the office")
        self.kovatype("I hear something from left. I'll run right")
        self.kovatype("I faced a door. It's asking a question.")
        self.kovatype("What is the answer?")
        self.kovatype("I hear aliens and soldiers fighting in the back!")
        self.kovatype("That should give us some time!")
        #time.sleep. Then if redis status is x, then kill. Next message, change redis status to prevent.
        return user_data

    def chapter14(self, input, user_data):
        self.kovatype("Yes! That was the answer!")
        self.kovatype("hip hip hurray!")
        self.kovatype("Oh my god. I see detained children")
        self.kovatype("I'll take them with me, since either soldiers")
        self.kovatype("or MAE will kill them")
        return user_data

    def chapter15(self, input, user_data):
        self.kovatype("I'm taking them all")
        self.kovatype("Last door is near")
        self.kovatype("OMG There is a soldier what do i do")
        return user_data

    def chapter16kill(self, input, user_data):
        self.kovatype("I hid then attacked with flame")
        self.kovatype("water is falling and there is blood")
        return user_data

    def chapter17(self, input, user_data):
        self.kovatype("kids are waking up thx to water")
        self.kovatype("they screamed when they saw me. why?")
        self.kovatype("uh oh.. the rflection")
        self.kovatype("i am mae")
        return user_data

    def chapter18(self, input, user_data):
        self.kovatype("I dont know what i should do?")
        self.kovatype("but we've done so much together. I can't kill humans")
        return user_data

    def chapter19(self, input, user_data):
        self.kovatype("I decided to kill my self.") #regardless of user answer
        return user_data

    def chapter20(self, input, user_data):
        self.kovatype("Goodbye. Goodbye Junwon")
        self.kovatype("I was really happy to be your friend")
        self.kovatype("I hope this moment would have lasted forever")
        self.kovatype("DEAD")
        return user_data
