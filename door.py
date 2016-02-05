# Using the cached data from sunrise_data.py, this script will check the current time
# and determine if the door should be opened (sunrise) or closed (sunset)
#
# I use the Add-A-Motor Chicken Coop Motor (D20) which simply operates in the opposite direction
# whenever it receives power. Because of this, we can't have the power on all the time; it
# needs to be switched on and off again when the motor should be run.
#
# My crontab: runs every 15 minutes every day between early morning and a possible sunset,
# which is just an estimated based on the widest range for my area's long summer days.
#
# */15 6-23 * * * python /full/path/door.py
#

import json
import sys
from datetime import datetime
from dateutil import parser, tz
from inc.doormod import Door
from inc import coop_settings as cs

# optional: can tell the script to be more verbose in the logs
if len(sys.argv) > 1:
    VERBOSE = sys.argv[1]
else:
    VERBOSE = 0


# get sunrise/sunset data
srdata = cs.getJSONData(cs.sunset_file)

sunrise = parser.parse(srdata['sunrise_localtime'])
sunset = parser.parse(srdata['sunset_localtime'])
current = datetime.now(tz.tzlocal())

# if any errors happened with pulling sunrise data, it may be out of date
# assume the _times_ are correct and just replace the old date with today's date
if sunrise.date() != current.date():
    sunrise = sunrise.replace(current.year, current.month, current.day)
    sunset = sunset.replace(current.year, current.month, current.day)

# the door is only open during sunrise and sunset
# any other time the door should be closed

d = Door()

if sunrise <= current < sunset:
    if VERBOSE:
        cs.appendLog('door','its after sunrise('+sunrise.strftime('%X')+') check door: open')
    if int(d.getdoor()) == 0:
        d.changedoor(1)
else:
    if VERBOSE:
        cs.appendLog('door','its after sunset('+sunset.strftime('%X')+') check door: closed')
    if int(d.getdoor()) == 1:
        d.changedoor(0)
