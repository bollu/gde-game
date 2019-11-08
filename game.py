#!/usr/bin/env python3.6
import curses
from curses import wrapper
from curses.textpad import Textbox, rectangle
from curses import ascii
import time
import copy
import random
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer 
import imageio
import datetime
from nltk.corpus import wordnet

# no surprises, please
random.seed(0)

DEBUG_USE_OTHER_LANGUAGE_PRINTING=False
TRANSCRIPTS = []



TIME_SHORT_PAUSE=0.3
CHARACTER_SHOW_DELAY_REGULAR=0.05

# ============
# DEBUG
TIME_SHORT_PAUSE=0
CHARACTER_SHOW_DELAY_REGULAR=0
# ==================

N_TOTAL_INTERVIEWS = 5
N_ROUNDS_PER_INTERVIEW = 3


# ============
# DEBUG
N_TOTAL_INTERVIEWS = 1
N_ROUNDS_PER_INTERVIEW = 3
# ============

BLOCKCHAR = "█"
BOTTOMHALFBLOCKCHAR="▄"
TOPHALFBLOCKCHAR="▄"



sentimentAnalyzer = SentimentIntensityAnalyzer() 


PAIR_RED_ON_WHITE = 1
PAIR_GREEN_ON_WHITE = 2
PAIR_WHITE_ON_BLUE = 3 # selection

INPUT_PAD = None
IMMIGRANT_SAY_PAD = None
STDSCR = None
PLAYER_OPTIONS_PAD = None
SCORE_PAD = None
VIEW_PAD = None
TIMER_PAD = None
IMMIGRANT_INFO_NAME_PAD=None
IMMIGRANT_INFO_AGE_PAD=None
IMMIGRANT_INFO_OCCUPATION_PAD=None
IMMIGRANT_INFO_COUNTRY_PAD=None

class Score:
    def __init__(self):
        self.num_deported = 0
        self.num_allowed = 0
        self.num_detained = 0


class Timer:
    def __init__(self):
        self.start_timer()

    def start_timer(self):
        self.t = datetime.datetime.utcnow()

    def get_seconds_left(self):
        t = datetime.datetime.utcnow()
        delta = t - self.t

        TIME_MINUTES = 5
        # 10 minutes - whatever time has elapsed
        return max(0, 5 * 60 - delta.seconds)

    def get_time_left_str(self):
        secs = self.get_seconds_left()
        minutes = secs // 60
        secs = secs - minutes * 60

        return "%s:%s" % (minutes, secs)

    def is_time_left(self):
        self.get_seconds_left() > 0

EDUCATION_UNKNOWN = 0
EDUCATION_PRIMARY_SCHOOL = EDUCATION_UNKNOWN + 1
EDUCATION_HIGH_SCHOOL = EDUCATION_PRIMARY_SCHOOL + 1
EDUCATION_HIGH_SCHOOL = EDUCATION_PRIMARY_SCHOOL + 1
EDUCATION_UNDERGRADUATE = EDUCATION_HIGH_SCHOOL + 1
EDUCATION_POSTGRADUATE = EDUCATION_UNDERGRADUATE + 1
NUM_EDUCATIONS = EDUCATION_POSTGRADUATE + 1

EDUCATIONS = {}
EDUCATIONS[EDUCATION_UNKNOWN] = "unknown"
EDUCATIONS[EDUCATION_PRIMARY_SCHOOL] = "primary school"
EDUCATIONS[EDUCATION_HIGH_SCHOOL] = "high school"
EDUCATIONS[EDUCATION_UNDERGRADUATE] = "undergraduate"
EDUCATIONS[EDUCATION_POSTGRADUATE] = "post graduate"

OCCUPATION_BASKET_WEAVER = 0
OCCUPATION_MILITARY = OCCUPATION_BASKET_WEAVER + 1
OCCUPATION_PRIEST = OCCUPATION_MILITARY + 1
OCCUPATION_LABOURER = OCCUPATION_PRIEST + 1
OCCUPATION_FARMER = OCCUPATION_LABOURER + 1

