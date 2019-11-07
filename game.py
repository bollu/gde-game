#!/usr/bin/env python3.6
import curses
from curses import wrapper
from curses.textpad import Textbox, rectangle
from curses import ascii
import time
import random
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer 
import imageio
import datetime
from nltk.corpus import wordnet

TRANSCRIPTS = []

# TIME_SHORT_PAUSE=0.3
# CHARACTER_SHOW_DELAY_REGULAR=0.04


TIME_SHORT_PAUSE=0.0
CHARACTER_SHOW_DELAY_REGULAR=0.00

N_TOTAL_INTERVIEWS = 5
N_ROUNDS_PER_INTERVIEW = 3

BLOCKCHAR = "█"
BOTTOMHALFBLOCKCHAR="▄"
TOPHALFBLOCKCHAR="▄"


sprite = imageio.imread('sprite.png')
print(sprite.shape)



sentimentAnalyzer = SentimentIntensityAnalyzer() 


PAIR_RED_ON_WHITE = 1
PAIR_GREEN_ON_WHITE = 2
PAIR_WHITE_ON_BLUE = 3 # selection

INPUT_PAD = None
CHOICES_PAD = None
STDSCR = None
IMMIGRATION_PAD = None
SCORE_PAD = None
VIEW_PAD = None
TIMER_PAD = None
IMMIGRANT_INFO_OCCUPATION_PAD=None

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
OCCUPATION_LAWYER = OCCUPATION_MILITARY + 1
OCCUPATION_PRIEST = OCCUPATION_LAWYER + 1
OCCUPATION_DOCTOR = OCCUPATION_PRIEST + 1
OCCUPATION_LABOURER = OCCUPATION_DOCTOR + 1
OCCUPATION_CARPET_SELLER = OCCUPATION_LABOURER + 1
OCCUPATION_FARMER = OCCUPATION_CARPET_SELLER + 1

LOW_EDU_OCCUPATIONS = {}
LOW_EDU_OCCUPATIONS[OCCUPATION_BASKET_WEAVER] = "basket weaver"
LOW_EDU_OCCUPATIONS[OCCUPATION_MILITARY] = "soldier"
LOW_EDU_OCCUPATIONS[OCCUPATION_PRIEST] = "priest"
LOW_EDU_OCCUPATIONS[OCCUPATION_CARPET_SELLER] = "carpet seller"
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
        self.names = 0
        self.occu = 0
        self.edu = 0
        self.attack = 0
        self.back = 0
        self.attack = 0


    def _new_low_education_immigrant(self):
        name = IMMIGRANT_NAMES[self.names % len(IMMIGRANT_NAMES)]
        self.names += 1

        # low education occupations
        occupation = LOW_EDU_OCCUPATIONS[(self.occu + 1) % len(LOW_EDU_OCCUPATIONS)]
        self.occu += 1
        education =  \
            EDUCATIONS[EDUCATION_UNKNOWN if random.randint(0, 1) == 0 else EDUCATION_PRIMARY_SCHOOL]
        age = random.randint(20, 30)
        backstory = BACKSTORY[self.back % len(BACKSTORY)]
        self.back += 1

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
        attack = TERROR_ATTACK[self.attack]
        self.attack += 1
        return attack


# Class containing all the information that the responses have managed to uncover
class ImmigrantInfoDiscovered:
    def __init__(self, immigrant):
        self.immigrant = immigrant
        self.occupation_discoverd = False
        self.backstory_discovered = False
        self.danger_discovered = False
        self.age_discovered = False
        self.reason_discovered = False

        self.occupation_newly_discovered = False

    def get_response(self, r):
        for w in TextBlob(r).words:
            if w in set(["job", "occupation", "word", "livelihood"]):
                self.occpuation_newly_discovered = False if self.occupation_discoverd else True
                self.occupation_discovered = True
                return "I worked as a " + self.immigrant.occupation
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


def draw_input_pad():
    global INPUT_PAD
    INPUT_PAD.refresh(0, 0, 1, 0, 1, 75)
    print_time()
    draw_timer_pad()


def draw_choices_pad():
    global CHOICES_PAD
    CHOICES_PAD.refresh(0, 0, 0, 0, 0, 75)
    print_time()
    draw_timer_pad()


