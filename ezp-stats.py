#!/usr/bin/env python3

#DELETEME - Review and remove line if no longer needed.
#TODO - Incomplete code that needs to be finished.

# os is used for directory navigation and folder creation.
# logging is used for logfiles and errors.
# argparse is for listening for Command Line Interface arguments.
# yaml is used to read the .yml config file.
# csv is used to read and write csv files.
# collections is used for the namedtuple function.
# Template is used for templating filenames.
# datetime is only used to validate dates on arguments DELETEME
import os
import logging
import argparse
import yaml
import csv
import collections as coll
from string import Template
#from datetime import datetime #DELETEME

# arrow is a drop-in replacement for datetime, date, and timedelta.
# pandas is used for data processing in data frames (PDF generation).
# matplotlib plt is used to plot data
# matplotlib PdfPages is used for multipage PDFs
# matplotlib Polygon is used to draw objects
# svgutils is used to render SVGs for PDFs
import arrow
import pandas as pd
import numpy as np
# from IPython.display import HTML

import matplotlib.pyplot as plt
# from matplotlib.backends.backend_pdf import PdfPages #DELETEME
#from matplotlib.patches import Polygon # Might use later for drawing polygons

# Open config file safely so it does not allow for code injection, and
# assign it the variable config so it can be called later.
with open('config.yml', "r") as cfg:
	config = yaml.safe_load(cfg)

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
		datefmt='%Y-%m-%d %H:%M:%S'
	)
else:
	logging.getLogger().disabled = True
