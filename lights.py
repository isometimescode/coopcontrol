# Using the cached data from sunrise_data.py, this script will check the current time
# and determine if the extra (winter time) lights should be on to stimulate laying.
#
# My crontab: runs every 15 minutes every day from early morning until mid morning. I run the
# winter light only in the morning until sunrise, so this range tries to cover the earliest
# the light might turn on (i.e. in dead of winter) to the latest sunrise. The cron can just be
# commented out in non-winter months if needed too. You can have finer control of the lights
# by running it more often (*/5 minutes perhaps), but I don't feel like it needs to be down to the
# second accurate, so that's why its at 15 for me.
#
# */15 4-9 * * * python /full/path/lights.py
#

import sys
from datetime import datetime
from dateutil import parser, tz
import wiringpi2 as wiringpi
import coop_settings

# this is for convenience in reading; basically you set the relay pin to "low" for "active"
# and set the pin to "high" to make it "inactive"
light_on = 0 # or low
light_off = 1 # or high

def changelight(newstate):
    wiringpi.wiringPiSetup()
    wiringpi.pinMode(coop_settings.pin_lights, 1) # output mode

    if newstate == light_on:
        coop_settings.appendLog('light','setting pin#'+str(coop_settings.pin_lights)+' to on')
        wiringpi.digitalWrite(coop_settings.pin_lights, light_on)
    else:
        coop_settings.appendLog('light','setting pin#'+str(coop_settings.pin_lights)+' to off')
        wiringpi.digitalWrite(coop_settings.pin_lights, light_off)


def getlight():
    wiringpi.wiringPiSetup()
    wiringpi.pinMode(coop_settings.pin_lights, 1) # output mode
    return wiringpi.digitalRead(coop_settings.pin_lights)

# get sunrise/sunset data
srdata = coop_settings.getJSONData(coop_settings.sunset_file)

# depending on the settings, we may not need any actual supplemental light
if srdata['light_on_localtime'] == 0:
    coop_settings.appendLog('light','light skipped')
    sys.exit()

lighton = parser.parse(srdata['light_on_localtime'])
sunrise = parser.parse(srdata['sunrise_localtime'])
current = datetime.now(tz.tzlocal())

# if any errors happened with pulling sunrise data, it may be out of date
# assume the _times_ are correct and just replace the old date with today's date
if lighton.date() != current.date():
    lighton = lighton.replace(current.year, current.month, current.day)
    sunrise = sunrise.replace(current.year, current.month, current.day)

# the light is going to be on between the light time and sunrise
# any other time the light should be off
if lighton <= current < sunrise:
    coop_settings.appendLog('light','its after lighton('+lighton.strftime('%X')+') check light: on')
    if int(getlight()) == light_off:
        changelight(light_on)
else:
    coop_settings.appendLog('light','its after sunrise('+sunrise.strftime('%X')+') check light: off')
    if int(getlight()) == light_on:
        changelight(light_off)
