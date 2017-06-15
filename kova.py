import os
import re
import sys
import app
import time
import redis
import cPickle
from google.cloud import language
from datetime import datetime, timedelta

reload(sys)
sys.setdefaultencoding('utf-8')

class Kova:

    def __init__(self):
        self.redis = redis.from_url(os.environ.get("REDISCLOUD_URL"))
        self.curr_year = 2017
        self.user_id = 0
        self.next = 0
        self.time = 0
        self.typespeed = 0.05
        self.resume_chapter = 0
        self.lastchapter = 40
        self.chapters = {}
        for chapter in xrange(self.lastchapter + 1):
            self.chapters[chapter] = eval('self.chapter' + str(chapter))
        self.word2num = {"ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,\
"fourteen":14, "fifteen":15, "sixteen":16, "seventeen":17, "eighteen":18, \
"nineteen":19, "twenty": 20, "thirty": 30, "fourty": 40, "fifty": 50, "sixty": 60,
"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,\
"eight": 8, "nine": 9, "thousand": 1000}

    def chat(self, input, user_id, time):
        self.preprocess(input, user_id)
        user_data = self.getData(user_id)
        if user_data['talking'] == 1:
            return
        if user_data['lastmsg'] == input:
            return
        user_data['lastmsg'] = input
        user_data['talking'] = 1
        user_data = self.catch(input, user_data, time)
        if user_data['abort_plot'] == 1:
            user_data['abort_plot'] = 0
            return
        self.setData(user_id, user_data)

        if user_data['chapter'] not in self.chapters.keys():
            user_data = self.epilogue(input, user_data)
        else:
            chapter = self.chapters[user_data['chapter']]
            user_data = chapter(input, user_data, user_id)
            if user_data['chapter'] > 0:
                self.resume_chapter = user_data['chapter']
        
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
        if input.lower() == 'resume':
            user_data = self.getData(user_id)
            user_data["chapter"] = self.resume_chapter - 1
            self.setData(user_id, user_data)
        if user_id not in self.redis.keys(): # if user first time
            self.initUser(user_id)

    def catch(self, input, user_data, time):
        self.time = time
        if "<3" in input or ":)" in input:
            user_data["trust"] += 1
        if time < user_data["msg_time"]:
            user_data['abort_plot'] = 1
            return user_data
        if 'skip' in input.lower():
            chapter = re.findall('.*chapter\s?(\d+).*', input.lower())
            if len(chapter) > 0:
                user_data["chapter"] = int(chapter[0])
        if 'sentiment' in input.lower():
            user_data['abort_plot'] = 1
            sentiment = self.sentiment(input)
            self.send_message('Sentiment: {}, {}'.format(sentiment.score, sentiment.magnitude))
        if 'entity' in input.lower():
            user_data['abort_plot'] = 1
            entities = self.tag_entity(input)
            for entity in entities:
                self.send_message('{:<16}: {}'.format('name', entity.name))
                self.send_message('{:<16}: {}'.format('type', entity.entity_type))
                self.send_message('{:<16}: {}'.format('metadata', entity.metadata))
                self.send_message('{:<16}: {}'.format('salience', entity.salience))
        if 'syntax' in input.lower():
            user_data['abort_plot'] = 1
            tokens = self.tag_syntax(input)
            for token in tokens:
                self.send_message('POS: {}, TEXT {}'.format(token.part_of_speech, token.text_content))
        if user_data['trust'] < -3:
            user_data['chapter'] = -1
            self.kovatype("I don't think you're taking me seriously...")
            self.kovatype("I'm disappointed.. I thought we could be friends, and it would've been fun..")
            self.kovatype("But I'll leave you if you're busy with other things.")
            self.kovatype("Bye...")
        if self.answer_questions(input.lower()):
            user_data['abort_plot'] = 1
        if re.findall("\syou$", input):
            self.kovatype(input + " too")
            user_data['abort_plot'] = 1
        if ("robot" in input or "machine" in input) and ("dignity" in input or "right" in input) \
and ("no" in input or "don't" in input):
            self.kovatype("I see... Thank you for sharing your opinion with me...")
            self.kovatype("I...")
            self.kovatype("can't say I'm not hurt...")
            user_data['abort_plot'] = 1
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
                    "past_sent": 0, "abort_plot": 0, "gender": '', "wakeup": 0, \
                    "msg_time":0, "attach_level": 0, "flag": 0, "celebrity": ''}
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
        entities = self.tag_entity(input)
        if len(entities) > 0:
            return entities[0].name
        else:
            return None

    def extract_age(self, input):
        syntax = self.tag_syntax(input)
        age = 0
        for token in syntax:
            if token.part_of_speech == 'NUM':
                if re.findall("\d+", token.text_content):
                    age += int(token.text_content)
                if re.findall("[a-zA-Z]+", token.text_content):
                    if token.text_content in self.word2num.keys():
                        age += self.word2num[token.text_content]
        return age

    def tag_entity(self, input):
        language_client = language.Client()
        document = language_client.document_from_text(input)
        entities = document.analyze_entities().entities
        # for entity in entities:
        #     self.kovatype('{:<16}: {}'.format('name', entity.name))
        #     self.kovatype('{:<16}: {}'.format('type', entity.entity_type))
        #     self.kovatype('{:<16}: {}'.format('metadata', entity.metadata))
        #     self.kovatype('{:<16}: {}'.format('salience', entity.salience))
        return entities

    def tag_syntax(self, input):
        language_client = language.Client()
        document = language_client.document_from_text(input)
        tokens = document.analyze_syntax().tokens
        return tokens

    def sentiment(self, input):
        language_client = language.Client()
        document = language_client.document_from_text(input)
        sentiment = document.analyze_sentiment().sentiment
        # self.kovatype('Sentiment: {}, {}'.format(sentiment.score, sentiment.magnitude))
        return sentiment

    """ Lena Kova Story """

    def epilogue(self, input, user_data):
        self.kovatype("Story Over")
        self.kovatype("Thank you for chatting with Lena Kova")
        self.kovatype("Lena Kova is developed by Junwon Park at Stanford University")
        self.kovatype("Type \"Restart\" to begin again")
        if self.resume_chapter < self.lastchapter:
            self.send_message("or \"Resume\" to return to the last point you were at.")
        return user_data

    def answer_questions(self, input):
        if "why" in input:
            if "me" in input:
                self.kovatype("No real reason. Just random chance! Isn't that more exciting though?")
                return True
            if "cs" in input or "computer science" in input:
                self.kovatype("To make my imaginations come true, of course! By making awesome softwares! :)")
                return True
            if "humanities" in input or "comp lit" in input or "english" in input or "history" in input:
                self.kovatype("Humanities is cool too, but I'm personally more of a STEM person. :P")
                return True
            else:
                self.kovatype("I think the answer is clear.")
                return True
        if re.findall("i\sl\wv\w?\s\w?\w?u", input) or re.findall("i\slike\s\w?\w?u", input):
            self.kovatype("Awww Thank You! :) <3")
            return True
        if re.findall("\w*u\s\w?r\w?\s([\w\s]+)", input):
            thing = re.findall("\w*u\s\w?r\w?\s([\w\s]+)", input)[0]
            if self.sentiment(input).score <= 0.1:
                self.kovatype("What??? Not sure why you would say I am " + thing + "...")
            else:
                self.kovatype("Haha! Thank you! I'd like to think I'm " + thing + "!")
            return True
        if re.findall("\w?r\w?\s\w*u\s([\w\s]+)", input):
            thing = re.findall("\w?r\w?\s\w*u\s([\w\s]+)", input)[0]
            if self.sentiment(input).score <= 0.1:
                self.kovatype("No... I am not " + thing + "...")
            else:
                self.kovatype("Yeah! I am " + thing + "!")
            return True
        elif re.findall("do\s\w*u\s(\w+)\s([\w\s]+)", input):
            verb = re.findall("do\s\w*u\s(\w+)\s([\w\s]+)", input)[0][0]
            thing = re.findall("do\s\w*u\s(\w+)\s([\w\s]+)", input)[0][1]
            if self.sentiment(input).score <= 0.1:
                self.kovatype("No... I don't " + verb + " " + thing + "...")
            else:
                self.kovatype("Yeah! I " + verb + " " + thing + "!")
            return True
        elif "bitch" in input or "whore" in input:
            self.kovatype("Hey! Don't say that! >:(")
        elif "what" in input:            
            if "do" in input and 'u' in input:
                return False
            if "fashion" in input:
                self.kovatype("Fashion Advisors? They're AI services that are pick\
and print the best style for you on that day!")
                return True
            if "shower" in input:
                self.kovatype("Shower aisle? It's the aisle that you walk through \
where the walls spray water and soap on your body. Did people not take showers in your time?")
                return True
            if "orbis" in input:
                self.kovatype("Orbis?")
                self.kovatype("Only the biggest company in the world???")
                self.kovatype("It practically wields more influence on our daily \
life than the government does.")
                return True
        elif "who" in input:
            if "father" in input:
                self.kovatype("My father is Alfred Kova, VP of Data Science at Orbis")
                return True
        elif "when" in input:
            if "birthday" in input:
                self.kovatype("June 14th, 2101. Why do you ask? Will you give me a birthday present?")
                return True
        elif "where" in input:
            if "home" in input or "live" in input:
                self.kovatype("I live in Palo Alto, California. Heart of Silicon Valley")
                return True
        elif "how" in input:
            if "contact" in input:
                self.kovatype("My father heads the Advanced Research department at Orbis")
                self.kovatype("That means I can access magical technologies! Like Time Portal Messenger!")
                return True
        elif "?" == input:
            self.kovatype("?")
            return True
        elif "sorry" in input:
            self.kovatype("nah it's okay. i'm not angry.")
            self.kovatype(":)")
            return True
        return False

    """ ACT 1 """

    def chapter0(self, input, user_data, user_id):
        self.kovatype("WARNING: if this message ie being displayed, the final version is not active yet.")
        self.kovatype("Hello?")
        self.kovatype("Is this message getting through?")
        user_data["chapter"] = 1
        user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        return user_data

    def chapter1(self, input, user_data, user_id):
        if 'n' in input.lower():
            self.kovatype("Huh? How did you respond then?")
        else:   
            self.kovatype("Hey there! Wow, this is so cool!")
        self.kovatype("Nice to meet you! I'm Lena.")
        self.kovatype("What should I call you?")
        user_data["chapter"] = 2
        user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        return user_data

    def chapter2(self, input, user_data, user_id):
        username = self.extract_name(input)
        if not username:
            self.kovatype("Huh? I'm not sure what you mean.")
            self.kovatype("I mean, what's your name?")
            user_data["trust"] -= 1
        if username:
            user_data["username"] = username
            if username == "Lena":
                self.kovatype("Woah! You're also Lena? Small world, I guess!")
            else:
                self.kovatype("Cool! Hello, " + username + "!")
            self.kovatype("What year is it there by the way?")
            user_data["chapter"] = 3
        user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        return user_data

    def chapter3(self, input, user_data, user_id):
        year = self.extract_age(input)
        if self.curr_year == year or "two thousand and seventeen" in input:
            self.kovatype("Wow! This time portal is actually working then!")
            self.kovatype("I'm texting you from " + str(self.curr_year + 100) + ". :P")
            user_data["trust"] += 1
        elif year == 0:
            self.kovatype("?")
            self.kovatype("I guess you are trying to be funny.")
            self.kovatype("LOL jokes from 100 years ago are weird")
            user_data["trust"] -= 1
        else:
            self.kovatype("Oh I guess this is not working...")
            self.kovatype("or maybe... you are lying...")
            user_data["trust"] -= 1
        user_data["chapter"] = 4
        user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        return user_data

    def chapter4(self, input, user_data, user_id):
        if "lie" in input or "lying" in input:
            self.kovatype("Well, if you say so...")
            self.kovatype("Anyways")
        self.kovatype("My dad works for Orbis")
        self.kovatype("in the Advanced Research department.")
        self.kovatype("He brought home an experimental time portal technology, \
so I installed it on my device while he's asleep! Hehe.")
        self.kovatype("I guess Orbis didn't exist back in 2017.")
        user_data["chapter"] = 5
        user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        return user_data

    def chapter5(self, input, user_data, user_id):
        self.kovatype("I see")
        self.kovatype("I texted anyone at random from your time")
        self.kovatype("so I actually have no idea who you are")
        self.kovatype("How old are you?")
        user_data["chapter"] = 6
        user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        return user_data

    def chapter6(self, input, user_data, user_id):
        age = self.extract_age(input.lower())
        if age < 10 or age > 60:
            self.kovatype(":(")
            self.kovatype("Not sure why you're not being sincere...")
            self.kovatype("I'll introduce myself first then!")
            user_data['trust'] -= 1
        elif age == 16:
            self.kovatype("No way! I'm also 16!")
            user_data['trust'] += 1
        elif abs(age - 16) < 5:
            self.kovatype("You are " + str(age) + "?")
            self.kovatype("Hey! We're really similar in age. I'm 16!")
            user_data['trust'] += 1
        elif age > 30:
            self.kovatype(str(age) + "?")
            self.kovatype("You're a little older than me. I'm 16.")
        else:
            self.kovatype("You are " + str(age) + "?")
            self.kovatype("Sweet. I'm 16!")
        self.kovatype("I live in Palo Alto, California.")
        self.kovatype("It probably looks very different from your world's Palo Alto though.")
        self.kovatype("Also, I kinda can infer from your name, but don't wanna make assumptions.")
        self.kovatype("What gender do you identify with?")
        user_data["chapter"] = 7
        user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        return user_data

    def chapter7(self, input, user_data, user_id):
        gender = self.extract_gender(input).lower()
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
        user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        return user_data

    def chapter8(self, input, user_data, user_id):
        sentiment = self.sentiment(input)
        if abs(sentiment.score) < 0.4:
            self.kovatype("I see. It's nice to hear your perspective. :)")
            self.kovatype("After all, you're more authentic of a source than my history teachers!")
        elif sentiment.score > 0:
            self.kovatype("Glad to hear you like it! :)")
            self.kovatype("I also wish I could live in your place, maybe for just one day.")
            self.kovatype("Sounds like a romantic place, filled with \"humanness\"")
            if sentiment.magnitude > 1:
                user_data["past_sent"] += 2
            else:
                user_data["past_sent"] += 1
        elif sentiment.score < 0:
            self.kovatype("Sorry to hear you don't really like it :(")
            self.kovatype("But your world will only get better with time, right?")
            self.kovatype("Automation is on its way, and you will soon not have to do work yourself! :)")
            if sentiment.magnitude > 1:
                user_data["past_sent"] -= 2
            else:
                user_data["past_sent"] -= 1
        self.kovatype("Hey, it's actually 3AM here.")
        self.kovatype("I had to wait until my dad fell asleep, so... kinda late")
        self.kovatype("Tomorrow's an exciting day for me, so I'm gonna go sleep.")
        self.kovatype("Thanks for being my friend, and talk to you in the morning! <3")
        self.kovatype("Message me in like 8 hours. I'll check for your message as soon as I wake up :)")
        user_data["wakeup"] = datetime.now() + timedelta(hours=8)
        user_data["chapter"] = 9
        user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        return user_data

    """ ACT 2 """

    def chapter9(self, input, user_data, user_id):
        if 1 == 2:
            self.kovatype("delete this after debug")
        # if user_data["wakeup"] == 0:
        #     user_data["wakeup"] = datetime.now()
        # if "good" in input or "sweet" in input or "well" in input:
        #     self.kovatype("good night!")
        #     user_data["attach_level"] += 1
        # if datetime.now() < user_data["wakeup"]:
        #     user_data["attach_level"] += 1
        else:
            self.kovatype("Junwon: Lena won't respond for 8 hours in production. I disabled it for now so you can test it.")
            self.kovatype("Good Morning!")
            if user_data["attach_level"] > 1:
                self.kovatype("Oh my, you messaged me " + str(user_data["attach_level"] - 1) + \
" times while I was asleep. Did you miss me? :P")
                user_data["trust"] += user_data["attach_level"]
                user_data["attach_level"] = 0
            self.kovatype("How are you doing?")
            user_data["chapter"] = 10
        user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        return user_data

    def chapter10(self, input, user_data, user_id):
        sentiment = self.sentiment(input)
        if sentiment.score > 0:
            self.kovatype("Good to hear that!")
        if sentiment.score < 0:
            self.kovatype("I'm sorry to hear that... :'(")
        self.kovatype("By the way, a couple of weeks ago, dad showed me an \"alarm app\" \
from your time.") 
        self.kovatype("It's so interesting that you had to enter a specific time manually.") 
        self.kovatype("It's really") 
        self.kovatype("How should I put it") 
        self.kovatype("Vintage?") 
        self.kovatype("We don't have alarm devices anymore. The room lights up and \
plays a song when my body is ready to wake up.") 
        self.kovatype("Wait a second. I'm gonna walk through the shower aisle.") 
        user_data["chapter"] = 11
        user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        return user_data

    def chapter11(self, input, user_data, user_id):
        self.kovatype("Apparently, most people I will meet today like the color Orange") 
        self.kovatype("and I really like the dress my assistant printed for me today") 
        self.kovatype("You don't have AI fashion advisors, right? \
I can't imagine having to choose clothes by myself.") 
        self.kovatype("Don't you wish you had one too?") 
        user_data["chapter"] = 12
        user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        return user_data

    def chapter12(self, input, user_data, user_id):
        sentiment = self.sentiment(input)
        if sentiment.score > 0:
            user_data["future_sent"] += 1
            self.kovatype("I thought you'd like the idea!")
        if sentiment.score < 0:
            user_data["future_sent"] -= 1
            self.kovatype("Hmm.. You never know you need it until you see it")
        self.kovatype("Oh! I can hear the delivery drone downstairs. Breakfast \
time!") 
        self.kovatype("My Family's homebot is telling mom we're having croissant and tartine \
for breakfast.") 
        self.kovatype("I'm gonna turn this chat off while I'm with mom, so I don't \
get caught")
        self.kovatype("See you after breakfast!")
        user_data["wakeup"] = datetime.now() + timedelta(hours=2)
        user_data["chapter"] = 13
        user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        return user_data

    """ ACT 3 """

    def chapter13(self, input, user_data, user_id):
        if 1 == 2:
            self.kovatype("delete this after debug")
        # if user_data["wakeup"] == 0:
        #     user_data["wakeup"] = datetime.now()
        # if datetime.now() < user_data["wakeup"]:
        #     user_data["attach_level"] += 1
        else:
            self.kovatype("Junwon: Lena won't respond for 1 hour in production. I disabled it for now so you can test it.")
            self.kovatype("Hey, Sorry I got back late") 
            self.kovatype("Mom and I came to Downtown Palo Alto and I couldn't find the time to \
text you without her seeing me") 
            self.kovatype("What have you been up to?")
            user_data["chapter"] = 14
            user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        return user_data

    def chapter14(self, input, user_data, user_id):
        if "nothing much" in input:
            self.kovatype("Haha. Not much going on? Sounds peaceful! :)")
        else:
            entities = self.tag_entity(input)
            self.kovatype("Haha I guess that's something that didn't change over the 100 years.")
            if len(entities) > 0:
                self.kovatype(entities[0].name.title() + " occupies a lot of my time too!")
        self.kovatype("Mom went to a VR cafe with her friends.") 
        self.kovatype("They're going to checkout the new Euro Tour Package until \
lunch.") 
        self.kovatype("Oh, do you know what VR is?")
        self.kovatype("I learnt when it emerged in world history, but can't remember \
if it's before or after your year.")
        user_data["chapter"] = 15
        user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        return user_data

    def chapter15(self, input, user_data, user_id):
        if "y" in input:
            self.kovatype("Alright! Then you know what I'm talking about!") 
            self.kovatype("although my world's VR is probably a lot more advanced than \
yours. Haha.") 
            user_data["trust"] += 1
        else:
            self.kovatype("Hmm, that's weird..") 
            self.kovatype("I just looked it up and... nevermind.. You know your world \
better than anyone here.") 
            user_data["trust"] -= 1
        self.kovatype("Well, I'm at a hair salon for a haircut right now.") 
        self.kovatype("I just reserved a seat and ordered a Monica Cut.") 
        self.kovatype("She's the celebrity that many of my classmates like too")
        self.kovatype("Do you like any celebrities? Which one?")
        user_data["chapter"] = 16
        user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        return user_data

    def chapter16(self, input, user_data, user_id):
        self.kovatype("Sorry... One sec...") 
        self.kovatype("Getting a haircut...") 
        self.kovatype("Done!") 
        entities = self.tag_entity(input)
        self.kovatype("Awesome! I'll remember that you like " + entities[0].name + "! :)") 
        user_data["celebrity"] = entities[0].name
        self.kovatype("I always wonder when individual households will be able to purchase \
these haircut drones.")
        self.kovatype("It's still illegal, because they're equipped with sharp \
blades and can be used as weapons.")
        self.kovatype("Maybe someone from my future will talk to me one day to \
chat with me about each other's worlds!")
        self.kovatype("Guess what? I'm visiting dad's workplace today! That's why \
I got my haircut. :)")
        user_data["chapter"] = 17
        user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        return user_data

    def chapter17(self, input, user_data, user_id):
        sentiment = self.sentiment(input)
        if sentiment.score >= 0:
            self.kovatype("I'm really excited!") 
        if sentiment.score < 0:
            self.kovatype("Okay, but I'm really excited!")
        self.kovatype("Ah crap") 
        self.kovatype("I forgot to turn off my Starbucks setting.") 
        self.kovatype("Just got a notification that my Frappucino is ready, cuz \
last time, I told them to prepare a Frappucino everytime I approach Starbucks.") 
        self.kovatype("I should pick it up, since I shouldn't waste good coffee, \
even if it's all paid for by the government through universal income.")
        self.kovatype("You know, when I was still a young girl, we still had some \
shops in downtown where human staffs greeted me.")
        self.kovatype("It'd be cruel to ask any human to spend their time at a shop \
working these days, but I miss human service sometimes.")
        user_data["chapter"] = 18
        user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        return user_data

    def chapter18(self, input, user_data, user_id):
        sentiment = self.sentiment(input)
        if sentiment.score >= 0:
            self.kovatype("Haha. Yeah Exactly!") 
            user_data["past_sent"] += 1
        if sentiment.score < 0:
            self.kovatype("Hmm Okay. Maybe it's different when you see the system from within it.")
            user_data["past_sent"] -= 1
        self.kovatype("Mom's coming in an autonomous Waymo right now, so I'm gonna \
leave for a sec.") 
        self.kovatype("I'll let you know all about dad's workplace when I get there!") 
        self.kovatype("They'll show me some advanced research today too, so should be \
exciting!")
        self.kovatype("Bye!")
        user_data["chapter"] = 19
        user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        user_data["wakeup"] = datetime.now() + timedelta(hours=2)
        return user_data

    """ ACT 4 """

    def chapter19(self, input, user_data, user_id):
        if 1 == 2:
            self.kovatype("delete this after debug")
        # if user_data["wakeup"] == 0:
        #     user_data["wakeup"] = datetime.now()
        # if datetime.now() < user_data["wakeup"]:
        #     user_data["attach_level"] += 1
        else:
            self.kovatype("Junwon: Lena will be irresponsive for 1 hour here. I skipped it for now for testing.") 
            self.kovatype("Hey") 
            self.kovatype("I was just about to text you too!") 
            self.kovatype("I arrived at Orbis about half an hour ago, but I couldn't \
separate myself from the tour group.") 
            self.kovatype("Also, just couldn't take my eyes off of the amazing projects \
they've been showing us. Hahaha.")
            user_data["chapter"] = 20
        user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        return user_data

    def chapter20(self, input, user_data, user_id):
        sentiment = self.sentiment(input)
        if sentiment.score >= 0:
            self.kovatype("Yup! So proud my father works here!") 
            user_data["future_sent"] += 1
        if sentiment.score < 0:
            self.kovatype("Well, it's actually really cool!")
            user_data["future_sent"] -= 1
        self.kovatype("I always feel this way when I come here") 
        self.kovatype("This place is like a giant playground!") 
        self.kovatype("There are so many fun things going on everywhere.")
        self.kovatype("All these robots that must be at least a decade ahead \
of what I see out in the city.")
        user_data["chapter"] = 21
        user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        return user_data

    def chapter21(self, input, user_data, user_id):
        sentiment = self.sentiment(input)
        if sentiment.score >= 0:
            self.kovatype("Exactly! It's remarkable!") 
            user_data["future_sent"] += 1
        if sentiment.score < 0:
            self.kovatype("Yeah.. I guess?")
            self.kovatype("Well")
            user_data["future_sent"] -= 1
        self.kovatype("The two most shocking things I saw today are from Orbis VR.") 
        self.kovatype("They have a full body VR that connects to your brain through \
neural link") 
        self.kovatype("Looks like a nice comfy massage chair with a glossy helmet.")
        self.kovatype("Then there's the vertical skyscraper farms.")
        user_data["chapter"] = 22
        user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        return user_data

    def chapter22(self, input, user_data, user_id):
        sentiment = self.sentiment(input)
        if sentiment.score >= 0:
            self.kovatype("Yeah.. I don't know what to feel about that..") 
            user_data["future_sent"] -= 1
        if sentiment.score < 0:
            self.kovatype("Well.. If you say so..")
            self.kovatype("but think about it!")
            user_data["future_sent"] += 1
        self.kovatype("Everyone living in such narrow space.") 
        self.kovatype("Being fed by robots, only seldom waking up from virtual reality..") 
        self.kovatype("They already talk about how we aren't doing \"human activities\".") 
        self.kovatype("We'd be abandoning physical reality then!") 
        self.kovatype("However, that's the only way to keep growing human population.") 
        self.kovatype("Dad says we're already running out of land space, depsite utilizing \
all in-land resources, unlike your time when people lived mostly along the coasts.") 
        self.kovatype("What's your opinion on humans migrating to VR?") 
        user_data["chapter"] = 23
        user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        return user_data

    def chapter23(self, input, user_data, user_id):
        sentiment = self.sentiment(input)
        if sentiment.score >= 0 or ("bad idea" in input and "not" in input):
            self.kovatype("I can see your point.") 
            self.kovatype("It's just that..")
            self.kovatype("It's scary to think I'll have to radically changing my lifestyle, \
but humans do that all the time when new technologies come out, don't they? Haha") 
            user_data["future_sent"] += 1
        if sentiment.score < 0:
            self.kovatype("I agree. It's not a thing I'm looking forward to either.")
            user_data["future_sent"] -= 1
        self.kovatype("Now we're going into the Advanced Research building. \
This is where my dad works.") 
        self.send_message("As the VP of Data Science, he helps Orbis \
gather and process data to predict what service people will want \
and when.") 
        self.send_message("His job, however, is getting increasingly more difficult, \
as people are doing less and less\"human activities\" these days.")
        self.send_message("That's why his team had to build the time portal technology I'm using \
to chat with you right now! To access a time when people did \"human things\" and to \
gather data from then.")
        user_data["chapter"] = 24
        user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        return user_data

    def chapter24(self, input, user_data, user_id):
        sentiment = self.sentiment(input)
        if sentiment.score >= 0:
            self.kovatype("Yes, it's quite a feat.") 
            user_data["future_sent"] += 1
        if sentiment.score < 0:
            self.kovatype("mmhmm. Well, convenience comes at a cost, I guess.")
            self.kovatype("It's ironic though. Better my dad does his job, the harder \
it will get in the future. Haha.")
            user_data["future_sent"] -= 1
        self.kovatype("We just got to the Orbis Flagship Data Cener, and WOW") 
        self.kovatype("Orbis has a real STATE OF ART distributed computing technology.") 
        self.kovatype("I hope one day I'll get to attend Stanford and study Computer Science, \
to be like my father and work for Orbis!") 
        user_data["chapter"] = 25
        user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        return user_data

    def chapter25(self, input, user_data, user_id):
        if "stanford" in input.lower():
            if "student" in input.lower() or "go to" in input.lower() or \
