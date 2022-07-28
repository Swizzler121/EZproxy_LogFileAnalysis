#!/bin/sh

#variables to use correct command
LAST_MONTH=`date -d "$(date +%Y-%m-1) -1 month" +%-m`
THIS_MONTH=`date -d "$(date +%Y-%m-1) 0 month" +%-m`

echo "delay test" 
wait 600
echo "it's been 10 minutes"