# Log wrapper that will record any error exceptions in the log.
try:
	spufolder = config["required"]["ezproxy_spulog_folder"]
	logging.debug(f'spu logfolder location: {spufolder}')
	spu = Template(config["optional"]["spulog_name_scheme"])
	out_file_prefix = config["optional"]["output_file_prefix"]
	outputfolder = config["optional"]["output_folder"]
	# Checks if spaced category names are enabled, and if so it pulls
	# the dictionary values from the config instead of the keys.
	if config["csv_flags"]["do_spaced_categories"] is True: 	
		db_col_list = list(config["csv_out"].values())
	else:
		db_col_list = list(config["csv_out"].keys())
	# Loads the dictionary keys and assigns them to values that will
	# be used in DataFrame columns to allow for agnostic column calls.
	cl_list = coll.namedtuple("cl_list", "dt0 usr sad dad loc")
	cl = cl_list(*list(config["csv_out"].keys()))

	#Check folder names from config and create them if they do not exist.
	if not os.path.exists(outputfolder):
		os.makedirs(outputfolder)
		logging.debug(f'Output folder created at {outputfolder}'
	)
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
		help="specify a year"		
	)
	# Listen for a year argument and use lamda and strptime to 
	# determine if it is a valid month (between 1-12).
	#parser.add_argument("-m","--month", type=lambda d: datetime.strptime(d, '%m'), help="specify a month (integer)") #DELETEME
	parser.add_argument(
		"-m","--month", 
		nargs='+', 
		type=lambda d: arrow.get(d, 'MM').format('MM'), #TODO figure out how to convert 1 digit numbers and 3 char months into 2 digit months
		#type=lambda d: arrow.Arrow.strptime(d, '%m'),
		help="specify a month (integer)"
	)
	args = parser.parse_args()

	try:
		# Function takes an input time (x) (or multiple input times) and
		# converts them to the specified format (t) using Arrow.
		def date_fmt(x,t):
			#TODO - Expand function funcionality to format multiple types and consolidate code from elsewhere
			if t == 0:
				ot = arrow.get(x).format('YYYY-MM-DD')
			if t == 1:
				ot = arrow.get(x).format('dddd')
			# Used to convert Monday through Sunday to 1 - 7 using arrow
			# then checks for 7 and changes it to 0 to make the sort start
			# with Sunday instead of Monday.
			if t == 2:
				ot = arrow.get(x).format('d')
				ot = '0' if ot == '7' else ot
			if t == 3:
				ot = arrow.get(x).format('HH')
			if t == 4:
				ot = arrow.get(x, config["csv"]["timestamp_format"])
			return ot
	


		def set_stat_range(y,m):
			# Calculate the previous month.
			prevmonth = arrow.now().shift(months=-1)
			# Calculate the first month of the year.
			first_month = arrow.get(1).replace(year=arrow.now().year)
			# Calculate the last month of the year.
			last_month = arrow.get(1).replace(
				year=arrow.now().year
			).shift(months=-1)
			# Creates a default range of last month to last month, can be
			# modified by other functions, will be expanded into a full 
			# range later in the program.
			start_end = [prevmonth, prevmonth]
			# Checks to run if at least one year was specified,
			# and if no months were specified.
			if y is not None and m is None:
				if len(y) <= 1 and m is None: 
					s = arrow.get(first_month).replace(year=int(y[0]))
					e = arrow.get(last_month).replace(year=int(y[0]))
					start_end = [s, e]
				elif len(y) == 2 and m is None: 
					s = arrow.get(first_month).replace(year=int(y[0]))
					e = arrow.get(last_month).replace(year=int(y[1]))
					start_end = [s, e]
			# Checks to run if at least one month was specified,
			# and no years were specified.
			if m is not None and y is None:
				if len(m) <= 1 and y is None:
					s = arrow.get(prevmonth).replace(month=int(m[0]))
					start_end = [s] * 2
				elif len(m) == 2 and y is None:
					s = arrow.get(prevmonth).replace(month=int(m[0]))
					e = arrow.get(prevmonth).replace(month=int(m[1]))
					start_end = [s, e]
			# Checks to run if at least one month and
			# one year were specified.
			if m and y is not None:
				if len(y) <= 1 and len(m) <= 1: 
					s = arrow.get().replace(year=int(y[0]),month=int(m[0]))
					start_end = [s] * 2
				elif len(y) == 1 and len(m) == 2:
					s = arrow.get().replace(year=int(y[0]),month=int(m[0]))
					e = arrow.get().replace(year=int(y[0]),month=int(m[1]))
					start_end = [s, e]
				elif len(y) == 2 and len(m) == 1:
					s = arrow.get().replace(year=int(y[0]),month=int(m[0]))
					e = arrow.get().replace(year=int(y[1]),month=int(m[0]))
					start_end = [s, e]
				elif len(y) == 2 and len(m) == 2:
					s = arrow.get().replace(year=int(y[0]),month=int(m[0]))
					e = arrow.get().replace(year=int(y[1]),month=int(m[1]))
					start_end = [s, e]
				# Checks if there are 3 or more arguments for month or
				# year and kills program if there is.
				elif len(y) >= 2 or len(m) >= 2:
					logging.debug(args)
					raise ValueError('too many arguments')
			return start_end


		# Uses args as input into the above function sets the return
		# value as the date_r variable.
		date_r = set_stat_range(args.year, args.month)
	except ValueError as err:
		logging.error(err)
		raise
	# Take the start and end dates, and create a range of dates by
	# iterating monthly from the start to the end date, then formats
	# the dates as YYYYMM in the spu Template from the config.
	filenames = []
	for r in arrow.Arrow.range('month', date_r[0], date_r[1]):
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
		])}''')

	# Check if the range is only one month, and if it is, make the 
	# date only appear once, else, use both dates.
	if date_r[0] == date_r[1]:
		output_name = os.path.sep.join([
			outputfolder,
			out_file_prefix
		  + "_"
		  + date_r[0].format("YYYYMM")
		])
		output_name_csv = output_name + ".csv"
		output_name_pdf = output_name + ".pdf"
		output_name_html = output_name + ".html"
	else:
		output_name = os.path.sep.join([
			outputfolder,
			out_file_prefix
		  + "_"
		  + date_r[0].format("YYYYMM")
		  + "_"
		  + date_r[1].format("YYYYMM")
		])
		output_name_csv = output_name + ".csv"
		output_name_pdf = output_name + ".pdf"
		output_name_html = output_name + ".html"
	# Set active output file to output_name_csv (specified in config)
	# and opens it to write.
	#output_csv = open(output_name_csv,'w') #DELETEME ?
	def load_log():
		# Creates an empty pandas DataFrame, then loads the logfile
		# via filenames variable and iterates through it, adding each
		# line to the DataFrame as it goes.
		global df #TODO - Find a better way to handle this
		df = pd.DataFrame()
		csv_in = config["csv_in"]
		for file in filenames:
			with open(file) as f:
				lines = [line.strip() for line in f]
				for line in lines:
					l = line.split()
					l_daddr = l[5]
					l_date = arrow.get(
						' '.join(l[1:3]), #TODO - make configurable
						config["csv"]["timestamp_format"]
					)
					
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
					l_row = { 
						cl.sad : l[0], 
						cl.dt0 : l_date, 
						cl.usr : l[3], 
						cl.dad : l_daddr, 
						cl.loc : l[6] 
					}
					df_row = pd.Series(l_row)
					df = df.append(df_row, ignore_index=True)
		df = df[[cl.dt0, cl.usr, cl.sad, cl.dad, cl.loc]]
	load_log()
	df.to_csv(output_name_csv, index=False)
	logging.debug(f'Saved and closed CSV File: {output_name_csv}')


	# Begin CSV analysis with Pandas and MatPlotLib.

	# Open the created CSV file in pandas.
	branding = config["pdf_branding"] #TODO -move this
	org_name = branding["org_name"]
	#df = pd.read_csv(output_name_csv)
	logging.debug(f'Opened CSV as DataFrame: {output_name_csv}')
	
	# Checks the date range, sets a single number if only one month
	# is the range, if it's anything else, display the start and end
	# date range.
	if date_r[0] == date_r[1]:
		date_range = date_r[0].format("MMMM YYYY")
	else:
		date_range = (
			date_r[0].format("MMMM YYYY")
		  + " - "
		  + date_r[1].format("MMMM YYYY")
		)
	htm_cfg = config["html_settings"]
	

	def html_head():
		htm_title = f'{htm_cfg["title_prefix"]} - {date_range}'
		with open(htm_cfg["css_template"], 'r') as file:
			htm_css = file.read()
		h = f'<head><title>{htm_title}</title><style>{htm_css}</style></head>'
		html.write(h)


	def html_unique_users():		
		title = '<h2>Unique Sessions</h2>'
		# Unique users table generation.
		tdf = pd.DataFrame({
				# Pulls in the index columns for source ips and users
				# then only displays the count of unique values.
				'Unique IPs' : [df[cl.sad].nunique()],
				'Unique Users': [df[cl.usr].nunique()]
		})
		page = tdf.to_html(index=False).replace('border="1"','border="0"')
		html.write(title)
		html.write(page)

	#TODO - Write calendar sessions by day parsing, output via matplotlib or html, probably matplotlib?
	

	def html_weekly_sessions():
		title = '<h2>Sessions by Weekday</h2>'
		tdf = df.filter([cl.dt0], axis=1)
		# The following Code reindexes the week and resorts it from
		# sunday to saturday by creating a temporary row and
		# uses it's index to order the original dataframes output.
		tdf['day_index'] = [date_fmt(x,2) for x in tdf[cl.dt0]]
		tdf = tdf.sort_values('day_index')
		tdf[cl.dt0] = [date_fmt(x,1) for x in tdf[cl.dt0]]
		tdf['sess0'] = tdf[cl.dt0].groupby(tdf[cl.dt0]).transform('count')
		tdf = pd.DataFrame(tdf).drop_duplicates().reset_index(drop=True)
		tdf = pd.DataFrame(tdf).drop(columns='day_index')
		tdf = tdf.set_axis(['Weekdays','Sessions'], axis=1, inplace=False)
		page = tdf.to_html(index=False).replace('border="1"','border="0"')
		html.write(title)
		html.write(page)

	def html_sessions_hourly():
		title = '<h2>Sessions by Hour</h2>'
		tdf = df.filter([cl.dt0], axis=1)
		tdf[cl.dt0] = [date_fmt(x,3) for x in tdf[cl.dt0]]
		tdf['sess0'] = tdf[cl.dt0].groupby(tdf[cl.dt0]).transform('count')
		tdf = tdf.sort_values(cl.dt0)
		tdf = pd.DataFrame(tdf).drop_duplicates().reset_index(drop=True)
		tdf = tdf.set_axis(['Hour','Sessions'], axis=1, inplace=False)
		page = tdf.to_html(index=False).replace('border="1"','border="0"')
		html.write(title)
		html.write(page)

	
	def html_session_location():
		title = '<h2>Sessions by Location</h2>'
		tdf = df.filter([cl.loc], axis=1)
		#TODO - Make this happen once in the dataframe after CSV generation.
		loc_dict = {"local" : 1, "proxy" : 0}
		tdf = tdf.replace({cl.loc: loc_dict})
		tdf['sess0'] = tdf.groupby(cl.loc)[cl.loc].transform('count')
		tdf = tdf.drop_duplicates().reset_index(drop=True)
		tdf = tdf.set_axis(['Location','Sessions'], axis=1, inplace=False)
		tdf = tdf.replace(to_replace={
			1:'Library Session', 
			0:'Remote Session'
		})
		page = tdf.to_html(index=False).replace('border="1"','border="0"')
		html.write(title)
		html.write(page)


	def html_requested_urls():
		title = '<h2>Sessions by Resource</h2>'
		# Filter the Data Frame into a new temporary frame.
		tdf = df.filter([cl.dad, cl.usr, cl.loc], axis=1)
		# Count number of sessions into a new column based on resource.
		tdf['sess0'] = tdf[cl.dad].groupby(tdf[cl.dad]).transform('count')
		# Count number of unique sessions by counting unique number 
		# of usernames in the usern column.
		tdf['sess1'] = tdf.groupby(cl.dad)[cl.usr].transform('nunique')
		# Count number of local sessions by creating a dictionary
		# and using that dictionary to replace all instances of
		# local and proxy with int values, then summing those values
		# based on the destination address.
		#TODO - Make this happen once in the dataframe after CSV generation.
		loc_dict = {"local" : 1, "proxy" : 0}
		tdf = tdf.replace({cl.loc: loc_dict})
		tdf['sess2'] = tdf[cl.loc].groupby(tdf[cl.dad]).transform('sum')
		# Copy the result dataframe into a new frame, drop the
		# now unneeded usern and local columns, drop all duplicate
		# rows from the frame, and resort the columns by the number 
		# of sessions.
		tdf = pd.DataFrame(tdf).drop(columns=[cl.usr,cl.loc])
		tdf = pd.DataFrame(tdf).drop_duplicates().reset_index(drop=True)
		tdf = tdf.sort_values(tdf.columns[1],ascending=False)
		tdf = tdf.set_axis(htm_cfg["resource_col"], axis=1, inplace=False)
		page = tdf.to_html(index=False).replace('border="1"','border="0"')
		html.write(title)
		html.write(page)


	# Begin Writing HTML File
	with open(output_name_html, "w") as html:
		html_head()
		html_unique_users()
		html_weekly_sessions()
		html_sessions_hourly()
		html_session_location()
		html_requested_urls()


	logging.debug(f'Saved and closed PDF File: {output_name_html}')
except Exception as err: # Sends any error exception to the log.
    logging.error(err, exc_info=True)
    print(f'\033[91mERROR\033[00m {err} -- Check {errorlog} for more details')