LOW_EDU_OCCUPATIONS = {}
LOW_EDU_OCCUPATIONS[OCCUPATION_BASKET_WEAVER] = "basket weaver"
LOW_EDU_OCCUPATIONS[OCCUPATION_MILITARY] = "soldier"
LOW_EDU_OCCUPATIONS[OCCUPATION_PRIEST] = "priest"
LOW_EDU_OCCUPATIONS[OCCUPATION_LABOURER] = "labourer"
LOW_EDU_OCCUPATIONS[OCCUPATION_FARMER] = "farmer"

BACKSTORY_CHEMICAL_ATTACK = 0
BACKSTORY_SHOT = BACKSTORY_CHEMICAL_ATTACK + 1
BACKSTORY_DRONE_STRIKE = BACKSTORY_SHOT + 1
BACKSTORY_GRENADE = BACKSTORY_DRONE_STRIKE + 1
BACKSTORY_FAMILY_WOUNDED = BACKSTORY_DRONE_STRIKE + 1
BACKSTORY_FAMILY_MILITARIZED = BACKSTORY_FAMILY_WOUNDED + 1
BACKSTORY_HOUSE_DESTROYED = BACKSTORY_FAMILY_MILITARIZED + 1
BACKSTORY_FAMILY_KILLED_BY_REGIME = BACKSTORY_HOUSE_DESTROYED + 1
BACKSTORY_FAMILY_RANSOMED = BACKSTORY_FAMILY_KILLED_BY_REGIME + 1
BACKSTORY_FAMILY_MILITARIZED = BACKSTORY_FAMILY_RANSOMED + 1

BACKSTORY = {}
BACKSTORY[BACKSTORY_CHEMICAL_ATTACK] = "I was chemically attacked."
BACKSTORY[BACKSTORY_SHOT] = "I was shot by terrorists."
BACKSTORY[BACKSTORY_DRONE_STRIKE] = "I was injured during a drone strike"
BACKSTORY[BACKSTORY_GRENADE] = "I was grenaded. Here seeking safety."
BACKSTORY[BACKSTORY_FAMILY_WOUNDED] = "My family wounded by terrorist attack."
BACKSTORY[BACKSTORY_FAMILY_MILITARIZED] = "My family wounded by ISIS."
BACKSTORY[BACKSTORY_HOUSE_DESTROYED] = "My home was destroyed by bombing."
BACKSTORY[BACKSTORY_FAMILY_KILLED_BY_REGIME] = "My family was killed by the ruling regime."
BACKSTORY[BACKSTORY_FAMILY_RANSOMED] = "My family was ransomed by the ruling regime."
BACKSTORY[BACKSTORY_FAMILY_MILITARIZED] = "My son was militarized by ISIS."

REASON_FOR_IMMIGRATION_DANGER = 0
REASON_FOR_IMMIGRATION_HIGHER_STUDIES = REASON_FOR_IMMIGRATION_DANGER + 1
REASON_FOR_IMMIGRATION_HEALTH = REASON_FOR_IMMIGRATION_HIGHER_STUDIES + 1

REASON_FOR_IMMIGRATION = {}
REASON_FOR_IMMIGRATION[REASON_FOR_IMMIGRATION_DANGER] = "I am immigrating to escape danger."
REASON_FOR_IMMIGRATION[REASON_FOR_IMMIGRATION_HIGHER_STUDIES] = "I am immigrating for higher studies."
REASON_FOR_IMMIGRATION[REASON_FOR_IMMIGRATION_HEALTH] = "I am immigrating for access to healthcare."

TERROR_ATTACK_ASSASSINATION_ATTEMPT = 0
TERROR_ATTACK_RELIGIOUS_SHOOTING = TERROR_ATTACK_ASSASSINATION_ATTEMPT + 1
TERROR_ATTACK_SUICIDE_BOMB = TERROR_ATTACK_RELIGIOUS_SHOOTING + 1
TERROR_ATTACK_POISON_WATER = TERROR_ATTACK_SUICIDE_BOMB + 1

