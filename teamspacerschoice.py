#!/usr/bin/env python3
import sys
import os
import getopt
import subprocess
from crontab import CronTab
from random import randint
from datetime import datetime

def printHelp():
    print("\nAbout:\tTeamspacerschoice can be executed (without options) to schedule a single non-recurring Groundbreaker.py job. Jobs are only scheduled M-TR 10AM-4PM, F 12PM-4PM.")
    print("\nOptional:")
    print("-c | --cron\tCreate a cron job at Friday 12:00PM to run Teamspacerschoice to schedule Groundbreaker.py")
    print("-s | --show\tShow jobs scheduled (including non-Teamspacerschoice jobs)")
    print("-r | --remove\tRemove scheduled jobs specified by job ID")
    print("-h | --help\tPrints this help message you see before you")
    exit()

def createCron():
    path = os.path.abspath(__file__)
    tsc_cron = CronTab(user=os.getlogin())
    job = tsc_cron.new(command="%s %s" % ('$(which python3)', path), comment="Teamspaceschoice weekly scheduler")
    job.setall('0 12 * * 5')
    tsc_cron.write()

def main(argv):

    try:
        opts,args = getopt.getopt(sys.argv[1:], 'chsr:',['remove=', 'r='])
    except Exception as err_msg:
        print(err_msg)
        exit()
    for opt,arg in opts:
        if opt in ('-c', '--cron'):
            #create cron job for Fridays 12pm
            createCron()
        elif opt in ('-h', '--help'):
            printHelp()
        elif opt in ('-s', '--show'):
            print(subprocess.getoutput("atq"))
            exit()
        elif opt in ('-r', '--remove'):
            if len(arg) == 0:
                jobID = input("Input Job ID to remove: ")
            else:
                jobID = arg.strip(' "\'\t\r\n')
            print(subprocess.getoutput("atrm %s" % jobID))
            print("Removed job %s" % jobID)
            print(subprocess.getoutput("atq"))
            exit()

    day = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']

    selectDate = day[randint(0, len(day)-1)]

    if 'friday' in selectDate:
        shour = 12
    else:
        shour = 10
    hour = randint(shour,16)
    
    if 16 == hour:
        emin = 00
    else:
        emin = 59
    minute = randint(0,emin)
    minute = "{:0>2d}".format(minute)    
    timeFormat = datetime.strptime("%s:%s" % (hour, minute), "%H:%M")
    print(timeFormat.strftime("%I:%M %p"), selectDate)

    atjob = subprocess.getoutput("echo 'groundbreaker.py' | at %s %s" % (timeFormat.strftime("%I:%M %p"), selectDate))
    print(atjob)
    exit()

if __name__=="__main__":
    main(sys.argv[1:])
