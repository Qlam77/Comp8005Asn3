#!/usr/bin/bash

sshdLogFile="/home/foo/Asn3/sshd.log"
lastCheckedFile="/home/foo/Asn3/sinceTime.txt"
banList="/home/foo/Asn3/bannedIps.txt"
currentlyBanned="/home/foo/Asn3/currentlyBanned.txt"
tmpBanFile="/home/foo/Asn3/tmpBanFile.txt"
banTimer=20

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

function banFromList()
{
    while IFS="\r\n" read ipToBan;
    do
        #do action based on input of time checked and pipe to file
        IFS=' ' read ip timeSinceBan<<< "${ipToBan}"
        iptables -A INPUT -s ${ip} -j DROP
        iptables -A INPUT -d ${ip} -j DROP
        iptables -A OUTPUT -s ${ip} -j DROP
        iptables -A OUTPUT -d ${ip} -j DROP
        echo "${ip} ${timeSinceBan}" >> ${currentlyBanned}
    done < "${banList}"

    #clears ban list since they are all processed
    rm "${banList}"

    #remakes it for next time
    touch "${banList}"
}

function unBanFromList()
{
    #makes temp file for ban processing
    touch "${tmpBanFile}"
    while IFS="\r\n" read ipToBan;
    do
        #do action based on input of time checked and pipe to file
        IFS=' ' read ip timeSinceBan<<< "${ipToBan}"
        # echo "ip: ${ip}"
        ipToBanTimer="$(date +%s -d "${timeSinceBan}")"
        curTimeSinceEpoch="$(date +%s)"

        z="$(expr $curTimeSinceEpoch - $ipToBanTimer)"
        z=${z#-}

        #un ban them if they are over time limit
        if [ "$z" -ge "$banTimer" ];
        then
            iptables -D INPUT -s ${ip} -j DROP
            iptables -D INPUT -d ${ip} -j DROP
            iptables -D OUTPUT -s ${ip} -j DROP
            iptables -D OUTPUT -d ${ip} -j DROP
        fi

        #move to a tmp ban file for further processing later
        if [ "$z" -lt "$banTimer" ];
        then
            echo "${ip} ${timeSinceBan}" >> "${tmpBanFile}"
        fi
    done < "${currentlyBanned}"

    cp ${tmpBanFile} ${currentlyBanned}

    rm ${tmpBanFile}
}

function clearMe()
{
    ip=25.67.176.150
    iptables -D INPUT -s ${ip} -j DROP
    iptables -D INPUT -d ${ip} -j DROP
    iptables -D OUTPUT -s ${ip} -j DROP
    iptables -D OUTPUT -d ${ip} -j DROP
}

#Main
# clearMe
unBanFromList
checkLog
./script.py
banFromList
