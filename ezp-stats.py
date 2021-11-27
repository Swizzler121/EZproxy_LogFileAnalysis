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
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib import colors
from reportlab.platypus import PageBreak

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
		help="specify a month (integer)"
	)
	args = parser.parse_args()
	try:
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
	# Set active output file to output_name_csv (specified in config)
	# and opens it to write.
	output_csv = open(output_name_csv,'w')
	def csv_output_columns():
		# Checks if extended dates seprate date, weekday, and hour are
		# enabled, if not, it deletes those keys from the dictionary.
		if config["csv_flags"]["do_extended_dates"] is not True:
			config["csv_out"].pop('date1')
			config["csv_out"].pop('date2')
		
		# Checks if spaced category names are enabled, and if so it pulls
		# the dictionary values from the config instead of the keys.
		if config["csv_flags"]["do_spaced_categories"] is True:
			db_value_list = list(config["csv_out"].values())
		else:
			db_value_list = list(config["csv_out"].keys())
		# Writes the resulting dictionary (either values or keys
		# depending on config) to the first row of the CSV file.
		output_csv.write(','.join(db_value_list))


	csv_output_columns()


	def write_csv_data():
		# Loads the logfile via filenames variable and iterates through
		# it, assigning each line to a variable as it goes
		csv_in = config["csv_in"]
		for file in filenames:
			with open(file) as f:
				#lines = [csv_cleanup_input(line) for line in f]
				lines = [
					line.strip().replace("[","").replace("]","") for line in f
				]
				for line in lines:
					l = line.split()
					l_saddr = l[csv_in["saddr"]]
					l_date = arrow.get(
						' '.join(l[1:3]), #TODO - make configurable
						config["csv"]["timestamp_format"]
					)
					l_usern = l[csv_in["usern"]]
					l_daddr = l[csv_in["daddr"]]
					l_local = l[csv_in["local"]]

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
					output_csv.write('\n')
					# Writes one line of data to the CSV.
					# Checks if do_extended_dates is true, if so it
					# formats the date entry 3 times to the predetermined
					# Date types and places them in the correct column.
					#TODO - implement a way to change ouput order
					if config["csv_flags"]["do_extended_dates"] is True:
						output_csv.write(
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
						output_csv.write(
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
	write_csv_data()
	# Closes the output CSV file.
	output_csv.close()

	# Open the created CSV file in pandas.
	branding = config["pdf_branding"]
	org_name = branding["org_name"]
	csv_pd = pd.read_csv(output_name_csv)
	if date_r[0] == date_r[1]:
		pdf_date = date_r[0].format("MMMM YYYY")
	else:
		pdf_date = (
			date_r[0].format("MMMM YYYY")
		  + " - "
		  + date_r[1].format("MMMM YYYY")
		)

	# Max Height 850
	# Max Width 195
	pdf = canvas.Canvas(output_name_pdf)
	# pdfmetrics.registerFont(
	# 	TTFont(
	# 		'title-font', os.path.sep.join([
	# 		branding["brand_folder"], 
	# 		branding["title_font_file"]
	# 		])
	# 	)
	# )
	# pdfmetrics.registerFont(
	# 	TTFont(
	# 		'body-font', os.path.sep.join([ 
	# 		branding["brand_folder"], 
	# 		branding["body_font_file"]
	# 		])
	# 	)
	# )
	pdf.setTitle(f'{branding["pdf_title"]}  {pdf_date}')
	def pdf_cover_page():
		pdf.setFont("Helvetica-Bold", 36)
		pdf.drawCentredString(300, 250, branding["pdf_title"])
		pdf.setFont("Helvetica-Bold", 24)
		pdf.drawCentredString(300, 150, pdf_date)
		pdf.drawInlineImage(os.path.sep.join([
				branding["brand_folder"],
				branding["big_logo"]]), 100, 350
		)
	def pdf_base_page():
		pdf.setFont("Helvetica-Bold", 36)
		pdf.drawCentredString(300, 250, branding["pdf_title"])
		pdf.setFont("Helvetica-Bold", 24)
		pdf.drawCentredString(300, 150, pdf_date)
		pdf.drawInlineImage(os.path.sep.join([
				branding["brand_folder"],
				branding["page_logo"]]), 50, 50
		)	
	pdf_pages = []
	pdf_pages.append(pdf_cover_page())
	pdf_pages.append(pdf.showPage())
	pdf_pages.append(pdf_base_page())

	pdf.save()

except Exception as err: # Sends any error exception to the log.
    logging.error(err, exc_info=True)
    print(f'\033[91mERROR\033[00m {err} -- Check {errorlog} for more details')