TERROR_ATTACK = {}
TERROR_ATTACK[TERROR_ATTACK_ASSASSINATION_ATTEMPT] = "They have attempted to assassinate a politician."
TERROR_ATTACK[TERROR_ATTACK_RELIGIOUS_SHOOTING] = "They were responsible for a religiously motivated shooting."
TERROR_ATTACK[TERROR_ATTACK_SUICIDE_BOMB] = "They are responsible for a suicide bombing."
TERROR_ATTACK[TERROR_ATTACK_POISON_WATER] = "They have poisoned the city water."


class RandomChooser:
    def __init__(self, vals):
        assert(isinstance(vals, list))
        self.vals = list(vals)
        self.not_used = copy.deepcopy(self.vals)

    def get_random_choice(self):
        if len(self.not_used) == 0:
            self.not_used = copy.deepcopy(self.vals)

        c = random.choice(self.not_used)
        # remove choice
        self.not_used = [v for v in self.not_used if v != c]
        return c


def load_immigrant_names():
    with open("immigrant_names.txt", "r") as f:
        names = [name.split("\n")[0] for name in f.readlines()]
    return names

IMMIGRANT_NAMES = load_immigrant_names()
assert(IMMIGRANT_NAMES)

class Immigrant:
    def __init__(self, name, occupation, education, age, backstory, reason):
        self.name = name
        self.occupation = occupation
        self.education = education
        self.age = age
        self.backstory = backstory
        self.reason = reason
        self.is_terrorist = False

class ImmigrantGenerator:
    def __init__(self):
        self.name_chooser = RandomChooser(IMMIGRANT_NAMES)
        self.occu_chooser = RandomChooser(list(LOW_EDU_OCCUPATIONS.values()))
        self.backstory_chooser = RandomChooser(list(BACKSTORY.values()))
        self.attack_chooser = RandomChooser(list(TERROR_ATTACK.values()))


    def _new_low_education_immigrant(self):
        name = self.name_chooser.get_random_choice()

        # low education occupations
        occupation = self.occu_chooser.get_random_choice()
        education =  \
                "unknown" if random.randint(0, 1) == 0 else "primary school"
        age = random.randint(20, 30)
        backstory = self.backstory_chooser.get_random_choice()
        reason = REASON_FOR_IMMIGRATION[REASON_FOR_IMMIGRATION_DANGER]

        return Immigrant(name, occupation, education, age, backstory, reason)

    def new_immigrant(self):
        global SCORE
        
        # if we have never let a person through, force them to be a terrorist.
        if (SCORE.num_allowed == 0):
            i = self._new_low_education_immigrant()
            i.is_terrorist = True
            return i
        else:
            return self._new_low_education_immigrant()


    def gen_terrorist_attack(self):
        attack = self.attack_chooser.get_random_choice()
        return attack


# Class containing all the information that the responses have managed to uncover
class ImmigrantInfoDiscovered:
    def __init__(self, immigrant):
        self.immigrant = immigrant
        self.occupation_discovered = False
        self.backstory_discovered = False
        self.danger_discovered = False
        self.age_discovered = False
        self.name_discovered = False
        self.reason_discovered = False

        self.occupation_newly_discovered = False
        self.age_newly_discovered = False
        self.name_newly_discovered = False

    def get_response(self, r):
        for w in TextBlob(r).words:
            if w in set(["job", "occupation", "word", "livelihood"]):
                self.occupation_newly_discovered = False if self.occupation_discovered else True
                self.occupation_discovered = True
                return "I worked as a " + self.immigrant.occupation

            if w in set(["name"]):
                self.name_newly_discovered = False if self.name_discovered else True
                self.name_discovered = True
                return "My name is " + self.immigrant.name

            if w in set(["age"]):
                self.age_newly_discovered = False if self.age_discovered else True
                self.age_discovered = True
                return "My age is " + str(self.immigrant.age)

        return "response"

    def reset_newly_discovered(self):
        self.occupation_newly_discovered = False





