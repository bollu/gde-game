#!/usr/bin/env python3
import curses
from curses import wrapper
from curses.textpad import Textbox, rectangle
from curses import ascii
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer 



PAIR_RED_ON_WHITE = 1
PAIR_GREEN_ON_WHITE = 2

sid_obj = SentimentIntensityAnalyzer() 


def print_prompt(pad, s):
    pad.clear()
    pad.addch(0, ord('>'))
    blob = TextBlob(s)

    words = s.split(' ')
    for i, w in enumerate(words):
        senti = sid_obj.polarity_scores(w)
        if senti['neg'] >= 0.5: pad.addstr(w, curses.color_pair(PAIR_RED_ON_WHITE))
        elif senti['pos'] >= 0.5: pad.addstr(w, curses.color_pair(PAIR_GREEN_ON_WHITE))
        else: pad.addstr(w)
        
        # pad.addstr(w)
        # pad.addstr(w, curses.COLOR_RED)
        # pad.addstr(w, 1)
        #for c in w:
        #    pad.addch(0, ord(c))
        if i < len(words)-1: pad.addch(0, ord(' '))

    pad.addch(0, ord('_'))

def read_input(stdscr, input_pad):

    stdscr.refresh()
    s = ""
    print_prompt(input_pad, s)
    while True:
        c = stdscr.getch()
        if c == curses.KEY_BACKSPACE:
            s = s[:-1]
        elif c == curses.KEY_ENTER:
            break
        else:
            s += chr(c)

        print_prompt(input_pad, s)
        input_pad.refresh(0,0, 0, 0, 20, 75)
        stdscr.refresh()

def main(stdscr):
    input_pad = curses.newpad(100, 100)

    # Clear screen
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(PAIR_RED_ON_WHITE, curses.COLOR_RED, -1)
    curses.init_pair(PAIR_GREEN_ON_WHITE, curses.COLOR_GREEN, -1)

    # for i in range(0, curses.COLORS):
    #     curses.init_pair(i + 1, i, -1)
    stdscr.clear()
    stdscr.refresh()


    # Take in input
    # =============

    i = read_input(stdscr, input_pad)




if __name__ == "__main__":
    wrapper(main)


