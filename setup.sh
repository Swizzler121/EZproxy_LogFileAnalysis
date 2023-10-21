#!/bin/sh

# ezp-stats install and upgrade script - for more information please see github:
# https://github.com/salinapl/ezp-stats
#
# !!!WORK IN PROGRESS -- DO NOT EXECUTE ON PRODUCTION SERVER!!!
ezpver=$(grep -oP 'ezpver = "\K[^"]+' ezp-stats.py)
echo "$ezpver"
