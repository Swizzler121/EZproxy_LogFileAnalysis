#!/usr/bin/env python3

#DELETEME - Review and remove line if no longer needed.
#TODO - Incomplete code that needs to be finished.

# os is used for directory navigation and folder creation.
# logging is used for logfiles and errors.
# argparse is for listening for Command Line Interface arguments.
# yaml is used to read the .yml config file.
# csv is used to read and write csv files.
# Template is used for templating filenames.
# datetime is only used to validate dates on arguments DELETEME
import os
import logging
import argparse
import yaml
import csv
from string import Template
#from datetime import datetime #DELETEME

# arrow is a drop-in replacement for datetime, date, and timedelta.
# pandas is used for data processing in data frames (PDF generation).
import arrow
import pandas as pd

# Open config file safely so it does not allow for code injection, and
# assign it the variable config so it can be called later.
with open('config.yml', "r") as f:
	config = yaml.safe_load(f)

# Check the config file to see if logging is disabled, and disable it
# if this is the case. Look at the config file and fetch the name and 
# location of the debug log file, and assign that name scheme.
if config["flags"]["do_debug_log"] == True:
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
# Log wrapper that will record any error exceptions in the log.
try:
	spufolder = config["required"]["ezproxy_spulog_folder"]
	logging.debug(f'spu logfolder location: {spufolder}')
	spu = Template(config["optional"]["spulog_name_scheme"])
	outputfileprefix = config["optional"]["output_file_prefix"]
	outputfolder = config["optional"]["output_folder"]
	# Calculate the previous month.
	prevmonth = arrow.now().shift(months=-1)
	# Calculate the first month of the year.
	first_month = arrow.get(1).replace(year=arrow.now().year)
	# Calculate the last month of the year.
	last_month = arrow.get(1).replace(year=arrow.now().year).shift(months=-1)
	# Creates a default range of last month to last month, can be
	# modified by other functions, will be expanded into a full 
	# range later in the program.
	start_end = [prevmonth, prevmonth] 
	#Check folder names from config and create them if they do not exist.
	if not os.path.exists(outputfolder):
		os.makedirs(outputfolder)
		logging.debug(f'Output folder created at {outputfolder}')
	#Section Listens for any CLI arguments and determines mode.
	logging.debug(f'Starting ArgumentParser')
	parser = argparse.ArgumentParser(
			# Allows for custom indents and returns for the description.
			formatter_class=argparse.RawDescriptionHelpFormatter,
			# Help description, the weird symbols are ANSI escape codes
			# that change the colors of the text.
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
	# Listen for a year argument and use lambda and strptime to 
	# determine if it is a valid year (between 0-9999).
	#parser.add_argument("-y", "--year", type=lambda d: datetime.strptime(d, '%Y'), help="specify a year") #DELETEME
	parser.add_argument(
			"-y", "--year", 
			nargs='+', 
			# Uses lambda to determine if a valid year has been input.
			type=lambda d: arrow.get(d, 'YYYY').format('YYYY'),
			help="specify a year"		)
	# Listen for a year argument and use lamda and strptime to 
	# determine if it is a valid month (between 1-12).
	#parser.add_argument("-m","--month", type=lambda d: datetime.strptime(d, '%m'), help="specify a month (integer)") #DELETEME
	parser.add_argument(
			"-m","--month", 
			nargs='+', 
			type=lambda d: arrow.get(d, 'MM').format('MM'), #TODO figure out how to convert 1 digit numbers and 3 char months into 2 digit months
			help="specify a month (integer)")
	args = parser.parse_args()
	try:
		# Checks to run if at least one year was specified,
		# and if no months were specified.
		if args.year is not None and args.month is None:
			if len(args.year) <= 1 and args.month is None: 
				start = arrow.get(first_month).replace(year=int(args.year[0]))
				end = arrow.get(last_month).replace(year=int(args.year[0]))
				start_end = [start, end]
			elif len(args.year) == 2 and args.month is None: 
				start = arrow.get(first_month).replace(year=int(args.year[0]))
				end = arrow.get(last_month).replace(year=int(args.year[1]))
				start_end = [start, end]
		# Checks to run if at least one month was specified,
		# and no years were specified.
		if args.month is not None and args.year is None:
			if len(args.month) <= 1 and args.year is None:
				start = arrow.get(prevmonth).replace(month=int(args.month[0]))
				start_end = [start] * 2
			elif len(args.month) == 2 and args.year is None:
				start = arrow.get(prevmonth).replace(month=int(args.month[0]))
				end = arrow.get(prevmonth).replace(month=int(args.month[1]))
				start_end = [start, end]
		# Checks to run if at least one month and
		# one year were specified.
		if args.month and args.year is not None:
			if len(args.year) <= 1 and len(args.month) <= 1: 
				start = arrow.get().replace(
											year=int(args.year[0]), 
											month=int(args.month[0])
											)
				start_end = [start] * 2
			elif len(args.year) == 1 and len(args.month) == 2:
				start = arrow.get().replace(
											year=int(args.year[0]), 
											month=int(args.month[0])
											)
				end = arrow.get().replace(
											year=int(args.year[0]), 
											month=int(args.month[1])
											)
				start_end = [start, end]
			elif len(args.year) == 2 and len(args.month) == 1:
				start = arrow.get().replace(
											year=int(args.year[0]), 
											month=int(args.month[0])
											)
				end = arrow.get().replace(
											year=int(args.year[1]), 
											month=int(args.month[0])
											)
				start_end = [start, end]
			elif len(args.year) == 2 and len(args.month) == 2:
				start = arrow.get().replace(
											year=int(args.year[0]), 
											month=int(args.month[0])
											)
				end = arrow.get().replace(
											year=int(args.year[1]), 
											month=int(args.month[1])
											)
				start_end = [start, end]
			# Checks if there are 3 or more arguments for month or
			# year and kills program if there is.
			elif len(args.year) >= 2 or len(args.month) >= 2:
				logging.debug(args)
				raise ValueError('too many arguments')
	except ValueError as e:
		logging.error(e)
		raise
	# Take the start and end dates, and create a range of dates by
	# iterating monthly from the start to the end date, then formats
	# the dates as YYYYMM in the spu Template from the config.
	filenames = []
	for r in arrow.Arrow.range('month', start_end[0], start_end[1]):
		filenames.append(os.path.sep.join([
										spufolder, 
										spu.substitute(
											year=r.format("YYYY"), 
											month=r.format("MM")
											)
										]))
		logging.debug(f'''Loaded file: {os.path.sep.join([
												spufolder, 
												spu.substitute(
													year=r.format("YYYY"), 
													month=r.format("MM")
													)
												])
										}''')
	# Check if the range is only one month, and if it is, make the 
	# date only appear once, else, use both dates.
	if start_end[0] == start_end[1]:
		csvoutput = os.path.sep.join([
									outputfolder,
									outputfileprefix
								  + "_"
								  + start_end[0].format("YYYYMM")
								  + ".csv"
								  	])
	else:
		csvoutput = os.path.sep.join([
									outputfolder,
									outputfileprefix
								  + "_"
								  + start_end[0].format("YYYYMM")
								  + "_"
								  + start_end[1].format("YYYYMM")
								  + ".csv"
								  	])
	# Set active output file to csvoutput (specified in config)
	# and opens it to write.
	output = open(csvoutput,'w')
	# Checks if extended dates seprate date, weekday, and hour are
	# enabled, if not, it deletes those keys from the dictionary.
	if config["csv_flags"]["do_extended_dates"] is not True:
		config["columns"].pop('date1')
		config["columns"].pop('date2')
	
	# Checks if spaced category names are enabled, and if so it pulls
	# the dictionary values from the config instead of the keys.
	if config["csv_flags"]["do_spaced_categories"] is True:
		db_value_list = list(config["columns"].values())
	else:
		db_value_list = list(config["columns"].keys())
	# Writes the resulting dictionary (either values or keys
	# depending on config) to the first row of the CSV file.
	output.write(','.join(db_value_list))
	
	# Loads the logfile via filenames variable and iterates through
	# it, assigning each line to a variable as it goes
	for file in filenames:
		with open(file) as f:
			lines = [line.strip() for line in f]
			for line in lines:
				l = line.split()
				l_saddr = l[0]
				l_date = arrow.get(
								' '.join(l[1:3]).strip('[]'),
								'DD/MMM/YYYY:HH:mm:ss Z'
								)
				l_usern = l[3]
				l_daddr = l[5]
				l_local = l[6]

				# Checks if do_resource_csv is enabled, and if so
				# loads the resource CSV file and compares each 
				# rows url with the resource CSV and applies the
				# prettier name to the line.
				if config["csv_flags"]["do_resource_csv"] is True:
					db_names = {}
					with open(config["csv"]["resource_csv"]) as csv_r:
						reader = csv.reader(csv_r)
						for row in reader:
							a, b = row
							db_names[a] = b
							db_list = list(db_names.keys())
						for x in db_list:
							if x in l_daddr:
								l_daddr = db_names[x]
				# Advances to the next row, occurs every line.
				output.write('\n')
				# Writes one line of data to the CSV.
				# Checks if do_extended_dates is true, if so it
				# formats the date entry 3 times to the predetermined
				# Date types and places them in the correct column.
				if config["csv_flags"]["do_extended_dates"] is True:
					output.write(
							str(l_date.format("YYYY-MM-DD"))
						  + ","
						  + str(l_date.format("dddd"))
						  + ","
						  + str(l_date.format("HH"))
						  + ","
						  + str(l_usern)
						  + ","
						  + str(l_saddr)
						  + ","
						  + str(l_daddr)
						  + ","
						  + str(l_local)
							)
				else:
					output.write(
							str(l_date)
						  + ","
						  + str(l_usern)
						  + ","
						  + str(l_saddr)
						  + ","
						  + str(l_daddr)
						  + ","
						  + str(l_local)
							)
	# Closes the output CSV file
	output.close()

except Exception as e: #Sends any error exception to the log
    logging.error(e, exc_info=True)
    print(f'\033[91mERROR\033[00m {e} -- Check {errorlog} for more details')
