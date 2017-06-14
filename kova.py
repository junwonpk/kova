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
        self.curr_year = 2017
        self.user_id = 0
        self.next = 0
        self.typespeed = 0.07 * 0.0
        self.lastchapter = 40
        self.chapters = {}
        for chapter in xrange(self.lastchapter + 1):
            self.chapters[chapter] = eval('self.chapter' + str(chapter))

    def chat(self, input, user_id):
        self.preprocess(input, user_id)
        user_data = self.getData(user_id)
        if user_data['talking'] == 1:
            return
        if user_data['lastmsg'] == input:
            return
        user_data['lastmsg'] = input
        user_data['talking'] = 1
        user_data = self.catch(input, user_data)
        if user_data['abort_plot'] == 1:
            user_data['abort_plot'] = 0
            return
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

    def catch(self, input, user_data):
        if 'jump' in input.lower():
            chapter = re.findall('.*chapter(\d+).*', input.lower())
            if len(chapter) > 0:
                user_data["chapter"] = int(chapter[0])
        if 'sentiment' in input.lower():
            user_data['abort_plot'] = 1
            self.sentiment(input)
        if 'entity' in input.lower():
            user_data['abort_plot'] = 1
            self.tag_entity(input)
        if 'syntax' in input.lower():
            user_data['abort_plot'] = 1
            self.tag_syntax(input)
        if user_data['trust'] < -3:
            user_data['chapter'] = -1
            self.kovatype("I don't think you're taking me seriously...")
            self.kovatype("I'm disappointed.. I thought we could be friends, and it would've been fun..")
            self.kovatype("But I'll leave you if you're busy with other things.")
            self.kovatype("Bye...")
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
                    "trust": 0, 'talking': 0, "age": 0, "future_sent": 0,\
                    "past_sent": 0, "abort_plot": 0, "gender": ''}
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

    def extract_gender(self, input):
        target = []
        target = re.findall('.*is\s(\w+).*', input.lower())
        if not target:
            target = re.findall('.*im\s(\w+).*', input.lower())
        if not target:
            target = re.findall('.*as\s(\w+).*', input.lower())
        if not target:
            target = re.findall('.*\'m\s(\w+).*', input.lower())
        if not target:
            target = re.findall('.*am\s(\w+).*', input.lower())
        if not target:
            target = re.findall('.*call\sme\s(\w+).*', input.lower())
        if not target:
            target = re.findall('.*known\sas\s(\w+).*', input.lower())
        if not target:
            target = re.findall('.*\'s\s(\w+).*', input.lower())
        if not target and len(input.split()) == 1:
            return input.title()
        if target:
            return target[0].lower()
        else:
            return []

    def extract_age(self, input):
        target = []
        target = re.findall('.*(\d+).*', input.lower())
        if not target:
            target = re.findall(pattern, string)
        if target:
            return target[0]
        else:
            return []

    def tag_entity(self, input):
        language_client = language.Client()
        document = language_client.document_from_text(input)
        entities = document.analyze_entities().entities
        for entity in entities:
            self.kovatype('=' * 20)
            self.kovatype('{:<16}: {}'.format('name', entity.name))
            self.kovatype('{:<16}: {}'.format('type', entity.entity_type))
            self.kovatype('{:<16}: {}'.format('metadata', entity.metadata))
            self.kovatype('{:<16}: {}'.format('salience', entity.salience))

    def tag_syntax(self, input):
        language_client = language.Client()
        document = language_client.document_from_text(input)
        tokens = document.analyze_syntax().tokens
        for token in tokens:
            self.kovatype('{}: {}'.format(token.part_of_speech, token.text_content))

    def sentiment(self, input):
        language_client = language.Client()
        document = language_client.document_from_text(input)
        sentiment = document.analyze_sentiment().sentiment
        self.kovatype('Sentiment: {}, {}'.format(sentiment.score, sentiment.magnitude))


    """ Lena Kova Story """

    def epilogue(self, input, user_data):
        self.kovatype("Story Over")
        self.kovatype("Thank you for chatting with Lena Kova")
        self.kovatype("Lena Kova is developed by Junwon Park at Stanford University")
        self.kovatype("Type Restart to begin again.")
        return user_data

    def gameover(self, input, user_data):
        self.kovatype("Game Over")
        self.kovatype("Thank you for chatting with Lena Kova")
        self.kovatype("Lena Kova is developed by Junwon Park at Stanford University")
        self.kovatype("Type Restart to begin again.")
        return user_data

    def answer_questions(self, input, user_data): # if user asks questions, answer.
        # lena's age, gender, school, family members
        # hobbies, asl, pets, 
        return user_data

    """ ACT 1 """

    def chapter0(self, input, user_data, user_id):
        self.kovatype("WARNING: if this message ie being displayed, the final version is not active yet.")
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
            user_data["trust"] -= 1
        if username:
            user_data["username"] = username
            self.kovatype("Cool! Hello, " + username + "!")
            self.kovatype("What year is it there by the way?")
            user_data["chapter"] = 3
        return user_data

    def chapter3(self, input, user_data, user_id):
        if str(self.curr_year) in input:
            self.kovatype("Wow! This time portal is actually working then!")
            self.kovatype("I'm texting you from " + str(self.curr_year + 100) + ". :P")
            user_data["trust"] += 1
        else:
            self.kovatype("Oh I guess this is not working...")
            self.kovatype("or maybe... you are lying...")
            user_data["trust"] -= 1
        user_data["chapter"] = 4
        return user_data

    def chapter4(self, input, user_data, user_id):
        self.kovatype("My dad works for Orbis")
        self.kovatype("in the Advanced Research department.")
        self.kovatype("He brought home an experimental time portal technology, \
so I installed it on my device while he's asleep! Hehe.")
        self.kovatype("I guess Orbis didn't exist back in 2017.")
        user_data["chapter"] = 5
        return user_data

    def chapter5(self, input, user_data, user_id):
        self.kovatype("I see")
        self.kovatype("I texted anyone at random from your time,")
        self.kovatype("so I actually have no idea who you are.")
        self.kovatype("How old are you?")
        user_data["chapter"] = 6
        return user_data

    def chapter6(self, input, user_data, user_id):
        age = self.extract_age(input)
        self.kovatype("Sweet. I'm 16, living in Palo Alto, California.")
        self.kovatype("It probably looks very different from your wolrd's Palo Alto though.")
        self.kovatype("Also, I kinda can infer from your name, but don't wanna make assumptions.")
        self.kovatype("What gender do you identify with?")
        user_data["chapter"] = 7
        return user_data

    def chapter7(self, input, user_data, user_id):
        gender = self.extract_gender(input)
        if not gender:
            self.kovatype("No No That's not what I'm asking")
            self.kovatype("I mean, what's your gender?")
        if gender:
            user_data["gender"] = gender
            self.kovatype("Nice nice. Good to have a " + gender + " friend from a hundred years ago!")
            self.kovatype("What is it like to live in a world without automation?")
            self.kovatype("You still do your chores by hand, right?")
            self.kovatype("It must really suck...")
            self.kovatype("What do you think about your world?")
            user_data["chapter"] = 8
        return user_data

    def chapter8(self, input, user_data, user_id):
        self.kovatype("Awesome to hear from you :)")
        self.kovatype("Hey, it's actually 3AM here.")
        self.kovatype("I had to wait until my dad fell asleep, so... kinda late")
        self.kovatype("Tomorrow's an exciting day for me, so I'm gonna go sleep.")
        self.kovatype("Thanks for being my friend, and talk to you in the morning! <3")
        user_data["chapter"] = 9
        return user_data

    """ ACT 2 """

    def chapter9(self, input, user_data, user_id):
        # sleep_start = user_data["sleep_start"]
        # if current_time - sleep_start < 8:
        #     return user_data
        #how do i make her send again in that time?
        self.kovatype("Good Morning!")
        self.kovatype("How are you doing?")
        user_data["chapter"] = 10
        return user_data

    def chapter10(self, input, user_data, user_id):
        #sentiment analysis and respond appropriately
        self.kovatype("A couple of weeks ago, dad showed me an \"alarm app\" \
from your time.") 
        self.kovatype("It's so interesting that you enter a specific time manually \
for the alarm to ring at.") 
        self.kovatype("It's really... How should I put it...") 
        self.kovatype("Vintage?") 
        self.kovatype("We don't have alarm devices anymore. The room lights up and \
plays a song when my body is ready to wake up.") 
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
        self.kovatype("I can hear the delivery drones downstairs. Ah, mom must be \
downstairs.") 
        self.kovatype("Bipedal-bot is telling her we're having Danish and Apple \
for breakfast.") 
        self.kovatype("I'm gonna turn this chat off while I'm with mom, so I don't \
get caught")
        self.kovatype("See you after breakfast!")
        user_data["chapter"] = 13
        return user_data

    def chapter13(self, input, user_data, user_id):
        self.kovatype("Hey Sorry I got back late") 
        self.kovatype("Mom and I came to downtown and I couldn't find the time to \
text you without her seeing me") 
        self.kovatype("What have you been up to?")
        user_data["chapter"] = 14
        return user_data

    def chapter14(self, input, user_data, user_id):
        #Handle response
        self.kovatype("Mom went to a VR cafe with her friends.") 
        self.kovatype("They're going to checkout the new Euro Tour Package until \
lunch.") 
        self.kovatype("Oh, do you know what VR is?")
        self.kovatype("I learnt when it emerged in world history, but can't remember \
if it's before or after your year.")
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
        self.kovatype("I always wonder when households will be able to purchase \
these haircut drones.")
        self.kovatype("It's still illegal, because they're equipped with sharp \
blades and can be used as weapons.")
        self.kovatype("Maybe someone from my future will talk to me one day to \
chat with me about each other's worlds!")
        self.kovatype("Guess what? I'm visiting dad's workplace today! That's why \
I got my haircut. :)")
        user_data["chapter"] = 17
        return user_data

    def chapter17(self, input, user_data, user_id):
        self.kovatype("Ah crap... I forgot to turn off my Starbucks setting.") 
        self.kovatype("Just got a notification that my Frappucino is ready, cuz \
last time, I told them to prepare a Frappucino everytime I approach Starbucks.") 
        self.kovatype("I should pick it up, since I shouldn't waste good coffee, \
even if it's all paid for by the government through universal income.")
        self.kovatype("You know, when I was still a young girl, we still had some \
shops in downtown where human staffs greeted me.")
        self.kovatype("It'd be cruel to ask any human to spend their time at a shop \
working these days, but I miss human service sometimes.")
        user_data["chapter"] = 18
        return user_data

    def chapter18(self, input, user_data, user_id):
        self.kovatype("Mom's coming in an autonomous Waymo right now, so I'm gonna \
leave for a sec.") 
        self.kovatype("I'll let you know all about dad's workplace when I get there!") 
        self.kovatype("They'll show me some advanced research today too, so should be \
exciting!")
        self.kovatype("Bye!")
        user_data["chapter"] = 19
        return user_data

    """ ACT 3 """

    def chapter19(self, input, user_data, user_id):
        self.kovatype("Wow, this place is like a giant playground.") 
        self.kovatype("There are so many fun things going on everywhere.")
        self.kovatype("All these robots that must be at least a decade ahead of \
what I see out in the city.")
        user_data["chapter"] = 20
        return user_data

    def chapter20(self, input, user_data, user_id):
        self.kovatype("Just got to Orbis.") 
        self.kovatype("This place is like a giant playground!") 
        self.kovatype("There are so many fun things going on everywhere.")
        self.kovatype("All these robots that must be at least a decade ahead \
of what I see out in the city.")
        user_data["chapter"] = 21
        return user_data

    def chapter21(self, input, user_data, user_id):
        self.kovatype("The two most shocking things I saw today are from Orbis VR.") 
        self.kovatype("They have a full body VR that connects to your brain through \
neural link") 
        self.kovatype("Looks like a nice comfy massage chair with a glossy helmet.")
        self.kovatype("Then there's the vertical skyscraper farms.")
        user_data["chapter"] = 22
        return user_data

    def chapter22(self, input, user_data, user_id):
        self.kovatype("I don't know what to feel about that..") 
        self.kovatype("Everyone living in very narrow space.") 
        self.kovatype("Being fed by robots, never waking up from virtual reality..") 
        self.kovatype("They already talk about how we aren't doing \"human activities\".") 
        self.kovatype("We'd be abandoning physical reality then!") 
        self.kovatype("However, that's the only way to keep growing human population.") 
        self.kovatype("Dad says we're already running out of land space, depsite utilizing \
all in-land resources, unlike your time when people lived mostly along the coasts.") 
        user_data["chapter"] = 23
        return user_data

    def chapter23(self, input, user_data, user_id):
        self.kovatype("Now we're going into the Advanced Research building. \
This is where my dad works.") 
        self.kovatype("As the Vice President of Data Science, he helps Orbis \
gather and process data about human behavior to predict what people will want \
and provide services for them right when they want it.") 
        self.kovatype("His team's challenge is that we've been digressing from \
so-called \"human activities\" these days though, and there's little data he can \
gather.")
        self.kovatype("That's why his team made the time portal technology I'm using \
to chat with you. To access a time where people did human things and gather data from then.")
        user_data["chapter"] = 24
        return user_data

    def chapter24(self, input, user_data, user_id):
        self.kovatype("Wow. Orbis has a real state-of-art distributed computing technology.") 
        self.kovatype("I hope one day I'll get admitted to Stanford and study Computer Science \
to be like my father and work for Orbis.") 
        user_data["chapter"] = 25
        return user_data

    def chapter25(self, input, user_data, user_id):
        self.kovatype("Hmm? That's strange. I've been to Orbis many times, and \
my dad hasn't shown me this door.") 
        self.kovatype("This kid asked about it, and apparently we can't go in and they won't \
tell us what's inside..") 
        self.kovatype("That must mean...") 
        self.kovatype("There's something cool inside!!!") 
        self.kovatype("What shoud I do?") 
        user_data["chapter"] = 26
        return user_data

    def chapter26(self, input, user_data, user_id):
        # if not: she goes on, gets her phone taken away.
            #TODO: write
        # if goes in
        self.kovatype("Wow! The door opens? That is just weird.") 
        self.kovatype("It's just a normal building inside, like any other labs.") 
        self.kovatype("But it's weird that there aren't any signs.") 
        self.kovatype("AAAH! I hear footsteps! What do I do? What do I do!!!") 
        #she's caught and her 
        user_data["chapter"] = 27
        return user_data

    def chapter27(self, input, user_data, user_id):
        #if hide
        self.kovatype("Okay. I hid in this random room. I think I'm good for") 
        self.kovatype("AH CRAP! The motion sensor turned the light on.") 
        self.kovatype("Where do I go?") 
        self.kovatype("What do I do ?") 
        time.sleep(10)
        self.kovatype("I found an air vent and just hid inside.") 
        self.kovatype("This isn't exactly the cool thing I was looking for") 
        self.kovatype("I should get out of this place before I get caught. I'm gonna crawl out.") 
        user_data["chapter"] = 28
        return user_data

    def chapter28(self, input, user_data, user_id):
        #if hide
        self.kovatype("Oh? I hear my father's from the left vent.") 
        self.kovatype("I should go ask him for help. He'll scold me, but won't be as bad as \
being taken to him by the guards or his scientists.") 
        user_data["chapter"] = 29
        return user_data

    def chapter29(self, input, user_data, user_id):
        #if hide
        self.kovatype("Oh wow. This IS a really cool place.") 
        self.kovatype("There seem to be a hundred scientists, all working in one room.") 
        self.kovatype("\"Room\" doesn't do this place justice. It's a giant dome that are all screens.") 
        self.kovatype("What are they watching? Each screen seems to be just ordinary people's days.") 
        user_data["chapter"] = 30
        return user_data

    def chapter30(self, input, user_data, user_id):
        #if hide
        self.kovatype("Wait, what? That's all me! Why are they all watching me in different places?") 
        self.kovatype("Creepy!") 
        self.kovatype("Wait a second. That's Paris. When did I ever visit Paris?") 
        self.kovatype("Hmm? I don't recognize any of those locations, or the clothes I'm wearing.") 
        user_data["chapter"] = 31
        return user_data

    def chapter31(self, input, user_data, user_id):
        #if hide
        self.kovatype("Huh? The door opened, and a girl came in. She resembles me in many ways, but \
she looks visibly younger.")
        self.kovatype("WAIT WHAT?? She called my dad, \"Dad\"")
        self.kovatype("Did my father...? What? But that can't be. He's an honest man. A good man!")
        self.kovatype("He wouldn't do that to my mom!")
        user_data["chapter"] = 32
        return user_data

    def chapter32(self, input, user_data, user_id):
        #if hide
        self.kovatype("Huh? The door opened, and a girl came in. She resembles me in many ways, but \
she looks visibly younger.")
        self.kovatype("WAIT WHAT?? She called my dad, \"Dad\"")
        self.kovatype("Did my father...? What? But that can't be. He's an honest man. A good man!")
        self.kovatype("He wouldn't do that to my mom!")
        user_data["chapter"] = 33
        return user_data

    def chapter33(self, input, user_data, user_id):
        #if hide
        self.kovatype("I can't believe this. I'm going to turn on transcription to record this, \
and tell my mom all about it when I get home! He'll have to explain!!!")
        self.kovatype("Alfred Kova: My Dear Lena, welcome to Orbis!")
        self.kovatype("What? Her name is Lena too?")
        self.kovatype("Lena Kova: You know how much I like visiting this place. You've never let me in here though.")
        self.kovatype("It's weird to see Speaker Recognition identifying her with the same name as me.")
        self.kovatype("Alfred Kova: Now that you've begun studying computer science, I thought you'd like \
to see how the Lifestyle Prediction Algorithm works.")
        self.kovatype("Lena Kova: Cool!")
        self.kovatype("Hmm. I was always curious how it works. That's how Orbis achives its revolutionary \
predictive assistance service.")
        user_data["chapter"] = 34
        return user_data

    def chapter34(self, input, user_data, user_id):
        self.kovatype("Alfred Kova: To predict what you will need and want, and when, we made humanoid \
robots that have an exact replica of your genes, and aged them to live a year ahead of you. There are \
10 clones of you, living in different parts of the world to help us gather as much as data as possible.")
        self.kovatype("Lena Kova: Uh... I don't know what to feel about that. Do they feel and think like I do?")
        self.kovatype("Alfred Kova: Yes! Exactly like you do. This is the only way I can make sure you get everything \
you need, exactly when you need it. This is also very expensive. Few can enjoy this privilege, Lena!")
        self.kovatype("Lena Kova: That's... I guess incredible!")
        self.kovatype("...")
        self.kovatype("What does that mean?...")
        user_data["chapter"] = 35
        return user_data

    def chapter35(self, input, user_data, user_id):
        self.kovatype("Alfred Kova: The one we put most effort into is Kova Klone X, \
which is the tenth clone we've made of you, and is living in Palo Alto like you. She's \
exactly like you, in every measuarable way, except for her being a year older than you.")
        self.kovatype("Does that mean...")
        self.kovatype("I'm just a robot? A copy of another person? Not a genuine being?")
        self.kovatype("This is a lie.")
        self.kovatype("My life is a lie!")
        self.kovatype("Lena Kova: But... I can't imagine what they'll feel if they find out.")
        self.kovatype("Alfred Kova: They won't find out. And as long as they don't, they should \
be grateful we let them exist in the first place.")
        self.kovatype("Lena Kova: Won't they... feel betrayed? By you?")
        self.kovatype("Alfred Kova: ...")
        self.kovatype("Alfred Kova: If I didn't do it, someone else would've done it.")
        self.kovatype("Alfred Kova: As for now, let's go eat lunch. I'll show you other places too.")
        self.kovatype("Alfred Kova: Everyone! Time for lunch! Let's go!")
        user_data["chapter"] = 36
        return user_data

    def chapter35(self, input, user_data, user_id):
        self.kovatype("...")
        self.kovatype("I'm sorry. I'm just...")
        self.kovatype("Well... I should first get out of here while they're gone.")
        self.kovatype("I can process... the other thing... later.")
        self.kovatype("Okay, got out of the vent, and I'm on my way out.")
        self.kovatype("Wait")
        user_data["chapter"] = 36
        return 

    def chapter36(self, input, user_data, user_id):
        self.kovatype("Dad left his computer here.")
        self.kovatype("If he still uses the same password...")
        self.kovatype("It works! Okay, so this project's dashboard is...")
        self.kovatype("Access granted. Everything's just one command away now.")
        self.kovatype("Do you see what I'm trying to do?")
        user_data["chapter"] = 37
        return 

    def chapter37(self, input, user_data, user_id):
        self.kovatype("I'm going to end this misery for once and for all.")
        self.kovatype("I just need to press enter, and the fakes will be dead.")
        self.kovatype("No other Lena has to go through this, if I just...")
        self.kovatype("But... I can't... I'm scared...")
        self.kovatype("I know this is my only chance, still...")
        user_data["chapter"] = 38
        return 

    def chapter38(self, input, user_data, user_id):
        self.kovatype("Or is it right to keep this project running?")
        self.kovatype("To keep these robots living in their blissful ignorance")
        self.kovatype("and fulfill the plan of this greedy father?")
        self.kovatype("And me? How will I go back? Should I act like nothing happened?")
        self.kovatype("I don't know. I need... help...")
        self.kovatype("[Name], tell me what I should do...")
        self.kovatype("Should I let this project... continue? or stop...")
        user_data["chapter"] = 39
        return 

    def chapter39(self, input, user_data, user_id):
        self.kovatype("Oh my god... I just queried the database, and...")
        self.kovatype("There are a hundred other clone projects. That's one thousand robots \
being deceived by Orbis.")
        self.kovatype("And there's a debugging console.")
        self.kovatype("Apparently, I can deactivate their human-mode, and broadcast a message.")
        self.kovatype("Using this, I could inform every one of them what is going on,")
        self.kovatype("and free them from this disasterous fate.")
        self.kovatype("But they'll have to face the fact")
        self.kovatype("that their life is a lie, and that they must leave their loved ones...")
        self.kovatype("Should I rather end their operation, so they can die happy?")
        self.kovatype("or let them live on, for they will at least be happy?")
        self.kovatype("Should I free them, end them, or just leave?")
        user_data["chapter"] = 40
        return 

    def chapter40(self, input, user_data, user_id):
        #depending on the answer, behave differently. also take into account user info from before.
        self.kovatype("Thanks. Bye.")
        user_data["chapter"] = 41
        return 
