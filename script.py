#!/usr/bin/env python

import io
import datetime
import re
import copy
from userSettings import maxAttempts, timeAllowed

class Client:
    """
    Client

    A class used to keep track of ssh attempt information.

    Attributes:
        ip (str): The ip of the client that failed an attempt.
        timeStamps (str[]): A list of timestamps of all the different attempts in order.
    """
    def __init__(self, ip=''):
        self.ip = ip
        self.timeStamps = []

    # adds a timestamp
    def addTime(self, time):
        self.timeStamps.append(time)

    def addTimes(self, times):
        self.timeStamps = copy.deepcopy(times)

    # calculates time between the earliest attempt and the latest attempt
    def calcTimeBetween(self):
        last = get_sec(self.timeStamps[len(self.timeStamps) - 1])
        first = get_sec(self.timeStamps[0])
        return abs(last - first)


    # calculates time between the earliest attempt and the latest attempt
    def calcBan(self):
        banned = False
        if len(self.timeStamps) >= maxAttempts:
            for x in range(0, len(self.timeStamps)):
                if (x + maxAttempts) < len(self.timeStamps):
                    last = get_sec(self.timeStamps[x + maxAttempts])
                    first = get_sec(self.timeStamps[x])
                    timeCalc = abs(last - first)
                    if timeCalc < timeAllowed:
                        banned = True
        return banned

    # returns all the timestamps
    def getTimes(self):
        out = ''
        for x in self.timeStamps:
            out += ('{},'.format(x))
        return out

    def getAttempts(self):
        return len(self.timeStamps)

def get_sec(time_str):
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)

def read_ipCount(f_count):
    for line in f_count:
        i = (len(ip_dict) - 1)
        buf = line.split(',')
        ip = buf.pop(0)
        print(ip)
        new = Client(ip)
        if ip not in ip_dict:
            ip_dict[ip] = i
            clientList.append(new)
            clientList[i].addTimes(buf)

def write_to_log(f_log):
    for c in clientList:
        f_log.write(c.ip + ',' + c.getTimes() + '\n')

def exportSinceRead(f_timer):
    f_timer.write(str(currentDT.year) + "-" + str(currentDT.month) + "-" + str(currentDT.day) + " " + str(currentDT.hour) + ":" + str(currentDT.minute) + ":" + str(currentDT.second) + "\n")

def read_sshLog(f_ssh):
    """
    read_sshLog

    A function used to convert logs into readable objects

    Args:
        f_ssh (file): the file object to write to.
    """
    i = 0
    for line in f_ssh.readlines():
        buf = line
        if "Failed" in buf:
            ip = re.findall(r'[0-9]+(?:\.[0-9]+){3}', buf)[0]
            time_stamp = re.findall(r'((2[0-3]|[01][0-9]):[0-5][0-9]:[0-5][0-9])', buf)[0][0]
            new = Client(ip)
            if ip not in ip_dict:
                ip_dict[ip] = i
                clientList.append(new)
                clientList[i].addTime(time_stamp)
                i += 1
            else:
                clientList[ip_dict[ip]].addTime(time_stamp)

def banSweep():
    for c in clientList:
        if c.calcBan():
            banList.append(c)

def exportBanList(f_banned):
    for x in banList:
        f_banned.write(str(x) + " " + str(currentDT.year) + "-" + str(currentDT.month) + "-" + str(currentDT.day) + " " + str(currentDT.hour) + ":" + str(currentDT.minute) + ":" + str(currentDT.second) + "\n")

# record time since read to split what was checked
currentDT = datetime.datetime.now()

# lists and dictionaries
ip_dict = {}
clientList = []
banList = []

# sshd log file
f = open("sshd.log", "r")
f_timer = open("sinceTime.txt", "w")
f_logs = open("ipCounter.txt", "w+")
f_banned = open("bannedIps.txt", "w+")

exportSinceRead(f_timer)
read_sshLog(f)
read_ipCount(f_logs)
write_to_log(f_logs)
banSweep()
exportBanList(f_banned)

print("map: {}".format(ip_dict))
print("banList: {}".format(banList))
