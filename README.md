# ezp-stats
Python script to analyze EZproxy SPU logs [Forked]

Code4Lib article: https://journal.code4lib.org/articles/13918

## Downloading & Installing the script
**Windows via Archive**
1. Unlike previous forks, you **cannot** easily run the script in an IDE like Anaconda, as I use command line arguements to simplify automation.
2. Check for python 3, install if needed.
	- Open Command Prompt, Powershell, or Powershell core and type `python3 -V`, if it returns a version number, it's already installed
	- You can download and install python 3 from [the python website](https://www.python.org/downloads/)
3. Create a program directory for the script. This has to be in a directory the user running it has write access to, so anything under `C:\Users\{username}\` should work. For this guide, I'm going to assume a directory was created at `C:\Users\{username}\ezp-stats\`.
4. Download the latest archive from the releases page.
5. Extract the script and related files into the directory we just created.
6. Install the required dependancies
	- Open Command Prompt, Powershell, or Powershell core as an administrator (install may fail when running as standard user) and navigate to the directory we created, E.g. `cd C:\Users\{username}\ezp-stats\`
	- Run the following command: `pip install -r requirements.txt`  as Administrator. This command will download the required dependencies via the Python Package Installer. Make sure you are currently in the directory with the requirements.txt file or this command will fail. I've had numpy wheels fail to compile when using 3.10, but we do not use that dependancy, so this is fine, however this will abort the pip requirements install and you will need to manually install the required libraries.

**Linux via Archive**
1. Check for python 3, install if needed.
	- Open a Terminal and type `python3 -V`, if it returns a version number, it's already installed
	- Most linux versions have Python installed by default, if it is not installed, you can install it via your distributions package manager.
2. Create a program directory for the script. This has to be in a directory the user running it has write access to, so anything under `/home/{username}/` should work in most distributions. For this guide, I'm going to assume a directory was created at `/home/{username}/ezp-stats/`
3. Download the latest archive from the releases page.
4. Extract the script and related files into the directory we just created.
5. Install the required dependancies
	- Open a Terminal and navigate to the directory we created, E.g. `cd /home/{username}/ezp-stats/`
	- Run the following command: `pip install -r requirements.txt` This command will download the required dependencies via the Python Package Installer. Make sure you are currently in the directory with the requirements.txt file or this command will fail.

## Running The Script

**Not finished, check back later**
