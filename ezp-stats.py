#!/usr/bin/env python3
import os # used for directory navigation, folder creation
import logging #logging is used to generate a logfile
import argparse #argparse for listening for cli arguments
import yaml #yaml is used to read the config file
import glob #used for reading and writing files
import csv #used to open and write csv files
from string import Template #used for templating things like the log file name.
from datetime import datetime #only used to interpret arguements as it handles conversion from 1 to 2 digit months better than arrow

import arrow #using arrow for instead of datetime, date, timedelta

#open config file safely so it does not allow for code injection, assign it the variable config
with open('config.yml', "r") as f:
	config = yaml.safe_load(f)
#cwd = os.path.sep.join(os.path.abspath(__file__).split(os.path.sep)[:-1]) #Setup Current Working Directory #deleteme maybe? not used?
#look at the config file and fetch the name and location of the diagnostic log file, spulog folder, and output log folder,
if config["flags"]["do_debug_log"] == True: #check the config file to see if logging is disabled, and disable it if this is the case
	if not config["flags"]["append_debug_log"] == True:
		errorlog = f'{config["optional"]["debug_log"]}{arrow.now()}.log'
	else: 
		errorlog = f'{config["optional"]["debug_log"]}.log'
	logging.basicConfig(
			filename= errorlog, 
			encoding='utf-8', 
			format='%(asctime)s %(levelname)-8s %(message)s',
			level=logging.DEBUG,
			datefmt='%Y-%m-%d %H:%M:%S')
else:
	logging.getLogger().disabled = True
try: #Log wrapper that will record any error exceptions in the log
	spufolder = config["required"]["ezproxy_spulog_folder"]
	logging.debug(f'spu logfolder location: {spufolder}')
	spu = Template(config["optional"]["spulog_name_scheme"])
	outputfolder = config["optional"]["output_folder"]
	brandfolder = config["branding"]["brand_folder"]
	#calculate the previous month
	prevmonth = arrow.now().shift(months=-1)
	#calculate the first month of the year
	first_month = arrow.get(1).replace(year=arrow.now().year)
	#calculate the last month of the year
	last_month = arrow.get(1).replace(year=arrow.now().year).shift(months=-1) 
	start_mo = prevmonth.format('MM')
	start_yr = prevmonth.format('YYYY')
	end_mo = prevmonth.format('MM')
	end_yr = prevmonth.format('YYYY')
	start_end = [start_yr, start_mo, end_yr, end_mo,] #creates a default range of last month to last month, can be modified by other functions, will be expanded into a full range later in the program
	#Check folder names from config and create them if they do not exist.
	if not os.path.exists(outputfolder):
		os.makedirs(outputfolder)
		logging.debug(f'Output folder created at {outputfolder}')
	#Section Listens for any CLI arguments and determines mode to start in
	logging.debug(f'Starting ArgumentParser')
	parser = argparse.ArgumentParser(
			formatter_class=argparse.RawDescriptionHelpFormatter, #lets me set the indents and returns for the help description
			#help description, the weird symbols are ANSI escape codes that change the colors of the text
			description='''\
	\033[93mPlease edit the config.yml file before starting\033[00m

	This program analyzes EZProxy SPU logs and has multiple modes. 
	==========================================================================
	No arguments specified = it will run stats for the previous month
	Only a year is specified = it will run stats for the whole year
	Only a month is specified = it will run stats for that month 
	Both a year and month are specified = it will run for the date specified
	A Month and Year range are specified = It will run for the range specified 

	\033[91mlog file(s) must exist in folder to run stats that range!\033[00m
			''')
	#listen for a year argument and use lambda and strptime to determine if it is a valid year (between 0-9999)
	#parser.add_argument("-y", "--year", type=lambda d: datetime.strptime(d, '%Y'), help="specify a year")
	parser.add_argument(
			"-y", "--year", 
			nargs='+', 
			type=lambda d: arrow.get(d, 'YYYY').format('YYYY'), #uses lambda to determine if a valid year has been input
			help="specify a year"		)
	#listen for a year argument and use lamda and strptime to determine if it is a valid month (between 1-12)
	#parser.add_argument("-m","--month", type=lambda d: datetime.strptime(d, '%m'), help="specify a month (integer)")
	parser.add_argument(
			"-m","--month", 
			nargs='+', 
			#type=lambda d: datetime.strptime(d, '%m') #TODO figure out how to get this working in arrow
			help="specify a month (integer)")
	args = parser.parse_args()
	try:
		if args.year or args.month:
			if len(args.year) <= 1 and args.month == None: #checks if only one year was specified, and if no month was specified
				start = [args.year[0], first_month.format("MM")]
				end = [args.year[0], last_month.format("MM")]
				start_end = [start, end]
			elif len(args.year) == 2 and args.month == None: #checks if 2 years and no month was specified, and assigns variables correctly
				start = f'{args.year[0]}{first_month.format("MM")}'
				end = f'{args.year[1]}{last_month.format("MM")}'
				start_end = [start, end]
			elif len(args.year) <= 1 and len(args.month) <= 1: #checks if one year and one month were specified
				start = args.year[0] + args.month[0]
				start_end = [start] * 2
			elif args.year == None and len(args.month) <= 1:
				start = last_month.format("YYYY") + args.month[0]
				end = last_month.format("YYYY") + args.month[0]
				start_end = [start, end]
			elif args.year == None and len(args.month) == 2:
				start = last_month.format("YYYY") + args.month[0]
				end = last_month.format("YYYY") + args.month[1]
				start_end = [start, end]
			elif len(args.year) == 2 and len(args.month) == 2:
				start = args.year[0] + args.month[0]
				end = args.year[1] + args.month[1]
				start_end = [start, end]
			elif len(args.year) >= 2 or len(args.month) >= 2:
				logging.debug(args)
				raise Exception('too many arguments')
	except Exception as e: # exception code to kill the program if too many arguments are provided
		logging.error(e)
		raise
	#TODO - take the start_end list, pull it's values into a full range, and then use that range to create a list of files to open
	loadedlogfile = spu.substitute(year=start_end[0], month=start_end[1]) #uses arrow to calculate the current time, then subtract a month
	logging.debug(f'loaded the logfile {loadedlogfile}')
	# 	#loadedlogfile = spu.substitute(year=str(datetime.today().replace(day=1) - timedelta(days=1))[0:4], month=str(datetime.today().replace(day=1) - timedelta(days=1))[5:7])#calculates the day, then uses timedelta to move to the last day of the previous month, then I use a string index to specify just the year and month out of the timecode and seperate them into individual template values
	# 	logging.debug(f'loaded the logfile {loadedlogfile}')
	# 	outputfile = f"{config['optional']['output_file_prefix']}{arrow.now().shift(months=-1).format('YYYYMM')}"
	# 	#outputfile = f'{config["optional"]["output_file_prefix"]}{str(datetime.today().replace(day=1) - timedelta(days=1))[0:7].replace("-","")}'
	# 	logging.debug(f'set output file name to {outputfile}')
	# 	open_files = glob.glob(os.path.join())


except Exception as e: #Sends any error exception to the log
    logging.error(e, exc_info=True)
    print(f'\033[91mERROR\033[00m {e} -- Check {errorlog} for more details')