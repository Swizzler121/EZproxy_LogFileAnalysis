# EZproxy_LogFileAnalysis
Python script to analyze EZproxy SPU logs [Forked]

Code4Lib article: https://journal.code4lib.org/articles/13918

Generally speaking, this script requires the following Python libraries to run:
- Pandas
- Matplotlib
The full list of dependencies are listed below.

I recommend installing Anaconda (https://www.anaconda.com/distribution/) to run the code and manage libraries

## Different report types
**Previous month (usually just 1 log file)**
Run the EZProxy-PrevMonth script to capture the data from the previous month (the script formats filenames and HTML based on the previous month)

**Full-year (or several log files)**
Run the EZProxy-FY script to capture data for a larger period of time. This one doesn't create a By Day chart/table.

## Required libraries & dependencies
**Pandas**
- setuptools
- NumPy
- python-dateutil
- pytz
- numexpr
- bottleneck

**Matplotlib**
- Python
- FreeType
- libpng
- NumPy
- setuptools
- cycler
- dateutil
- kiwisolver
- pyparsing

## How to Setup and use
**Inside Anaconda (windows)**
1. Install Anaconda and ensure that all the libraries/dependencies listed above are included
2. Download files from Google Drive or Github
3. Create a folder in root C:\ called Statistics
4. Unpack files and move into root of C:\Statistics
5. Inside C:\Statistics, create another folder ezproxy_logs.

**Outside Anaconda or on Other Operating Systems**
1. Check for python, install if needed
	- from a terminal or CMD, type python3 -V, if it returns a version number, it's already installed (all script testing was done on python 3.6-3.10)
	- If you are on windows, you can download and install python from [the python website](https://www.python.org/downloads/)
	- on linux, it is best to install python from your package manager, this changes depending on the distribution
2. install the needed dependencies using pip (included with python)
	- `pip install pandas` 
	- `pip install matplotlib` On windows, you may need to download the microsoft visual c++ compliler to install matplotlib, pay attention to terminal output for instructions if it fails to install.
3. Download EZproxy_LogFileAnalysis files from Github releases page
4. Create a program folder somewhere on your drive, name it something recognizable (like EZproxy_stats)
	- Make sure you have read/write access to the folder, normally on linux I place it in the home directory ( cd ~)
5. Unpack files and move into root of the folder you created
6. Inside the program folder, create another folder ezproxy_logs.
7. place the log or logs you want to analyze into the ezproxy_logs folder.

**Running the script inside Anaconda**
1. Copy any number of logs you want to analyze into the ezproxy_logs folder you created
2. Open the Python file you want to run in Spyder (the Python environment for Anaconda)
3. Press the PLAY button and the script will go through the logs.
4. When completed, you'll see the generated charts load in the bottom right console window.

**Running the script outside Anaconda**
1. Navigate to the EZproxy_LogFileAnalysis program directory you created in a terminal or CMD
2. for linux type `python3 EZProxy-<script you want to run>.py` for example `python3 EZProxy-PrevMonth.py` to generate a report for a single month file in the ezproxy_logs folder.
3. for windows type `python.exe EZProxy-<script you want to run>.py` for example `python.exe EZProxy-PrevMonth.py` to generate a report for a single month file in the ezproxy_logs folder.
	- I have not tested how to run the script outside anaconda on windows for enviornments that include both python 2 and python 3 installs.
4. when completed, you'll see the generated charts load in the bottom right console window.

**Opening results**
1. Navigate to the program folder and find the folder the script generated with unpacked log stats.
2. You can delete the [date].csv file generated if you don't want to keep the translated log data.
3. Opening the [date].html file will display the generated charts and table results. The chart graphics are stored in the Charts folder.