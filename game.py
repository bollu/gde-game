#!/usr/bin/env python3
import curses
from curses import wrapper
from curses.textpad import Textbox, rectangle
from curses import ascii

def print_prompt(pad, s):
    pad.clear()
    pad.addch(0, ord('>'))
    for c in s:
        pad.addch(0, ord(c))

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
    stdscr.clear()
    stdscr.refresh()


    # Take in input
    # =============

    i = read_input(stdscr, input_pad)




if __name__ == "__main__":
    wrapper(main)


