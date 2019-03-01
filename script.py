#!/usr/bin/env python

import io
import datetime
import re

# record time since read to split what was checked
currentDT = datetime.datetime.now()

def findOccurrence(a1, mmap):
    for i in mmap:
        i == a1


# ip dictionary
ip_dict = {}
ip_set = []

# sshd log file
f = open("sshd.log", "r")
f_settings = open("settings.txt", "r")
f_timer = open("timeSinceRead.txt", "w")
f_logs = open("ipCounter.txt", "w")

f_timer.write(str(currentDT.year) + "-" + str(currentDT.month) + "-" + str(currentDT.day) + " " + str(currentDT.hour) + ":" + str(currentDT.minute) + ":" + str(currentDT.second))

repeatFail = []

for line in f.readlines():
    buf = line
    if "Failed" in buf:
        ip = re.findall( r'[0-9]+(?:\.[0-9]+){3}', buf)
        ip_dict = {ip[0], 0}

        i = ip_dict[ip[0]]
        i += 1
        ip_dict[ip[0]] = i

        # print("map: {}".format(ip_dict))
        print buf
        f_logs.write(str(ip[0]) + "\n")