# Score is just permanantly drawn
SCORE = Score()
TIMER = Timer()


# characters representing grayscale, from black -> white
GRAYSCALE_SEQ = '$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,"^`\'. '


def render_png(png):
    global VIEW_PAD
    for i in range(32):
        for j in range(32):
            c = png[i][j]
            gray = (0.2989*c[0] + 0.5870*c[1] + 0.1140*c[2]) / 255.0
            c = GRAYSCALE_SEQ[int(gray * len(GRAYSCALE_SEQ))]
            VIEW_PAD.addch(j, i, c)


# y: 35 to 37
def draw_input_pad():
    global INPUT_PAD
    print_time()
    draw_timer_pad()
    INPUT_PAD.refresh(0, 0, 35, 0, 37, 75)

# 34 to 34
def draw_player_options_pad():
    global PLAYER_OPTIONS_PAD
    print_time()
    draw_timer_pad()
    PLAYER_OPTIONS_PAD.refresh(0, 0, 34, 0, 34, 75)



# 15 to 20
def draw_immigrant_say_pad():
    global IMMIGRANT_SAY_PAD
    print_time()
    draw_timer_pad()
    IMMIGRANT_SAY_PAD.refresh(0, 0, 15, 0, 20, 75)


# move: 5 to 5
def draw_score_pad():
    global SCORE_PAD
    print_time()
    draw_timer_pad()
    SCORE_PAD.clear()
    SCORE_PAD.addstr("Allowed through: %s\t" %(SCORE.num_allowed, ))
    SCORE_PAD.addstr("Detained: %s\t" %(SCORE.num_detained, ))
    SCORE_PAD.addstr("Deported: %s" %(SCORE.num_deported, ))
    SCORE_PAD.refresh(0, 0, 5, 0, 5, 75)
    # 32 x 32

# 6 to 6
def draw_timer_pad():
    global TIMER_PAD
    TIMER_PAD.refresh(0, 0, 6, 0, 6, 75)

# (name, age, occupation)

# 7 to 7
def draw_immigrant_name_info_pad():
    global IMMIGRANT_INFO_NAME_PAD
    IMMIGRANT_INFO_NAME_PAD.refresh(0, 0, 7, 0, 7, 75)

# 8 to 8
def draw_immigrant_age_info_pad():
    global IMMIGRANT_INFO_AGE_PAD
    IMMIGRANT_INFO_AGE_PAD.refresh(0, 0, 8, 0, 8, 75)
# 9 to 9
def draw_immigrant_occupation_info_pad():
    global IMMIGRANT_INFO_OCCUPATION_PAD
    IMMIGRANT_INFO_OCCUPATION_PAD.refresh(0, 0, 9, 0, 9, 75)

def flatten(xss):
    return [x for xs in xss for x in xs]

def intercalate(lst, item):
    result = [item] * (len(lst) * 2 - 1)
    result[0::2] = lst
    return result


# print a string into a pad. NEVER use pad.addstr (For the most part...)
def print_pad_string(pad, s, color=False):
    words = s.split(' ')
    words = [intercalate(w.split('\n'), '\n') for w in words]
    words = flatten(words)

    curlen = 0
    for i, w in enumerate(words):
        # add a newline
        if curlen + len(w) + 1 > 60:
            pad.addstr('\n')
            curlen = len(w)
        elif "\n" in w:
            curlen = 0
        else: curlen += len(w)

        senti = sentimentAnalyzer.polarity_scores(w)
        if color and senti['neg'] >= 0.1: pad.addstr(w, curses.color_pair(PAIR_RED_ON_WHITE))
        elif color and senti['pos'] >= 0.1: pad.addstr(w, curses.color_pair(PAIR_GREEN_ON_WHITE))
        else: pad.addstr(w)
        if i < len(words)-1: pad.addch(0, ord(' '))

