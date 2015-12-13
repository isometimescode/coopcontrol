# Using the sunrise-sunset.org API, this script writes some data out every day at midnight to a local file.
# Includes: sunrise in localtime, sunset in localtime, and total daylight hours.
#
# Note: running this will always overwrite the existing file in FILENAME with new data.
#

import urllib2
import json
import sys
import os
from datetime import datetime, timedelta
import dateutil.tz
import dateutil.parser

# set this latitude and longitude to your location
LAT = '47.690416'
LONG = '-122.315576'
SUNRISE_URL = 'http://api.sunrise-sunset.org/json?date=tomorrow&formatted=0&lat='+LAT+'&lng='+LONG

# where results will be saved for other code to reference
FILENAME = os.path.splitext(__file__)[0]+'.json'

# how many hours of daylight you want your chickens to have, for adding supplemental light in the short winter
NEEDED_DAYLIGHT = 12

try:
    apidata = json.load(urllib2.urlopen(SUNRISE_URL,None,2))
except (urllib2.HTTPError,urllib2.URLError) as e:
    print 'API error: ', e.reason
    sys.exit()

if apidata and apidata['status'] != 'OK':
    sys.exit('Error: '+apidata['status'])

# the results look like 2015-12-10T15:47:11+00:00
# so we need to convert from UTC to whatever the local time is
utc = dateutil.parser.parse(apidata['results']['sunrise'])
sunrise_lcl = utc.astimezone(dateutil.tz.tzlocal())

utc = dateutil.parser.parse(apidata['results']['sunset'])
sunset_lcl = utc.astimezone(dateutil.tz.tzlocal())

daylight_hours = (sunset_lcl - sunrise_lcl).total_seconds() / 60 / 60

if daylight_hours < NEEDED_DAYLIGHT:
    light_lcl = sunrise_lcl - timedelta(hours=(NEEDED_DAYLIGHT-daylight_hours))
    light_lcl = light_lcl.strftime("%Y-%m-%d %H:%M:%S")
else:
    light_lcl = 0

# write it out to a cache file
data = {}
data['sunrise_localtime'] = sunrise_lcl.strftime("%Y-%m-%d %H:%M:%S")
data['sunset_localtime'] = sunset_lcl.strftime("%Y-%m-%d %H:%M:%S")
data['daylight_hours'] = daylight_hours
data['light_on_localtime'] = light_lcl

outfile = open(FILENAME,'w')
outfile.write(json.dumps(data,indent=4))
outfile.close