def draw_immigration_pad():
    global IMMIGRATION_PAD
    IMMIGRATION_PAD.refresh(0, 0, 2, 0, 2, 75)
    print_time()
    draw_timer_pad()

def draw_score_pad():
    global SCORE_PAD
    SCORE_PAD.clear()
    SCORE_PAD.addstr("Allowed through: %s\t" %(SCORE.num_allowed, ))
    SCORE_PAD.addstr("Detained: %s\t" %(SCORE.num_detained, ))
    SCORE_PAD.addstr("Deported: %s" %(SCORE.num_deported, ))
    SCORE_PAD.refresh(0, 0, 3, 0, 3, 75)
    print_time()
    draw_timer_pad()
    # 32 x 32

def draw_timer_pad():
    global TIMER_PAD
    TIMER_PAD.refresh(0, 0, 4, 0, 4, 75)


# 5 x 75
def draw_immigrant_occupation_info_pad():
    global IMMIGRANT_INFO_OCCUPATION_PAD
    IMMIGRANT_INFO_OCCUPATION_PAD.refresh(0, 0, 5, 0, 5 + 1, 75)

def print_officer_prompt(s):
    global INPUT_PAD
    global CHOICES_PAD
    global STDSCR
    INPUT_PAD.clear()
    INPUT_PAD.addstr('officer: ')
    draw_input_pad()
    # blob = TextBlob(s)

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
    CHOICES_PAD.clear()
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
    global CHOICES_PAD
    global STDSCR
    # stdscr.refresh()
    s = ""
    
    curses.flushinp()
    STDSCR.keypad(1)
    while True:
        if s == "":
            print_officer_prompt("(Type to respond)")
        else:
            print_officer_prompt(s)

        c = STDSCR.getch()
        if c == curses.KEY_BACKSPACE:
            s = s[:-1]
        elif c == curses.KEY_ENTER or chr(c) == '\n':
            if len(s) > 0:
                break
        else:
            s += chr(c)
        # stdscr.refresh()


    STDSCR.keypad(0)
    return s



def print_immigrant(r):
    global INPUT_PAD
    global CHOICES_PAD
    global STDSCR

    rencoded = TextBlob(r).translate(to='ar')

    for i in range(len(r)+1):
        s = rencoded[:i]
        CHOICES_PAD.clear()
        CHOICES_PAD.addstr("%s" %(s,))
        draw_choices_pad()
        time.sleep(CHARACTER_SHOW_DELAY_REGULAR)


    for i in range(len(r)+1):
        s = r[:i] + str(rencoded[i:])
        CHOICES_PAD.clear()
        CHOICES_PAD.addstr("%s" %(s))
        draw_choices_pad()
        time.sleep(CHARACTER_SHOW_DELAY_REGULAR)


def print_immigrant_info(immigrantInfo):
    global IMMIGRANT_INFO_OCCUPATION_PAD
    IMMIGRANT_INFO_OCCUPATION_PAD.clear()

    def print_info_animated(pad, renderer, name, value, animated):
        if animated:
            for i in range(len(value) + 1):
                pad.clear()
                pad.addstr("%s: %s" % (name, value[:i]))
                renderer()
                time.sleep(CHARACTER_SHOW_DELAY_REGULAR)
        else:
            pad.clear()
            padd.addstr("%s: %s" % (name, value))
            renderer()


    print_info_animated(IMMIGRANT_INFO_OCCUPATION_PAD, 
            draw_immigrant_occupation_info_pad, 
            "occupation", 
            immigrantInfo.immigrant.occupation, 
            animated=immigrantInfo.occpuation_newly_discovered)

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
    global IMMIGRATION_PAD
    global STDSCR
    choices = [IMMIGRATION_CHOICE_ENTER, IMMIGRATION_CHOICE_DEPORT, IMMIGRATION_CHOICE_DETAIN]
    ix = 0 

    curses.flushinp()
    STDSCR.keypad(1)
    while True:
        IMMIGRATION_PAD.clear()
        for i in range(len(choices)):
            if ix == i:
                IMMIGRATION_PAD.addstr("%s\t" % (choices[i], ), curses.color_pair(PAIR_WHITE_ON_BLUE))
            else:
                IMMIGRATION_PAD.addstr("%s\t" % (choices[i], ))
            draw_immigration_pad()

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
    global IMMIGRATION_PAD
    global STDSCR
    global SCORE

    IMMIGRATION_PAD.clear()

    s = ""
    if choice == IMMIGRATION_CHOICE_ENTER:
        s = "%s was let through." % (immigrant.name, )
        if immigrant.is_terrorist: s += " " + generator.gen_terrorist_attack() + ". (%s citizens lost their lives today" % (random.randint(10, 200)) 
    elif choice == IMMIGRATION_CHOICE_DEPORT:
        s = "%s was deported." % (immigrant.name, )
    else: # only possible choice is 
        assert_in_game(choice == IMMIGRATION_CHOICE_DETAIN)
        s = "%s was detained." % (immigrant.name, )


    CHOICES_PAD.clear()
    INPUT_PAD.clear()
    for i in range(len(s) + 1):
        IMMIGRATION_PAD.clear()
        IMMIGRATION_PAD.addstr(s[:i])
        draw_immigration_pad()
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
        
    draw_score_pad()
    pass