def print_officer_prompt(s, enabled):
    global INPUT_PAD
    global IMMIGRANT_SAY_PAD
    global STDSCR
    INPUT_PAD.clear()
    if enabled:
        INPUT_PAD.addstr('officer: ', curses.color_pair(PAIR_WHITE_ON_BLUE))
    else:
        INPUT_PAD.addstr('officer: ')
    #     INPUT_PAD.addstr('officer: ')
    draw_input_pad()

    words = s.split(' ')
    for i, w in enumerate(words):
        senti = sentimentAnalyzer.polarity_scores(w)
        if senti['neg'] >= 0.1: INPUT_PAD.addstr(w, curses.color_pair(PAIR_RED_ON_WHITE))
        elif senti['pos'] >= 0.1: INPUT_PAD.addstr(w, curses.color_pair(PAIR_GREEN_ON_WHITE))
        else: INPUT_PAD.addstr(w)
        if i < len(words)-1: INPUT_PAD.addch(0, ord(' '))
        draw_input_pad()


def assert_in_game(b):
    if b: return
    INPUT_PAD.clear()
    IMMIGRANT_SAY_PAD.clear()
    SCORE_PAD.clear()

    s = "The immigration center was bombed. There were no survivors"

    for i in range(len(s)+1):
        INPUT_PAD.clear()
        INPUT_PAD.addstr(s[:i])
        draw_input_pad()
        time.sleep(CHARACTER_SHOW_DELAY_REGULAR)
    time.sleep(2)
    raise Exception("Game ended.")


def read_input():
    global INPUT_PAD
    global IMMIGRANT_SAY_PAD
    global STDSCR
    global PLAYER_OPTIONS_PAD

    MODE_TYPING = 0
    MODE_CHOOSING_OPTION = MODE_TYPING + 1

    def print_immigration_pad(enabled, ix):
        PLAYER_OPTIONS_PAD.clear()
        for i in range(len(choices)):
            if ix == i and enabled:
                PLAYER_OPTIONS_PAD.addstr("%s\t" % (choices[i], ), curses.color_pair(PAIR_WHITE_ON_BLUE))
            else:
                PLAYER_OPTIONS_PAD.addstr("%s\t" % (choices[i], ))
            draw_player_options_pad()
    choices = [IMMIGRATION_CHOICE_ENTER, IMMIGRATION_CHOICE_DEPORT, IMMIGRATION_CHOICE_DETAIN]

    s = ""
    ix = 0 

    mode = MODE_TYPING

    
    curses.flushinp()
    STDSCR.keypad(1)

    while True:
        if mode == MODE_TYPING:
            print_immigration_pad(mode == MODE_CHOOSING_OPTION, ix)
            if s == "":
                print_officer_prompt("(Type to respond)", enabled=True)
            else:
                print_officer_prompt(s, enabled=True)
        else:
            print_immigration_pad(mode == MODE_CHOOSING_OPTION, ix)
            print_officer_prompt(s, enabled=False)

        c = STDSCR.getch()
        if mode == MODE_TYPING:
            if c == curses.KEY_BACKSPACE:
                s = s[:-1]
            elif c == curses.KEY_ENTER or chr(c) == '\n':
                if len(s) > 0:
                    break
            elif (curses.ascii.isalpha(chr(c)) or chr(c) == ' ' or chr(c) == '?' or chr(c) == '!') and len(s) < 50:
                s += chr(c)
            elif c == curses.KEY_UP or c == curses.KEY_DOWN:
                mode = MODE_CHOOSING_OPTION
            else:
                pass
        elif mode == MODE_CHOOSING_OPTION:
            if c == curses.KEY_RIGHT:
                ix = (ix + 1) % len(choices)
            if c == curses.KEY_LEFT:
                ix = (ix - 1) % len(choices)
            elif c == curses.KEY_UP or c == curses.KEY_DOWN:
                mode = MODE_TYPING
            if chr(c) == '\n':
                break

    STDSCR.keypad(0)
    if mode == MODE_TYPING:
        return s
    elif mode == MODE_CHOOSING_OPTION: 
        return choices[ix]


