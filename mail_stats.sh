#!/bin/sh

####################
##Static Variables##
####################
LAST_MONTH_NAME=`date -d "$(date +%Y-%m-1) -1 month" +%B`
LAST_MONTH_YEARDAY=`date -d "$(date +%Y-%m-1) -1 month" +%Y%m`

###########################
##User Editable Variables##
###########################
#destination Email Address
DEST_EMAIL="example@example.com"

#Prefix before Month Name
SUBJECT_PF="EZProxy Stats"

#EZP-stats ouput folder/file location
OUTPUT_LOC="/home/ezproxy/ezpstats/output/ezpstat_$LAST_MONTH_YEARDAY.html"

#Program
python3 /home/ezproxy/ezpstats/ezp-stats.py &
PROCESS_ID=$!
#Waiting for script to finish
wait $PROCESS_ID
#Sending mail
echo "" | mutt -s "$SUBJECT_PF $LAST_MONTH_NAME" $DEST_EMAIL -a $OUTPUT_LOC