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
from time import sleep
from datetime import datetime
from dateutil import parser, tz
import wiringpi2 as wiringpi
import coop_settings


# function for managing the door open/close state
# technically, we don't know if the door is already opened or closed
# this function just turns the motor for half a second regardless
def changedoor(newstate):
    wiringpi.wiringPiSetup()
    wiringpi.pinMode(coop_settings.pin_door, 1) # output mode

    if newstate == 1: #open
        coop_settings.appendLog('door','opening the door')
    else:
        coop_settings.appendLog('door','closing the door')

    # low turns the motor on
    wiringpi.digitalWrite(coop_settings.pin_door, 0)
    # wait for it to finish running - a bigger door would require more to complete
    sleep(0.5)
    # high turns the motor back off so that it can run again later
    wiringpi.digitalWrite(coop_settings.pin_door, 1)

# check the door's current state; we are just manually saving this data to a file
# since there is no other way to know if the door was last opened or closed
# TODO: replace this with a contact switch to get real data
def getdoor():
    try:
        with open(coop_settings.doorstate_file,'r') as f:
            doorstate = f.readline()
            doorstate = doorstate.strip()
        f.close
    except IOError:
        doorstate = 0
    return doorstate

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
    coop_settings.appendLog('door','its after sunrise('+sunrise.strftime('%X')+') check door: open')
    if int(getdoor()) == 0:
        changedoor(1)
else:
    coop_settings.appendLog('door','its after sunset('+sunset.strftime('%X')+') check door: closed')
    if int(getdoor()) == 1:
        changedoor(0)