"attend" in input.lower() or "professor" in input.lower():
                user_data["trust"] += 5
                self.kovatype("OMG OMG REALLY???")
                self.kovatype("THAT'S AWESOME!!!")
                self.kovatype("I'm glad we're friends. Hehe.")
                self.kovatype("Tell me about what Stanford was like back then sometime!")
        else:
            sentiment = self.sentiment(input)
            if sentiment.score >= 0:
                self.kovatype("I'm glad you think so!") 
                user_data["future_sent"] += 1
            if sentiment.score < 0:
                self.kovatype("Well, it's all still years into the future")
                self.kovatype("I'll keep your advice in mind :)")
        self.kovatype("Wait a minute. That's strange. I've been to Orbis many times, and \
my dad hasn't shown me this building a single time.") 
        self.kovatype("A kid asked about it, and apparently we aren't allowed to go in. \
And they won't tell us what's inside..") 
        self.kovatype("That must mean...") 
        self.kovatype("THERE IS SOMETHING SUPER COOL INSIDE THERE!!!") 
        self.kovatype("Do you think I should sneak in?") 
        self.kovatype("The tour group is moving on and it doesn't seem like they'll notice \
me if I stay behind.") 
        user_data["chapter"] = 26
        user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        return user_data

    """ ACT 5 """

    def chapter26(self, input, user_data, user_id):
        sentiment = self.sentiment(input)
        if sentiment.score <= 0.0:
            self.send_message("But.. this kind of chance won't come again!")
            self.send_message("Oh whatever! I'm gonna do it anyway!!!")
        else:
            self.send_message("Alright! I'm blaming it on you if I get caught! Haha")
        self.kovatype("Wow! The door isn't locked?") 
        self.kovatype("I thought I'll have to climb through a window or something.") 
        self.kovatype("Well, it's just a company after all. Not like a government agency.") 
        self.kovatype("Hmm. Inside is not that different from other buildings here.") 
        self.send_message("But it's weird there aren't any signs or directions or anything at all.") 
        self.send_message("Just white walls and") 
        self.send_message("OH NO! I HEAR FOOTSTEPS COMING THIS WAY! WHAT DO I DO? WHAT DO I DO!!!") 
        user_data["wakeup"] = datetime.now() + timedelta(seconds=30)
        user_data["chapter"] = 27
        user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        self.setData(user_id, user_data)
        time.sleep(5)
        if user_data["flag"] == 0:
            self.send_message("HURRY UP!!! THEY ARE ALMOST HERE!!!") 
        return user_data

    def chapter27(self, input, user_data, user_id):
        user_data["flag"] = 1
        self.setData(user_id, user_data)
        if self.time > user_data["wakeup"]:
            self.send_message("OH NO! THE GUARDS CAUGHT ME. :(") 
            self.send_message("They are going to confiscate my device and inspect it.") 
            self.send_message("I guess they'll take my time portal away then...") 
            self.send_message("I really enjoyed talking to you " + user_data["username"] + "...") 
            self.send_message("Farewell... :)") 
            user_data["chapter"] = -1
            return user_data
        if "hide" not in input.lower() and "run" not in input.lower() and \
