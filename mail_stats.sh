#!/bin/sh

#Static Variables
LAST_MONTH_NAME=`date -d "$(date +%Y-%m-1) -1 month" +%B`
LAST_MONTH_YEARDAY=`date -d "$(date +%Y-%m-1) -1 month" +%Y%m`

#User Editable Variables
DEST_EMAIL="example@example.com"
SUBJECT_LN="EZProxy Stats" $LAST_MONTH_NAME

#Program
python /home/ezproxy/ezpstats/ezp-stats.py &
PROCESS_ID=$!
echo "waiting for script to finish"
wait $PROCESS_ID
echo "sending mail"
echo "" | mutt -s $SUBJECT_LN $DEST_EMAIL -a  /home/ezproxy/ezpstats/output/ezpstat_$LAST_MONTH_YEARDAY.html