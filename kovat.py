import re
import time

class Kovat:

    def __init__(self):
        self.chapter = 0
        self.username = "name"
        self.cardkey = 0
        self.next = 0

    def chat(self, input):
        if self.chapter == 0:
            self.chapter0()
        if self.chapter == 1:
            self.chapter1()
        if self.chapter == 2:
            self.chapter2(input)
        if self.chapter == 3:
            self.chapter3()
        if self.chapter == 4:
            if 'gate' in input and self.cardkey == 0:
                self.chapter4gate0()
            if 'gate' in input and self.cardkey == 1:
                self.chapter4gate1()
            if 'corpse' in input:
                self.chapter4dead()
            if 'prison' in input:
                self.chapter4prison()
        if self.chapter == 5:
            self.chapter5()
        if self.chapter == 6:
            if 'ask' in input:
                self.chapter6ask()
            if 'run' in input:
                self.chapter6run()
        if self.chapter == 7:
            self.chapter7()
        if self.chapter == 8:
            self.chapter8()
        if self.chapter == 9:
            self.chapter9()
        if self.chapter == 10:
            self.chapter10()
        if self.chapter == 11:
            self.chapter11()
        if self.chapter == 12:
            self.chapter12()
        if self.chapter == 13:
            self.chapter13()
        if self.chapter == 14:
            self.chapter14()
        if self.chapter == 15:
            self.chapter15()
        if self.chapter == 16:
            self.chapter16()
        if self.chapter == 17:
            self.chapter17()
        if self.chapter == 18:
            self.chapter18()
        if self.chapter == 19:
            self.chapter19()
        if self.chapter == 20:
            self.chapter20()
        else:
            print 'done'
        if self.next == 1:
            self.chapter += 1
            self.next = 0
        return 'KOVA'

    def chapter20(self):
        print "Goodbye. Goodbye Junwon"
        print "I was really happy to be your friend"
        print "I hope this moment would have lasted forever"
        print "DEAD"

    def chapter19(self):
        print "I decided to kill my self." #regardless of user answer

    def chapter18(self):
        print "I dont know what i should do?"
        print "but we've done so much together. I can't kill humans"

    def chapter17(self):
        print "kids are waking up thx to water"
        print "they screamed when they saw me. why?"
        print "uh oh.. the rflection"
        print "i am mae"

    def chapter16kill(self):
        print "I hid then attacked with flame"
        print "water is falling and there is blood"

    def chapter15(self):
        print "I'm taking them all"
        print "Last door is near"
        print "OMG There is a soldier what do i do"

    def chapter14(self):
        print "Yes! That was the answer!"
        print "hip hip hurray!"
        print "Oh my god. I see detained children"
        print "I'll take them with me, since either soldiers"
        print "or MAE will kill them"

    def chapter13(self):
        print "I ran out of the office"
        print "I hear something from left. I'll run right"
        print "I faced a door. It's asking a question."
        print "What is the answer?"
        print "I hear aliens and soldiers fighting in the back!"
        print "That should give us some time!"
        #time.sleep. Then if redis status is x, then kill. Next message, change redis status to prevent.

    def chapter12(self):
        print "Alright! I freed them!"
        print "Oh no. Breach alarm went on"
        print "Oh no! The alarm says MAE also escaped."
        print "Must have been one of the aliens. Let's run away"

    def chapter11(self):
        print "There are aliens detained here."
        print "Poor things... Look so sad..."
        print "Let's free them. Should we?"
        print "It will also distract the soldiers"

    def chapter10(self):
        print "also MAE kills everyone"
        print "including children, and is deadly"
        print "OMG so scary"
        print "OMGOMG I heard some sound from behind the curtains"

    def chapter9(self):
        print "I found a notebook."
        print "They are using children for testing since"
        print "some aliens don't hurt kids."
        print "Soldiers kill these kids after tests to prevent"
        print "info or virus from leaking"

    def chapter8(self):
        print "I climbed through the air vent"
        print "and arrived at a dark weird research lab."
        print "Tell me to do something"

    def chapter7(self):
        print "I can see an air chamber and a few other useless things."
        print "What should I do?"

    def chapter6ask(self):
        print "OMG. I asked for help and they tried to shoot me."
        print "I escaped to a room and locked the door."
        print "The door is not gonna last long. What should I do!!"

    def chapter6run(self):
        print "I escaped to a room and locked the door."
        print "The door is not gonna last long. What should I do!!"

    def chapter5(self):
        print "Yes! I opened the door!"
        print "Now I hear footsteps... What should I do?"

    def chapter4gate0(self):
        print 'The gate is locked. I need a card key. Where could I find it?'
    def chapter4gate1(self):
        print 'Let me try Lena\'s key. Wow! It works!'
        self.next = 1
    def chapter4dead(self):
        print 'I found a card key!'
        self.cardkey = 1
    def chapter4prison(self):
        print 'The prison is bloody.'

    def chapter3(self):
        print "There is a dead woman on the ground. Her nametag says Lena Kova."
        print "There is a prison cell behind me, and a locked metal gate in front."
        print "What should I do?"
        self.next = 1

    def chapter2(self, input):
        self.username = self.extract_name(input)
        print "Glad to meet you, " + self.username + "!"
        print "I'd love to tell you my name too"
        print "but.."
        print "the truth is..."
        print "I'm not sure what my name is..."
        print "or where I'm from"
        print "or where I am"
        print "I'm just really scared and want to get out of here."
        self.next = 1

    def chapter1(self):
        print "Oh my god! Thank goodness. I'm so glad to meet you."
        print "What should I call you?"
        self.next = 1

    def chapter0(self):
        print "Hello?"
        print "Is someone there?"
        print "Please.. I'm scared.. Let me know if you can hear me..."
        self.next = 1

    def extract_name(self, input):
        name = []
        while not name:
            name = re.findall('.*is\s(\w+).*', input.lower())
            if not name:
                name = re.findall('.*\'m\s(\w+).*', input.lower())
            if not name:
                name = re.findall('.*am\s(\w+).*', input.lower())
            if not name:
                name = re.findall('.*call\sme\s(\w+).*', input.lower())
            if not name:
                name = re.findall('.*known\sas\s(\w+).*', input.lower())
            if not name:
                print 'Kova: Sorry, I didn\'t catch that. Would you tell me your name again?\n'
                input = raw_input('User: ')
        return name[0].title()
