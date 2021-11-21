#!/usr/bin/env python3
import os, argparse #os is used for directory navigation, argparse for listening for cli arguements
import yaml #yaml is used to read the config file
from datetime import date, datetime, timedelta

##### Global Variables and definitions Start #####
#open config file safely so it does not allow for code injection, assign it the variable config
with open('config.yml', "r") as f:
	config = yaml.safe_load(f)
#Setup Current Working Directory
cwd = os.path.sep.join(os.path.abspath(__file__).split(os.path.sep)[:-1])
spufolder = config["required"]["EZProxyLogFolderName"] #look at the config file and fetch the name of the log folder assign it to a variable
##### Global Variables and definitions End #####

#Section Listens for any CLI arguements and determines mode to start in
parser = argparse.ArgumentParser(
	formatter_class=argparse.RawDescriptionHelpFormatter, #lets me set the indents and returns for the help description
	#help description, the weird symbols are ANSI escape codes that change the colors of the text
	description='''\
	\033[93mPlease edit the config.ini file before running the script for the first time\033[00m

	This script analyzes EZProxy SPU logs and has multiple modes. 
	==============================================================
	\033[92m*\033[00m If no arguements are specified, it will run stats for the previous month
	\033[92m*\033[00m If only a year is specified, it will run stats for the whole year
	\033[92m*\033[00m If only a month is specified, it will run stats for that month 
	\033[92m*\033[00m If both a year and month are specified, it will run for the date specified. 

\033[91m	Corresponding SPU log file(s) must exist in the EZProxy log folder to run stats for a time period!\033[00m
		''')
#listen for a year argument and use lambda and strptime to determine if it is a valid year (between 0-9999)
parser.add_argument("-y", "--year", type=lambda d: datetime.strptime(d, '%Y'), help="specify a year")
#listen for a year argument and use lamda and strptime to determine if it is a valid month (between 1-12)
parser.add_argument("-m","--month", type=lambda d: datetime.strptime(d, '%m'), help="specify a month (integer)")
args = parser.parse_args()

print (spufolder)

if args.year:
    print("year specified")
    print("EZproxy_" + args.year.strftime("%Y"))
#    print("EZproxy_",datetime.date.today().replace(day=1) - datetime.timedelta(days=1))
    print(date.today().month) #just messing with how to count back a month
elif args.month:
	print("Month specified")
	print("EZproxy_" + args.month.strftime("%m"))
