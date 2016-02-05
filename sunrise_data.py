# Using the sunrise-sunset.org API, this script writes some data out to a local file.
# Includes: sunrise in localtime, sunset in localtime, and total daylight hours.
#
# Note: running this will always overwrite the existing file in
# coop_settings.sunset_file with new data.
#
# My crontab: runs every day at midnight
# 0 0 * * * python /full/path/sunrise_data.py
#

import urllib2
import json
import sys
from datetime import datetime, timedelta
from dateutil import parser, tz
from inc import coop_settings as cs

# optional: can pass in dates to the script; otherwise we just default to today
if len(sys.argv) > 1:
    DATE = sys.argv[1]
else:
    DATE = 'today'

SUNRISE_URL = ('http://api.sunrise-sunset.org/json?date='+DATE+
    '&formatted=0'+
    '&lat='+cs.latitude+
    '&lng='+cs.longitude)

try:
    apidata = json.load(urllib2.urlopen(SUNRISE_URL,None,2))
except (urllib2.HTTPError,urllib2.URLError) as e:
    print 'API error: ', e.reason
    sys.exit(1)

if apidata and apidata['status'] != 'OK':
    sys.exit('Error: '+apidata['status'])

# the results look like 2015-12-10T15:47:11+00:00
# so we need to convert from UTC to whatever the local time is
utc = parser.parse(apidata['results']['sunrise'])
sunrise_lcl = utc.astimezone(tz.tzlocal())

utc = parser.parse(apidata['results']['sunset'])
sunset_lcl = utc.astimezone(tz.tzlocal())

# this data is also in apidata['results']['day_length']
daylight_hours = (sunset_lcl - sunrise_lcl).total_seconds() / 60 / 60

if daylight_hours < cs.needed_daylight:
    light_lcl = sunrise_lcl - timedelta(hours=(cs.needed_daylight-daylight_hours))
    light_lcl = light_lcl.strftime("%Y-%m-%d %H:%M:%S%z")
else:
    light_lcl = 0

# write it out to a cache file, basically just makes it so we don't have
# to talk to the sunrise API all the time
data = {}
data['sunrise_localtime'] = sunrise_lcl.strftime("%Y-%m-%d %H:%M:%S%z")
data['sunset_localtime'] = sunset_lcl.strftime("%Y-%m-%d %H:%M:%S%z")
data['daylight_hours'] = daylight_hours
data['light_on_localtime'] = light_lcl

cs.writeJSONData(cs.sunset_file, data)
