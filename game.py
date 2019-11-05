#!/usr/bin/env python3
import curses
from curses import wrapper
from curses.textpad import Textbox, rectangle
from curses import ascii
import time
# from textblob import TextBlob
# from textblob.sentiments import NaiveBayesAnalyzer
# from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer 



PAIR_RED_ON_WHITE = 1
PAIR_GREEN_ON_WHITE = 2
PAIR_WHITE_ON_BLUE = 3 # selection

INPUT_PAD = None
RESPONSE_PAD = None
STDSCR = None
IMMIGRATION_PAD = None
SCORE_PAD = None

# Score is just permanantly drawn
SCORE = 0


def draw():
    global INPUT_PAD
    global RESPONSE_PAD
    global STDSCR
    global IMMIGRATION_PAD
    global SCORE_PAD

    RESPONSE_PAD.refresh(0, 0, 0, 0, 0, 75)
    INPUT_PAD.refresh(0, 0, 1, 0, 1, 75)
    IMMIGRATION_PAD.refresh(0, 0, 2, 0, 2, 75)
    SCORE_PAD.clear()
    SCORE_PAD.addstr("Score: %s" %(SCORE, ))
    SCORE_PAD.refresh(0, 0, 3, 0, 3, 75)

    STDSCR.refresh()

def print_prompt(s):
    global INPUT_PAD
    global RESPONSE_PAD
    global STDSCR
    INPUT_PAD.clear()
    INPUT_PAD.addstr('officer: ')
    draw()
    # blob = TextBlob(s)

    words = s.split(' ')
    for i, w in enumerate(words):
        # senti = sid_obj.polarity_scores(w)
        # if senti['neg'] >= 0.5: pad.addstr(w, curses.color_pair(PAIR_RED_ON_WHITE))
        # elif senti['pos'] >= 0.5: pad.addstr(w, curses.color_pair(PAIR_GREEN_ON_WHITE))
        # else: pad.addstr(w)
        

        # pad.addstr(w, curses.COLOR_RED)
        INPUT_PAD.addstr(w)
        draw()
        #for c in w:
        #    pad.addch(0, ord(c))
        if i < len(words)-1: INPUT_PAD.addch(0, ord(' '))

def read_input():
    global INPUT_PAD
    global RESPONSE_PAD
    global STDSCR
    # stdscr.refresh()
    s = ""
    while True:
        if s == "":
            print_prompt("(Type to respond)")
        else:
            print_prompt(s)
        c = STDSCR.getch()
        if c == curses.KEY_BACKSPACE:
            s = s[:-1]
        elif c == curses.KEY_ENTER or chr(c) == '\n':
            return s
        else:
            s += chr(c)
        # stdscr.refresh()

def compute_response(i):
    return "response"


def print_immigrant(name, r):
    global INPUT_PAD
    global RESPONSE_PAD
    global STDSCR

    s = ""
    for c in r:
        s += c
        RESPONSE_PAD.clear()
        RESPONSE_PAD.addstr("%s: %s" %(name, s))
        draw()
        time.sleep(1e-2)


IMMIGRATION_CHOICE_ENTER = 'ENTER'
IMMIGRATION_CHOICE_DEPORT = 'DEPORT'
IMMIGRATION_CHOICE_DETAIN = 'DETAIN'

def read_immigration():
    """Read the input of the immigration status that we want to provide them"""
    global IMMIGRATION_PAD
    global STDSCR
    choices = [IMMIGRATION_CHOICE_ENTER, IMMIGRATION_CHOICE_DEPORT, IMMIGRATION_CHOICE_DETAIN]
    ix = 0 



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
            return choices[i]


def print_immigration_feedback(choice):
    pass

def update_score(choice):
    pass

def print_immigrant_hello():
    print_immigrant("foo", "hello. My name is foo")

def main(stdscr):
    global INPUT_PAD
    global RESPONSE_PAD
    global STDSCR
    global IMMIGRATION_PAD
    global SCORE_PAD

    STDSCR = stdscr
    INPUT_PAD = curses.newpad(1, 80)
    RESPONSE_PAD = curses.newpad(1, 80)
    IMMIGRATION_PAD = curses.newpad(1, 80)
    SCORE_PAD = curses.newpad(1, 80)

    # Clear screen
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(PAIR_RED_ON_WHITE, curses.COLOR_RED, -1)
    curses.init_pair(PAIR_GREEN_ON_WHITE, curses.COLOR_GREEN, -1)
    curses.init_pair(PAIR_WHITE_ON_BLUE, curses.COLOR_WHITE, curses.COLOR_BLUE)

    # for i in range(0, curses.COLORS):
    #     curses.init_pair(i + 1, i, -1)
    STDSCR.clear()
    draw()
    STDSCR.refresh()


    print_immigrant_hello()
    draw()
    
    # Allow for dialogue
    # ==================
    for i in range(3):
        draw()


        i = read_input()

        # Print out output
        r = compute_response(i)
        print_immigrant("sid", r)

    # Provide options
    # ===============
    immigration_status = read_immigration()

    # Print what happens to them, update score
    print_immigration_feedback(immigration_status)
    update_score(immigration_status)



if __name__ == "__main__":
    wrapper(main)