def print_immigrant_hello(immigrant_name):
    print_immigrant("hello. My name is " + immigrant_name)

def load_bitmap(path):
    pass

def print_time():
    global TIMER
    global TIMER_PAD
    TIMER_PAD.clear()
    TIMER_PAD.addstr("Tme left: %s" % TIMER.get_time_left_str())

def main(stdscr):
    global INPUT_PAD
    global CHOICES_PAD
    global STDSCR
    global IMMIGRATION_PAD
    global SCORE_PAD
    global VIEW_PAD
    global TIMER_PAD
    global IMMIGRANT_NAMES
    global IMMIGRANT_INFO_OCCUPATION_PAD
    global TRANSCRIPTS


    STDSCR = stdscr
    INPUT_PAD = curses.newpad(1, 800)
    CHOICES_PAD = curses.newpad(1, 800)
    IMMIGRATION_PAD = curses.newpad(1, 800)
    SCORE_PAD = curses.newpad(1, 800)
    VIEW_PAD = curses.newpad(40, 400)
    TIMER_PAD = curses.newpad(1, 800)
    IMMIGRANT_INFO_OCCUPATION_PAD = curses.newpad(1, 800)

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


    render_png(sprite)
    VIEW_PAD.refresh(0, 0, 4, 0, 4 + 32, 32)

    generator = ImmigrantGenerator()
    
    for _ in range(N_TOTAL_INTERVIEWS):
        immigrant = generator.new_immigrant()
        immigrantInfo = ImmigrantInfoDiscovered(immigrant)

        # ask for new immigrant
        CHOICES_PAD.clear()
        IMMIGRATION_PAD.clear()
        draw_immigration_pad()
        draw_choices_pad()

        print_officer("officer", "next, please!")
        time.sleep(TIME_SHORT_PAUSE)

        # Have immigrant say hello
        print_immigrant_hello(immigrant.name)
        # draw_immigration_pad()
        
        # Allow for dialogue
        # ==================
        for i in range(N_ROUNDS_PER_INTERVIEW):
            transcript = ""
            time.sleep(TIME_SHORT_PAUSE)
            i = read_input()
            transcript += i + "\n"

            # Print out output
            r = immigrantInfo.get_response(i)
            transcript += transcript + "\n"
            print_immigrant(r)
            print_immigrant_info(immigrantInfo)
            # reset fields that we will animate for being newly discovered
            immigrantInfo.reset_newly_discovered()
        TRANSCRIPTS.append(transcript)

        # Provide options
        # ===============
        time.sleep(TIME_SHORT_PAUSE)
        immigration_choice = read_immigration_choice()
        time.sleep(TIME_SHORT_PAUSE)

        # Print what happens to them, update score
        print_immigration_feedback(generator, immigrant, immigration_choice)
        update_score(immigration_choice)

    # TODO: test this code
    INPUT_PAD.clear()
    CHOICES_PAD.clear()
    STDSCR.clear()
    IMMIGRATION_PAD.clear()
    SCORE_PAD.clear()
    VIEW_PAD.clear()
    TIMER_PAD.clear()
    IMMIGRANT_INFO_OCCUPATION_PAD.clear()
    for transcript in TRANSCRIPTS:
        IMMIGRANT_INFO_OCCUPATION_PAD.clear()
        IMMIGRANT_INFO_OCCUPATION_PAD.addstr(transcript)
        draw_immigrant_occupation_info_pad()

if __name__ == "__main__":
    wrapper(main)

