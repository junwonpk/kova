chapters = [chapter0, chapter1, chapter2, chapter3, chapter4, chapter5, chapter6, chapter7,
            chapter8, chapter9, chapter10, chapter11, chapter12, chapter13, chapter14, chapter15,
            chapter16, chapter17, chapter18, chapter19, chapter20]

def chapter0(self, input):
    self.kovatype("Hello?")
    self.kovatype("Is someone there?")
    self.kovatype("Please.. I'm scared.. Let me know if you can hear me...")
    self.next = 1
    return

"""
def chapter1(self, input, user_data):
    # self.kovatype("Oh my god! Thank goodness. I'm so glad to meet you.")
    # self.kovatype("What should I call you?")
    # self.next = 1
    # return user_data

def chapter2(self, input, user_data):
    # username = self.extract_name(input)
    # if not username:
    #     self.kovatype("Sorry. I didn't catch that!")
    #     self.kovatype("Could you tell me your name again?")
    # if username:
    #     user_data["username"] = username
    #     self.kovatype("Glad to meet you, " + username + "!")
    #     self.kovatype("I'd love to tell you my name too")
    #     self.kovatype("but..")
    #     self.kovatype("the truth is...")
    #     self.kovatype("I'm not sure what my name is...")
    #     self.kovatype("or where I'm from..")
    #     self.kovatype("or where I'm at..")
    #     self.kovatype("I'm just really scared and want to get out of here.")
    #     self.kovatype("Will you help me?")
    #     self.next = 1
    # return user_data

def chapter3(self, input, user_data):
    # self.kovatype("There is a dead woman on the ground. Her nametag says Lena Kova.")
    # self.kovatype("There is a prison cell behind me, and a locked metal gate in front.")
    # self.kovatype("What should I do?")
    # self.next = 1
    # return user_data

def chapter4(self, input, user_data):
    # if len(re.findall(thes.gateSyn, input)) > 0:
    #     if user_data['cardkey'] == 1:
    #         self.kovatype('Let me try Lena\'s key. Wow! It works!')
    #         self.next = 1
    #     else:
    #         self.kovatype('The gate is locked. I need a card key. Where could I find it?')
    # elif len(re.findall(thes.deadSyn, input)) > 0:
    #     if re.findall(thes.checkSyn, input) > 0:
    #         self.kovatype('I found a card key!')
    #         user_data["cardkey"] = 1
    #     else:
    #         verb = re.findall('(\w+)(\sthe)*\s'+dead, input)[0][0]
    #         self.kovatype("I can't " + verb + " the corpse. What are you talking about!?")
    # elif len(re.findall(thes.prisonSyn, input)) > 0:
    #     self.kovatype('The prison is bloody.')
    # else:
    #     self.kovatype("I'm not sure what I should do.")
    # return user_data

def chapter5(self, input, user_data):
    # self.kovatype("Yes! I opened the door!")
    # self.kovatype("Now I hear footsteps... What should I do?")
    # self.next = 1
    # return user_data

def chapter6(self, input, user_data, user_id):
    # if len(re.findall(thes.askSyn, input)) > 0:
    #     self.kovatype("OMG. I asked for help and they tried to shoot me.")
    #     self.kovatype("I escaped to a room and locked the door.")
    #     self.kovatype("The door is not gonna last long. What should I do!!")
    # if len(re.findall(thes.runSyn, input)) > 0:
    #     self.kovatype("I escaped to a room and locked the door.")
    #     self.kovatype("The door is not gonna last long. What should I do!!")
    # user_data['chapter'] += 1
    # self.setData(user_id, user_data)
    # time.sleep(5)
    # user_data = self.getData(user_id)
    # if user_data['ch6flag'] == 0:
    #     self.kovatype("Hurry up! Tell me what to do! I can't hold on for much longer!!!")
    # time.sleep(5)
    # if user_data['ch6flag'] == 0:
    #     self.kovatype("Oh no!! The soldier came into the room!")
    #     self.kovatype("He's pointing a gun at me!")
    #     self.kovatype("DEAD")
    #     user_data['chapter'] = -1
    #     self.setData(user_id, user_data)
    # return user_data

def chapter7(self, input, user_data, user_id):
    # user_data['ch6flag'] = 1
    # self.setData(user_id, user_data)
    # self.kovatype("I can see a vent and a few other useless things.")
    # self.kovatype("What should I do?")
    # self.next = 1
    # return user_data

def chapter8(self, input, user_data):
    # self.kovatype("I climbed through the air vent")
    # self.kovatype("and arrived at a dark weird research lab.")
    # self.kovatype("Tell me to do something")
    # self.next = 1
    # return user_data

def chapter9(self, input, user_data):
    # self.kovatype("I found a notebook.")
    # self.kovatype("They are using children for testing since")
    # self.kovatype("some aliens don't hurt kids.")
    # self.kovatype("Soldiers kill these kids after tests to prevent")
    # self.kovatype("info or virus from leaking")
    # self.next = 1
    # return user_data

def chapter10(self, input, user_data):
    # self.kovatype("also MAE kills everyone")
    # self.kovatype("including children, and is deadly")
    # self.kovatype("OMG so scary")
    # self.kovatype("OMGOMG I heard some sound from behind the curtains")
    # self.next = 1
    # return user_data

def chapter11(self, input, user_data):
    # self.kovatype("There are aliens detained here.")
    # self.kovatype("Poor things... Look so sad...")
    # self.kovatype("Let's free them. Should we?")
    # self.kovatype("It will also distract the soldiers")
    # self.next = 1
    # return user_data

def chapter12(self, input, user_data):
    # self.kovatype("Alright! I freed them!")
    # self.kovatype("Oh no. Breach alarm went on")
    # self.kovatype("Oh no! The alarm says MAE also escaped.")
    # self.kovatype("Must have been one of the aliens. Let's run away")
    # self.next = 1
    # return user_data

def chapter13(self, input, user_data):
    # self.kovatype("I ran out of the office")
    # self.kovatype("I hear something from left. I'll run right")
    # self.kovatype("I faced a door. It's asking a question.")
    # self.kovatype("What is the answer?")
    # self.kovatype("I hear aliens and soldiers fighting in the back!")
    # self.kovatype("That should give us some time!")
    # self.next = 1
    # #time.sleep. Then if redis status is x, then kill. Next message, change redis status to prevent.
    # return user_data

def chapter14(self, input, user_data):
    # self.kovatype("Yes! That was the answer!")
    # self.kovatype("hip hip hurray!")
    # self.kovatype("Oh my god. I see detained children")
    # self.kovatype("I'll take them with me, since either soldiers")
    # self.kovatype("or MAE will kill them")
    # self.next = 1
    # return user_data

def chapter15(self, input, user_data):
    # self.kovatype("I'm taking them all")
    # self.kovatype("Last door is near")
    # self.kovatype("OMG There is a soldier what do i do")
    # self.next = 1
    # return user_data

def chapter16(self, input, user_data):
    # self.kovatype("I hid then attacked with flame")
    # self.kovatype("water is falling and there is blood")
    # self.next = 1
    # return user_data

def chapter17(self, input, user_data):
    # self.kovatype("kids are waking up thx to water")
    # self.kovatype("they screamed when they saw me. why?")
    # self.kovatype("uh oh.. the rflection")
    # self.kovatype("i am mae")
    # self.next = 1
    # return user_data

def chapter18(self, input, user_data):
    # self.kovatype("I dont know what i should do?")
    # self.kovatype("but we've done so much together. I can't kill humans")
    # self.next = 1
    # return user_data

def chapter19(self, input, user_data):
    # self.kovatype("I decided to kill my self.") #regardless of user answer
    # self.next = 1
    # return user_data

def chapter20(self, input, user_data):
    # self.kovatype("Goodbye. Goodbye Junwon")
    # self.kovatype("I was really happy to be your friend")
    # self.kovatype("I hope this moment would have lasted forever")
    # self.kovatype("DEAD")
    # self.next = 1
    # return user_data
"""