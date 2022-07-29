#!/bin/sh

# ezp-stats automatic email script - for more information please see github:
# https://github.com/salinapl/ezp-stats

# The following script will automatically run ezp-stats and then send the
# resulting file via email (using mutt) to a set destination. There are three
# sections below, but users under normal circumstances should only need to 
# edit the middle section titled "User Editable Variables" At bare minimum, 
# users will need to change the destination email address as the default is 
# not a valid address. The script does not set up any cron jobs, users should
# set up those scripts on their own.


######################
## Static Variables ##
######################
# These variables shouldn't need to be changed.

MONTH_NAME=`date -d "$(date +%Y-%m-1) -1 month" +%B`
MONTH_YYYYMM=`date -d "$(date +%Y-%m-1) -1 month" +%Y%m`
MONTH_MM=`date -d "$(date +%Y-%m-1) -1 month" +%m`
MONTH_YYYY=`date -d "$(date +%Y-%m-1) -1 month" +%Y`
MONTH_YY=`date -d "$(date +%Y-%m-1) -1 month" +%y`
TYPE="set content_type=text/html"

#############################
## User Editable Variables ##
#############################
# Change these variables to meet your needs.

# Destination Email Address
DEST="example@example.com"

# Prefix before MONTH_NAME
SUBJECT="EZProxy Stats"

# EZP-stats ouput folder/file location
OUTPUT="/home/ezproxy/ezpstats/OUTPUTput/ezpstat_$MONTH_YYYYMM.html"
SCRIPT_LOC="/home/ezproxy/ezpstats/ezp-stats.py"

# HTML Rich Email
RICH_EML=true

############
## Script ##
############
# You shouldn't need to edit beyond this point unless something breaks.

python3 $SCRIPT_LOC &
PROCESS_ID=$!
#Waiting for script to finish
wait $PROCESS_ID
#Sending mail
if [ "RICH_EML" = true ] ; then
    echo "" \
        | mutt -e "$TYPE" -s "$SUBJECT $MONTH_NAME" $DEST -a $OUTPUT < $OUTPUT
else
    echo "" \
        | mutt -s "$SUBJECT $MONTH_NAME" $DEST -a $OUTPUT
fi
