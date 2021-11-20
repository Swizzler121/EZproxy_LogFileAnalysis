#!/usr/bin/env python3
import os, argparse #os is used for directory navigation, argparse for listening for cli arguements
from datetime import date, timedelta

##### Global Variables Start #####
#Setup Current Working Directory
cwd = os.path.sep.join(os.path.abspath(__file__).split(os.path.sep)[:-1])

##### Global Variables End #####

#Section reads config file and determines parameters such as if to listen for usernames, where to find log files, etc

####TODO####

#Section Listens for any CLI arguements and determines mode to start in
parser = argparse.ArgumentParser()
parser.add_argument("-y", "--year", help="specify a year to calculate stats from")
parser.add_argument("-m","--month", help="specify a month to calculate stats from")
args = parser.parse_args()
if args.year:
    print("year specified")
#    print("EZproxy_",datetime.date.today().replace(day=1) - datetime.timedelta(days=1))
    print(date.today().month)

#    if len(sys.argv) >= 2: #Counts the number of arguements, currently the script only looks at the 1st arguement after the script, but it won't error out when more are included, it just doesn't pay attention to them.
#        if len(sys.argv[1]) == 2: #check the length of a given argument, if 2 characters are detected,its assumed to be a month
#            print("The script has detected a month")
            #date.month(sys.argv[1]) <--not working
            #print("EZproxy_",sys.argv[1],datetime.today().year)
#        elif len(sys.argv[1]) == 4: #check the length of a given argument, if 4 characters are detected,its assumed to be a year
#            print("the script has detected a year")
#        else
#            print("Invalid arguement detected, please enter a month - MM or a year - YYYY")
#    else: #if no valid argument is detected, run script for last month
#    else
#        print("no arguements were detected or an invalid arguement was detected")
        #print("EZproxy_",datetime.date.today().replace(day=1) - datetime.timedelta(days=1))

#currently fails with no arguement because it throws an out of index error as it's looking for argv 1, look for a better way to handle this
