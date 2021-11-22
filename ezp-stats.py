#!/usr/bin/env python3
import logging #logging is used to generate a logfile
import os, argparse #os is used for directory navigation, argparse for listening for cli arguments
import yaml #yaml is used to read the config file
from string import Template #used for templating things like the log file name.
from datetime import date, datetime, timedelta

##### Global Variables and definitions Start #####
#open config file safely so it does not allow for code injection, assign it the variable config
with open('config.yml', "r") as f:
	config = yaml.safe_load(f)
#cwd = os.path.sep.join(os.path.abspath(__file__).split(os.path.sep)[:-1]) #Setup Current Working Directory #deleteme maybe? not used?
#look at the config file and fetch the name and location of the diagnostic log file, spulog folder, and output log folder,
if config["flags"]["do_logging"] == True: #check the config file to see if logging is disabled, and disable it if this is the case
	logging.basicConfig(
		filename=config["optional"]["error_log"], 
		encoding='utf-8', 
		format='%(asctime)s %(levelname)-8s %(message)s',
		level=logging.DEBUG,
		datefmt='%Y-%m-%d %H:%M:%S')
else:
	logging.getLogger().disabled = True

spufolder = config["required"]["ezproxy_spulog_folder"]
spu = Template(config["optional"]["spulog_name_scheme"])
outputfolder = config["optional"]["output_folder"]
brandfolder =  config["branding"]["brand_folder"]
#TODO - look at the config spulog naming scheme and set the logfile name variable
##### Global Variables and definitions End #####
logging.debug(f'spu logfolder location: {spufolder}')
#Check folder names from config and create them if they do not exist.
if not os.path.exists(outputfolder):
	os.makedirs(outputfolder)
	logging.debug(f'Output folder created at {outputfolder}')
#Section Listens for any CLI arguments and determines mode to start in
parser = argparse.ArgumentParser(
	formatter_class=argparse.RawDescriptionHelpFormatter, #lets me set the indents and returns for the help description
	#help description, the weird symbols are ANSI escape codes that change the colors of the text
	description='''\
	\033[93mPlease edit the config.yml file before running the script for the first time\033[00m

	This script analyzes EZProxy SPU logs and has multiple modes. 
	==============================================================
	\033[92m*\033[00m If no arguments are specified, it will run stats for the previous month
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

if (args.year and args.month):
    logging.debug("both year and month specified")
    print(spu.substitute(year=args.year.strftime("%Y"), month=args.month.strftime("%m")))
elif args.year:
	#TODO - figure out how whole-year logfile processing will work
	logging.debug("Year specified")
	print("EZproxy_" + args.year.strftime("%Y"))
elif args.month:
	logging.debug("Month specified")
	print(spu.substitue(year=str(datetime.today().replace(day=1) - timedelta(days=1))[0:4], month=args.month.strftime("%m")) #calculates the day, then uses timedelta to move to the last day of the previous month, then I use a string index to specify just the current year minus a month, and append the month from the argument
else:
	logging.debug("No arguments specified")
	print(spu.substitute(year=str(datetime.today().replace(day=1) - timedelta(days=1))[0:4], month=str(datetime.today().replace(day=1) - timedelta(days=1))[5:7]))#calculates the day, then uses timedelta to move to the last day of the previous month, then I use a string index to specify just the year and month out of the timecode and seperate them into individual template values