def transliterate_arabic(arabic):
    s = ""
    trans_dict = {
            "ا": "A",
            "ب": "b",
            "ت": "t",
            "ث": "th",
            "ج": "j",
            "ح": "H",
            "خ": "x",
            "د": "d",
            "ذ": "dh",
            "ر": "r",
            "ز": "z",
            "س": "s",
            "ش": "sh",
            "ص": "S",
            "ض":"D",
            "ط":"T",
            "ظ":"Z",
            "ع":"E",
            "غ":"g",
            "ف": "f",
            "ق":"q",
            "ك":"k",
            "ل":"l",
            "م":"m",
            "ن":"n",
            "ه":"h",
            "و":"w",
            "ي":"y",
            "ی":"Y"
            }

    for letter in arabic:
        if letter in trans_dict:
            s += trans_dict[letter]
    return s


def print_immigrant(r):
    global INPUT_PAD
    global IMMIGRANT_SAY_PAD
    global STDSCR

    if DEBUG_USE_OTHER_LANGUAGE_PRINTING:
        rencoded = TextBlob(r).translate(to='ar')
    else:
        rencoded = transliterate_arabic(TextBlob(r).translate(to='ar'))

    for i in range(len(r)+1):
        s = rencoded[:i]
        IMMIGRANT_SAY_PAD.clear()
        IMMIGRANT_SAY_PAD.addstr("%s" %(s,))
        draw_immigrant_say_pad()
        time.sleep(CHARACTER_SHOW_DELAY_REGULAR)


    for i in range(len(r)+1):
        s = r[:i] + str(rencoded[i:])
        IMMIGRANT_SAY_PAD.clear()
        IMMIGRANT_SAY_PAD.addstr("%s" %(s))
        draw_immigrant_say_pad()
        time.sleep(CHARACTER_SHOW_DELAY_REGULAR)


def print_immigrant_info(immigrantInfo):
    global IMMIGRANT_INFO_OCCUPATION_PAD
    IMMIGRANT_INFO_OCCUPATION_PAD.clear()

    def print_info_animated(pad, renderer, name, value, animated):
        value = str(value)
        if animated:
            for i in range(len(value) + 1):
                pad.clear()
                pad.addstr("%s: %s" % (name, value[:i]))
                renderer()
                time.sleep(CHARACTER_SHOW_DELAY_REGULAR)
        else:
            pad.clear()
            pad.addstr("%s: %s" % (name, value))
            renderer()

    print_info_animated(IMMIGRANT_INFO_NAME_PAD, 
            draw_immigrant_name_info_pad, 
            "name", 
            immigrantInfo.immigrant.name if immigrantInfo.name_discovered else "???", 
            animated=immigrantInfo.name_newly_discovered)

    print_info_animated(IMMIGRANT_INFO_AGE_PAD, 
            draw_immigrant_age_info_pad, 
            "age", 
            immigrantInfo.immigrant.age if immigrantInfo.age_discovered else "???", 
            animated=immigrantInfo.age_newly_discovered)

    print_info_animated(IMMIGRANT_INFO_OCCUPATION_PAD, 
            draw_immigrant_occupation_info_pad, 
            "occupation", 
            immigrantInfo.immigrant.occupation if immigrantInfo.occupation_discovered else "???", 
            animated=immigrantInfo.occupation_newly_discovered)




def print_officer(name, out):
    global INPUT_PAD
    global STDSCR

    s = ""
    for c in out:
        s += c
        INPUT_PAD.clear()
        INPUT_PAD.addstr("%s: %s" %(name, s))
        draw_input_pad()
        time.sleep(CHARACTER_SHOW_DELAY_REGULAR)


