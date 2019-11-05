#!/usr/bin/env python3
import curses
from curses import wrapper
from curses.textpad import Textbox, rectangle
from curses import ascii
import time
import random
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer 

CHARACTER_SHOW_DELAY_REGULAR=0.01

sentimentAnalyzer = SentimentIntensityAnalyzer() 


PAIR_RED_ON_WHITE = 1
PAIR_GREEN_ON_WHITE = 2
PAIR_WHITE_ON_BLUE = 3 # selection

INPUT_PAD = None
CHOICES_PAD = None
STDSCR = None
IMMIGRATION_PAD = None
SCORE_PAD = None

# Score is just permanantly drawn
SCORE = 0

sid_obj = SentimentIntensityAnalyzer() 


def draw():
    global INPUT_PAD
    global CHOICES_PAD
    global STDSCR
    global IMMIGRATION_PAD
    global SCORE_PAD

    CHOICES_PAD.refresh(0, 0, 0, 0, 0, 75)
    INPUT_PAD.refresh(0, 0, 1, 0, 1, 75)
    IMMIGRATION_PAD.refresh(0, 0, 2, 0, 2, 75)
    SCORE_PAD.clear()
    SCORE_PAD.addstr("Score: %s" %(SCORE, ))
    SCORE_PAD.refresh(0, 0, 3, 0, 3, 75)

    STDSCR.refresh()


def print_officer_prompt(s):
    global INPUT_PAD
    global CHOICES_PAD
    global STDSCR
    INPUT_PAD.clear()
    INPUT_PAD.addstr('officer: ')
    draw()
    # blob = TextBlob(s)

    words = s.split(' ')
    for i, w in enumerate(words):
        senti = sentimentAnalyzer.polarity_scores(w)
        if senti['neg'] >= 0.1: INPUT_PAD.addstr(w, curses.color_pair(PAIR_RED_ON_WHITE))
        elif senti['pos'] >= 0.1: INPUT_PAD.addstr(w, curses.color_pair(PAIR_GREEN_ON_WHITE))
        else: INPUT_PAD.addstr(w)
        

        draw()
        #for c in w:
        #    pad.addch(0, ord(c))
        if i < len(words)-1: INPUT_PAD.addch(0, ord(' '))


def assert_in_game(b):
    if b: return
    INPUT_PAD.clear()
    CHOICES_PAD.clear()
    SCORE_PAD.clear()

    s = "The immigration center was bombed. There were no survivors"

    for i in range(len(s)+1):
        INPUT_PAD.clear()
        INPUT_PAD.addstr(s[:i])
        draw()
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

def compute_response(i):
    return "response"


def print_immigrant(r):
    global INPUT_PAD
    global CHOICES_PAD
    global STDSCR

    rencoded = TextBlob(r).translate(to='ar')

    for i in range(len(r)+1):
        s = rencoded[:i]
        CHOICES_PAD.clear()
        CHOICES_PAD.addstr("%s" %(s,))
        draw()
        time.sleep(CHARACTER_SHOW_DELAY_REGULAR)


    for i in range(len(r)+1):
        s = r[:i] + str(rencoded[i:])
        CHOICES_PAD.clear()
        CHOICES_PAD.addstr("%s" %(s))
        draw()
        time.sleep(CHARACTER_SHOW_DELAY_REGULAR)


def print_officer(name, out):
    global INPUT_PAD
    global STDSCR

    s = ""
    for c in out:
        s += c
        INPUT_PAD.clear()
        INPUT_PAD.addstr("%s: %s" %(name, s))
        draw()
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
        draw()

        c = STDSCR.getch()
        if c == curses.KEY_RIGHT:
            ix = (ix + 1) % len(choices)
        if c == curses.KEY_LEFT:
            ix = (ix - 1) % len(choices)
        if chr(c) == '\n':
            break

    STDSCR.keypad(0)
    return choices[ix]


def print_immigration_feedback(immigrant_name, choice):
    global IMMIGRATION_PAD
    global STDSCR

    IMMIGRATION_PAD.clear()

    s = ""
    if choice == IMMIGRATION_CHOICE_ENTER:
        s = "%s was let through." % (immigrant_name, )
    elif choice == IMMIGRATION_CHOICE_DEPORT:
        s = "%s was deported." % (immigrant_name, )
    else: # only possible choice is 
        assert_in_game(choice == IMMIGRATION_CHOICE_DETAIN)
        s = "%s was detained." % (immigrant_name, )


    CHOICES_PAD.clear()
    INPUT_PAD.clear()
    for i in range(len(s) + 1):
        IMMIGRATION_PAD.clear()
        IMMIGRATION_PAD.addstr(s[:i])
        draw()
        time.sleep(CHARACTER_SHOW_DELAY_REGULAR)
    time.sleep(1)
    STDSCR.getch()

def update_score(choice):
    pass

def print_immigrant_hello(immigrant_name):
    print_immigrant("hello. My name is " + immigrant_name)

def main(stdscr):
    global INPUT_PAD
    global CHOICES_PAD
    global STDSCR
    global IMMIGRATION_PAD
    global SCORE_PAD

    with open("immigrant_names.txt", "r") as f:
        IMMIGRANT_NAMES = [name.split("\n")[0] for name in f.readlines()]
    random.shuffle(IMMIGRANT_NAMES)


    STDSCR = stdscr
    INPUT_PAD = curses.newpad(1, 80)
    CHOICES_PAD = curses.newpad(1, 80)
    IMMIGRATION_PAD = curses.newpad(1, 80)
    SCORE_PAD = curses.newpad(1, 80)

    # disable input
    STDSCR.keypad(0)

    # Clear screen
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(PAIR_RED_ON_WHITE, curses.COLOR_RED, -1)
    curses.init_pair(PAIR_GREEN_ON_WHITE, curses.COLOR_GREEN, -1)
    curses.init_pair(PAIR_WHITE_ON_BLUE, curses.COLOR_WHITE, curses.COLOR_BLUE)

    STDSCR.clear()
    draw()
    STDSCR.refresh()
    
    for i in range(10):
        immigrant_name = IMMIGRANT_NAMES[0]
        IMMIGRANT_NAMES = IMMIGRANT_NAMES[1:]

        # ask for new immigrant
        CHOICES_PAD.clear()
        IMMIGRATION_PAD.clear()
        draw()
        print_officer("officer", "next, please!")
        time.sleep(0.3)

        # Have immigrant say hello
        print_immigrant_hello(immigrant_name)
        draw()
        
        # Allow for dialogue
        # ==================
        for i in range(3):
            draw()
            i = read_input()

            # Print out output
            r = compute_response(i)
            print_immigrant(r)

        # Provide options
        # ===============
        immigration_choice = read_immigration_choice()

        # Print what happens to them, update score
        print_immigration_feedback(immigrant_name, immigration_choice)
        update_score(immigration_choice)



if __name__ == "__main__":
    wrapper(main)

