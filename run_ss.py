#!/usr/bin/env python3
from subprocess import getoutput, call
from time import sleep

# NBoids screensaver launcher, Linux ONLY, requires xprintidle
# This version uses subprocess.call() to launch the screensaver, to avoid memory leak.
# Copyright (c) 2022  Nikolaus Stromberg  github.com/Nikorasu/PyNBoids

SAVERTIME = 900 # How long before the screensaver starts, in seconds

if __name__ == '__main__':
    while True:
        sleep(60)
        idletime = int(getoutput('xprintidle')) / 1000
        if idletime > SAVERTIME: call(['python','nboids_ss.py'])