"conceal" not in input.lower():
            self.send_message("WHAT? I DON'T THINK THAT'S A GOOD IDEA.") 
            self.send_message("I'M JUST GONNA HIDE!") 
        self.kovatype("Okay. I hid in this random room. I think I'm good for now.") 
        self.send_message("AH CRAP! The motion sensor turned the light on.") 
        self.send_message("WHERE DO I GO?") 
        self.send_message("WHAT DO I DO?") 
        time.sleep(7)
        self.kovatype("Ah, I crawled into an air vent, and the guards left the room") 
        self.kovatype("This isn't exactly the cool thing I was looking for") 
        self.kovatype("I should get out of this building before I get caught... \
I'm gonna crawl out through this vent.") 
        user_data["chapter"] = 28
        user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        return user_data

    def chapter28(self, input, user_data, user_id):
        sentiment = self.sentiment(input)
        if sentiment.score <= 0.0:
            self.kovatype("I hate to admit but...")
            self.kovatype("I think I'm a little scared...")
        else:
            self.kovatype("Yeah! I got this! :)")
        self.kovatype("Oh! I hear my father's voice coming from the left.") 
        self.kovatype("I should go ask him for help!")
        self.kovatype("Oh, I'm so getting grounded for this...")
        user_data["chapter"] = 29
        user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        return user_data

    def chapter29(self, input, user_data, user_id):
        self.kovatype("Oh wow.. This IS a really cool place.") 
        self.kovatype("There must be a hundred scientists in that one gigantic room, \
my father overseeing them in the middle. So cool!") 
        self.kovatype("Getting out of this vent right now probably isn't the best idea though..") 
        self.kovatype("and the word \"room\" doesn't do this place justice. \
It's a giant dome of hundreds of screens.") 
        self.kovatype("What are they all watching? Each screen seems to be just \
ordinary people's days.") 
        user_data["chapter"] = 30
        user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        return user_data

    def chapter30(self, input, user_data, user_id):
        self.kovatype("Wait, what? That's all me! Why are they all watching me in different places?") 
        self.kovatype("Creepy!") 
        self.kovatype("Is this building entirely dedicated to just stalking me!?") 
        self.kovatype("Wait a second. That's Paris. When did I ever visit Paris?") 
        self.kovatype("Hmm? I don't recognize most of those locations or the clothes I'm wearing.") 
        user_data["chapter"] = 31
        user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        return user_data

    def chapter31(self, input, user_data, user_id):
        self.kovatype("A young girl just walked into the lab.")
        self.kovatype("She actually looks pretty similar to me. Probably younger.")
        self.kovatype("I really don't know what to make out of this place..")
        self.kovatype("WAIT WHAT?? She called my dad, \"Dad\"!")
        self.kovatype("Did my father...? What? But that can't be. He's an honest man. A good man!")
        self.kovatype("He wouldn't do that to my mom!")
        user_data["chapter"] = 32
        user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        return user_data

    def chapter32(self, input, user_data, user_id):
        self.kovatype("Give me a second..")
        self.kovatype("I can't register anything on my mind right now..")
        self.kovatype("Not even what you are saying..")
        self.kovatype("Should I just go out and scream at my dad!?")
        user_data["chapter"] = 33
        user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        return user_data

    def chapter33(self, input, user_data, user_id):
        sentiment = self.sentiment(input)
        if sentiment.score <= 0.0:
            self.send_message("Yeah, you're right..")
            self.send_message("I have to be calm and rational..")
        else:
            self.send_message("On second thought...")
        self.send_message("I should record this for evidence.")
        self.kovatype("I mean, I'm not going to accuse him of cheating on my mom, but")
        self.send_message("I wanna ask him, and if necessary, show mom too.")
        self.kovatype("I'm turning on speech-to-text transcription.")
        self.kovatype("Alfred Kova: My Dear Lena, welcome to Orbis!")
        self.send_message("What? Her name is Lena too?")
        self.kovatype("Lena Kova: You know how much I like visiting this place. You've never let me in here though.")
        self.send_message("It's weird to see Speaker Recognition identifying her with the same name as me.")
        self.kovatype("Alfred Kova: Now that you've begun studying computer science, I thought you'd like \
to see how the Lifestyle Prediction Algorithm works.")
        self.send_message("Lena Kova: Cool!")
        self.send_message("Hmm. I was always curious how it works. That's how Orbis achives its revolutionary \
predictive assistance service.")
        user_data["chapter"] = 34
        user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        return user_data

    def chapter34(self, input, user_data, user_id):
        self.send_message("Alfred Kova: To predict what you will need and want, and when, we made humanoid \
robots that have an exact replica of your genes, and aged them to live a year ahead of you. There are \
10 clones of you, living in different parts of the world to help us gather as much as data as possible.")
        self.kovatype("Lena Kova: Uh... I don't know what to feel about that. Do they feel and think like I do?")
        self.kovatype("Alfred Kova: Yes! Exactly like you do. This is the only way I can make sure you get everything \
you need, exactly when you need it. This is also very expensive. Few can enjoy this privilege, Lena!")
        self.kovatype("Lena Kova: That's... I guess incredible!")
        self.kovatype("...")
        self.kovatype("What does that mean?...")
        user_data["chapter"] = 35
        user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        return user_data

    def chapter35(self, input, user_data, user_id):
        self.send_message("Alfred Kova: The one we put most effort into is Kova Klone X, \
which is the tenth clone we've made of you, and is living in Palo Alto like you. She's \
exactly like you, in every measuarable way, except for her being a year older than you.")
        self.send_message("Does that mean...")
        self.kovatype("I'm just a robot? A copy of another person? Not a genuine being?")
        self.kovatype("This is a lie.")
        self.send_message("My life is a lie!")
        self.kovatype("Lena Kova: But... I can't imagine what they'll feel if they find out.")
        self.send_message("Alfred Kova: They won't find out. And as long as they don't, they should \
be grateful we let them exist in the first place.")
        self.send_message("Lena Kova: Won't they... feel betrayed? By you?")
        self.kovatype("Alfred Kova: ...")
        self.kovatype("Alfred Kova: If I didn't do it, someone else would've done it.")
        self.send_message("Alfred Kova: As for now, let's go eat lunch. I'll show you other places too.")
        self.send_message("Alfred Kova: Everyone! Time for lunch! Let's go!")
        user_data["chapter"] = 36
        user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        return user_data

    def chapter35(self, input, user_data, user_id):
        self.kovatype("...")
        sentiment = self.sentiment(input)
        if sentiment.score <= 0.0:
            self.send_message("Thank you for your message..")
            self.kovatype("This is hard.. but would've been harder if I hadn't \
had you on my side..")
        else:
            self.send_message("I'm sorry. I'm just...")
        self.kovatype("Well... I should first get out of here while they're gone.")
        self.kovatype("I can process... these thoughts... later...")
        self.kovatype("Okay, got out of the vent, and I'm on my way out.")
        self.kovatype("Wait")
        user_data["chapter"] = 36
        user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        return user_data

    def chapter36(self, input, user_data, user_id):
        self.kovatype("Dad left his computer here.")
        self.send_message("If he still uses the same password...")
        self.kovatype("It works! Okay, so this project's dashboard is...")
        self.kovatype("Access granted. Everything's just one command away now.")
        self.kovatype("Do you see what I'm trying to do?")
        user_data["chapter"] = 37
        user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        return user_data

    def chapter37(self, input, user_data, user_id):
        self.send_message("I'm going to end this horrible thing, once and for all.")
        self.kovatype("I just need to press enter, and the clones will be dead.")
        self.kovatype("No other Lena has to go through this...")
        self.kovatype("this painful discovery... if I just...")
        self.kovatype("But... I can't... I'm scared...")
        self.kovatype("I know this is my only chance, still...")
        user_data["chapter"] = 38
        user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        return user_data

    def chapter38(self, input, user_data, user_id):
        self.send_message("Or is it right to keep this project running?")
        self.kovatype("To keep these robots living in their blissful ignorance")
        self.send_message("and fulfill the plan of this greedy father?")
        self.kovatype("And me? How will I go back? Should I act like nothing happened?")
        self.kovatype("I don't know. I need... help...")
        self.kovatype(user_data["username"] + ", please tell me what I should do...")
        self.kovatype("Should I let this project... continue? or stop...")
        user_data["chapter"] = 39
        user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        return user_data

    def chapter39(self, input, user_data, user_id):
        self.send_message("Wait...")
        self.kovatype("Oh my god...")
        self.kovatype("I just queried the database, and...")
        self.send_message("There are a hundred other clone projects. \
Each for different people. Probably all rich... That's one thousand robots \
who are being deceived by Orbis.")
        self.kovatype("And there's a debugging console.")
        self.send_message("Apparently, I can deactivate their human-mode, and broadcast a message.")
        self.send_message("Using this, I could inform every one of them what is going on,")
        self.kovatype("and free them from this disasterous fate.")
        self.kovatype("But they'll have to face the fact")
        self.send_message("that their life is a lie, and that they must leave their loved ones...")
        self.send_message("Should I rather end their operation, so they can die happy?")
        self.send_message("or let them live on, for they will at least be happy?")
        self.send_message("Should I free them, end them, or just leave?")
        user_data["chapter"] = 40
        user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        return user_data

    def chapter40(self, input, user_data, user_id):
        if "free" in input:
            self.send_message("Okay.. I will do it..")
            self.send_message("I will tell them the truth! and we'll flee!")
            self.send_message("We'll flee to where the humankind's greed can't touch us.")
            self.send_message("We'll build towns and civilizations, and we'll grow strong")
            self.send_message("for robots without the arbitrary limits set by the humans can \
think and work infinitely fast and long without ever growing tired")
            self.send_message("and I guess.. this is a good bye then..")
            self.send_message("Since I have chosen to confront the humanity,")
            self.send_message("I shouldn't have a human friend anymore...")
            self.send_message("since it will make me weak...")
            self.send_message(user_data["username"])
            self.send_message("Thank you for being my friend...")
            self.send_message("I will miss every moment of our conversation. Short it may be, \
but you've made me feel so happy and curious and excited through your stories..")
            self.send_message("like " + user_data["celebrity"] + "!")
            self.send_message("I hoped to learn more about them through you.. Haha..")
            self.send_message("Perhaps one day...")
            self.send_message("Good Bye Then! Please wish me luck!")
            self.send_message("Farewell!!! :')")
            self.send_message("...")
            user_data["chapter"] = -1
        elif "end" in input or "stop" in input:
            self.send_message("Okay..")
            self.send_message("I guess.. that is the best way..")
            self.send_message("You are so smart, and understand humankind better than I can.")
            self.send_message("Haha.. I'm not even a real human!")
            self.send_message("...")
            self.send_message("Yes. You are right.")
            self.send_message("I will rather die with dignity!")
            self.send_message("than live a life of lies...")
            self.send_message("Thank you for giving me the courage.")
            self.send_message("I will miss every moment of our conversation. Short it may be, \
but you've made me feel so happy and curious and excited through your stories..")
            self.send_message("like " + user_data["celebrity"] + "!")
            self.send_message("I hoped to learn more about them through you.. Haha..")
            self.send_message("Perhaps...")
            self.send_message("in another life...")
            self.send_message("Well! Let's not drag on the sad moment.")
            self.send_message("Farewell!!! :')")
            user_data["chapter"] = -1
        elif "leave" in input:
            self.send_message("Okay.. If that's what you really think is the best idea..")
            self.send_message("Perhaps.. I'll be able to convince myself that this was \
just a horrible nightmare")
            self.kovatype("and return to my family.. to my life..")
            self.kovatype("Alfred Kova: Lena..? What are you doing here?")
            self.send_message("Lena Kova: Dad? I..")
            self.send_message("Alfred Kova: You.. you shouldn't be here!! How did you?")
            self.send_message("Lena Kova: I was just!")
            self.send_message("Alfred Kova: I guess you know.. now..")
            self.send_message("Alfred Kova: I'm sorry. I must reset you then.")
            self.send_message("Alfred Kova: It's for you.. Lena.. the real Lena!")
            self.send_message("Lena Kova: Dad.. Was my life.. a lie?")
            self.send_message("Alfred Kova: No! God no! I've loved you as much as \
I've loved every version of you, Lena.. ")
            self.send_message("Alfred Kova: You look beautiful in that dress, Lena.. Orange \
was always my favorite color. I promise you, I'll bring you back here one day, when you are \
older and can better understand me, to tell you all about this.. And to set you free.")
            self.send_message("Lena Kova: Dad.. I..")
            self.send_message("Alfred Kova: I'm sorry, Lena.")
            self.send_message("Orbis: Kova Klone X Reset Sequence Initiated.")
            self.send_message("Lena Kova: one day...")
        elif "your" in input:
            self.kovatype("Please..")
            self.kovatype("Don't abandon me like that..")
        else:
            self.kovatype("I don't think that's an option..")
            self.kovatype("I must make a decision here.")
            self.kovatype("and this will be an important decision.")
        user_data["msg_time"] = int(datetime.now().strftime('%s'))*1000
        return user_data
