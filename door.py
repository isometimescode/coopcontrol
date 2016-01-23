# Using the cached data from sunrise_data.py, this script will check the current time
# and determine if the door should be opened (sunrise) or closed (sunset)
#
# I use the Add-A-Motor Chicken Coop Motor (D20) which simply operates in the opposite direction
# whenever it receives power. Because of this, we can't have the power on all the time; it
# needs to be switched on and off again when the motor should be run.
#

import json
import sys
from datetime import datetime
from dateutil import parser, tz
import coop_settings

# function for managing the door open/close state
def changedoor(newstate):
    "This changes the door state to open or closed"
    if newstate == 1:
        print 'door is opening'
    else:
        print 'door is closing'
    with open(coop_settings.doorstate_file,'w') as f:
        f.write(str(newstate))
    f.close

# check the door's current state
# TODO: replace this with a contact switch
try:
    with open(coop_settings.doorstate_file,'r') as f:
        dooropen = f.readline()
        dooropen = dooropen.strip()
    f.close
except IOError:
    dooropen = 0

# get sunrise/sunset data
srdata = coop_settings.getJSONData(coop_settings.sunset_file)

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
if sunrise <= current < sunset:
    print "its daytime"
    if int(dooropen) == 0:
        changedoor(1)
    else:
        print "door is already open"
else:
    print "its nighttime"
    if int(dooropen) == 1:
        changedoor(0)
    else:
        print "door is already closed"
