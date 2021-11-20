#!/usr/bin/env python3
import os, sys #os is used for directory navigation, sys for listening for cli arguements
import datetime # import date, datetime, timedelta

##### Global Variables Start #####
#Setup Current Working Directory
cwd = os.path.sep.join(os.path.abspath(__file__).split(os.path.sep)[:-1])
##### Global Variables End #####

#Listen for cli arguements to decide mode to start in
if len(sys.argv[1]) == 2: #check the length of a given argument, if 2 characters are detected,its assumed to be a month
	print("The script has detected a month")
	#date.month(sys.argv[1]) <--not working
	#print("EZproxy_",sys.argv[1],datetime.today().year)
elif len(sys.argv[1]) == 4: #check the length of a given argument, if 4 characters are detected,its assumed to be a year
	print("the script has detected a year")
else: #if no valid argument is detected, run script for last month
	print("no arguements were detected or an invalid arguement was detected")
	#print("EZproxy_",datetime.date.today().replace(day=1) - datetime.timedelta(days=1))

#currently fails with no arguement because it throws an out of index error as it's looking for argv 1, look for a better way to handle this