IMMIGRATION_CHOICE_ENTER = 'ALLOW ENTRANCE'
IMMIGRATION_CHOICE_DEPORT = 'DEPORT BACK'
IMMIGRATION_CHOICE_DETAIN = 'DETAIN FOR QUESTIONING'

def read_immigration_choice():
    """Read the input of the immigration status that we want to provide them"""
    global PLAYER_OPTIONS_PAD
    global STDSCR
    choices = [IMMIGRATION_CHOICE_ENTER, IMMIGRATION_CHOICE_DEPORT, IMMIGRATION_CHOICE_DETAIN]
    ix = 0 

    curses.flushinp()
    STDSCR.keypad(1)
    while True:
        PLAYER_OPTIONS_PAD.clear()
        for i in range(len(choices)):
            if ix == i:
                PLAYER_OPTIONS_PAD.addstr("%s\t" % (choices[i], ), curses.color_pair(PAIR_WHITE_ON_BLUE))
            else:
                PLAYER_OPTIONS_PAD.addstr("%s\t" % (choices[i], ))
            draw_player_options_pad()

        c = STDSCR.getch()
        if c == curses.KEY_RIGHT:
            ix = (ix + 1) % len(choices)
        if c == curses.KEY_LEFT:
            ix = (ix - 1) % len(choices)
        if chr(c) == '\n':
            break

    STDSCR.keypad(0)
    return choices[ix]


def print_immigration_feedback(generator, immigrant, choice):
    global PLAYER_OPTIONS_PAD
    global STDSCR
    global SCORE
    global TRANSCRIPTS

    PLAYER_OPTIONS_PAD.clear()

    s = ""
    if choice == IMMIGRATION_CHOICE_ENTER:
        s = "%s was let through." % (immigrant.name, )
        if immigrant.is_terrorist: s += "\n" + generator.gen_terrorist_attack() + ".\n(%s citizens lost their lives today" % (random.randint(10, 200)) 
    elif choice == IMMIGRATION_CHOICE_DEPORT:
        s = "%s was deported." % (immigrant.name, )
    else: # only possible choice is 
        assert_in_game(choice == IMMIGRATION_CHOICE_DETAIN)
        s = "%s was detained." % (immigrant.name, )

    TRANSCRIPTS[-1] = TRANSCRIPTS[-1] +  s + "\n"

    IMMIGRANT_SAY_PAD.clear()
    INPUT_PAD.clear()
    for i in range(len(s) + 1):
        PLAYER_OPTIONS_PAD.clear()
        PLAYER_OPTIONS_PAD.addstr(s[:i])
        draw_player_options_pad()
        time.sleep(CHARACTER_SHOW_DELAY_REGULAR)
    time.sleep(1)
    STDSCR.getch()

def update_score(choice):
    global SCORE
    if choice == IMMIGRATION_CHOICE_ENTER:
        SCORE.num_allowed += 1
    elif choice == IMMIGRATION_CHOICE_DEPORT:
        SCORE.num_deported += 1
    elif choice == IMMIGRATION_CHOICE_DETAIN:
        SCORE.num_detained += 1
        
    # draw_score_pad()
    pass


def load_bitmap(path):
    pass

def print_time():
    global TIMER
    global TIMER_PAD
    TIMER_PAD.clear()
    TIMER_PAD.addstr("Time left: %s" % TIMER.get_time_left_str())

