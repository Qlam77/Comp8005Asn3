#!/usr/bin/bash

sshdLogFile="/home/foo/Asn3/sshd.log"
lastCheckedFile="/home/foo/Asn3/timeSinceRead.txt"

# Exports log file with from last check time
function exportSinceLog()
{
    while IFS="\r\n" read time;
    do
        #do action based on input of time checked and pipe to file
        journalctl -r -u sshd -S "${time}"| egrep 'Failed|Accepted' > ${sshdLogFile}
    done < "${lastCheckedFile}"
}

# Exports log file without a last check time
function exportNewLog()
{
    journalctl -r -u sshd | egrep 'Failed|Accepted' > ${sshdLogFile}
}

# Checks log file to see if there existed a last check
function checkLog()
{
    if [ -s "${lastCheckedFile}" ]
    then
        exportSinceLog
    else
        exportNewLog
    fi
}

checkLog
./script.py
