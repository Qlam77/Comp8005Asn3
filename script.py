#!/usr/bin/env python

import io
import datetime
import re

# record time since read to split what was checked
currentDT = datetime.datetime.now()

def get_sec(time_str):
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)

class client:
    def __init__(self, ip='', attempts=0):
        self.ip = ip
        self.attempts = attempts
        self.timeStamps = []
    
    # adds a timestamp
    def addTime(self, time):
        self.timeStamps.append(time)
    
    # calculates time between the earliest attempt and the latest attempt
    def calcTimeBetween(self):
        last = self.timeStamps[len(self.timeStamps) - 1]
        first = self.timeStamps[0]
        return last - first

    # attempts incrementer
    def incAttempt(self):
        self.attempts += 1
        return self.attempts
    
    # prints out all the timestamps
    def printTimes(self):
        for x in self.timeStamps:
            print(x)

maxAttempts = 3
# in seconds
timeAllowed = 10

# ip dictionary
ip_dict = {}
clientList = []
banList = []

# sshd log file
f = open("sshd.log", "r")
f_settings = open("settings.txt", "r")
f_timer = open("timeSinceRead.txt", "w")
f_logs = open("ipCounter.txt", "a+")

f_timer.write(str(currentDT.year) + "-" + str(currentDT.month) + "-" + str(currentDT.day) + " " + str(currentDT.hour) + ":" + str(currentDT.minute) + ":" + str(currentDT.second))

repeatFail = []

for line in f.readlines():
    i = 0
    buf = line
    if "Failed" in buf:
        ip = re.findall(r'[0-9]+(?:\.[0-9]+){3}', buf)[0]
        time_stamp = re.findall(r'((2[0-3]|[01][0-9]):[0-5][0-9]:[0-5][0-9])', buf)[0][0]
        new = client(ip[0], 1)
        if ip not in ip_dict:
            ip_dict[ip] = i
            clientList.append(new)
            print(time_stamp)
            clientList[i].addTime(get_sec(time_stamp))
        else:
            attempts = clientList[ip_dict[ip]].incAttempt()
            clientList[ip_dict[ip]].addTime(time_stamp)

for x in clientList:
    if x.attempts >= maxAttempts:
        print("Over attempt limit!")
        if x.calcTimeBetween() >= timeAllowed:
            print("Too short in between requests!")
            banList.append(x.ip)

print("map: {}".format(ip_dict))
print("banList: {}".format(banList))