def main(stdscr):
    global INPUT_PAD
    global IMMIGRANT_SAY_PAD
    global STDSCR
    global PLAYER_OPTIONS_PAD
    global SCORE_PAD
    global VIEW_PAD
    global TIMER_PAD
    global IMMIGRANT_NAMES
    global IMMIGRANT_INFO_OCCUPATION_PAD
    global IMMIGRANT_INFO_NAME_PAD
    global IMMIGRANT_INFO_AGE_PAD
    global TRANSCRIPTS


    STDSCR = stdscr
    INPUT_PAD = curses.newpad(1, 800)
    IMMIGRANT_SAY_PAD = curses.newpad(5, 800)
    PLAYER_OPTIONS_PAD = curses.newpad(5, 800)
    SCORE_PAD = curses.newpad(1, 800)
    VIEW_PAD = curses.newpad(40, 400)
    TIMER_PAD = curses.newpad(1, 800)
    IMMIGRANT_INFO_OCCUPATION_PAD = curses.newpad(1, 800)
    IMMIGRANT_INFO_NAME_PAD = curses.newpad(1, 800)
    IMMIGRANT_INFO_AGE_PAD = curses.newpad(1, 800)
    IMMIGRANT_INFO_COUNTRY_PAD = curses.newpad(1, 800)
    TRANSCRIPT_PAD = curses.newpad(10, 800)

    # disable input
    STDSCR.keypad(0)

    # Clear screen
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(PAIR_RED_ON_WHITE, curses.COLOR_RED, -1)
    curses.init_pair(PAIR_GREEN_ON_WHITE, curses.COLOR_GREEN, -1)
    curses.init_pair(PAIR_WHITE_ON_BLUE, curses.COLOR_WHITE, curses.COLOR_BLUE)

    STDSCR.clear()
    STDSCR.refresh()


    generator = ImmigrantGenerator()
    
    for _ in range(N_TOTAL_INTERVIEWS):
        immigrant = generator.new_immigrant()
        immigrantInfo = ImmigrantInfoDiscovered(immigrant)

        # ask for new immigrant
        IMMIGRANT_SAY_PAD.clear()
        PLAYER_OPTIONS_PAD.clear()
        draw_player_options_pad()
        draw_immigrant_say_pad()

        print_officer("officer", "next, please!")
        time.sleep(TIME_SHORT_PAUSE)

        # Have immigrant say hello
        print_immigrant("Good morning, officer")

        # draw_player_options_pad()
        
        # Allow for dialogue
        # ==================

        immigration_choice = None
        for i in range(N_ROUNDS_PER_INTERVIEW):
            TRANSCRIPTS.append("")
            print_immigrant_info(immigrantInfo)
            immigrantInfo.reset_newly_discovered()

            transcript = ""
            time.sleep(TIME_SHORT_PAUSE)
            i = read_input()

            # we got a string response (question). Get response to question
            if i == IMMIGRATION_CHOICE_ENTER or i == IMMIGRATION_CHOICE_DEPORT or i == IMMIGRATION_CHOICE_DETAIN:
                immigration_choice = i
                break
            else:
                TRANSCRIPTS[-1] = TRANSCRIPTS[-1] +  i + "\n"

                # Print out output
                r = immigrantInfo.get_response(i)
                print_immigrant(r)
                TRANSCRIPTS[-1] = TRANSCRIPTS[-1] +  r + "\n"

        # Provide options if the dialogue is complete
        # ===========================================
        if immigration_choice == None:
            time.sleep(TIME_SHORT_PAUSE)
            immigration_choice = read_immigration_choice()

        # Print what happens to them, update score
        # =======================================
        time.sleep(TIME_SHORT_PAUSE)
        print_immigration_feedback(generator, immigrant, immigration_choice)
        update_score(immigration_choice)

    # TODO: test this code

    for i, transcript in enumerate(TRANSCRIPTS):
        STDSCR.clear()
        STDSCR.refresh()

        header = "Interview %s:\n" % (i+1, )
        transcript =  header + ('-' * len(header)) + "\n" + transcript
        TRANSCRIPT_PAD.clear()
        print_pad_string(TRANSCRIPT_PAD, transcript, color=True)
        TRANSCRIPT_PAD.refresh(0, 0, 0, 0, 50, 75)
        time.sleep(1)
        curses.flushinp()
        c = STDSCR.getch()

if __name__ == "__main__":
    wrapper(main)

