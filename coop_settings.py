# One place for easy and central definition of file data. This is helpful when you run this
# script in multiple environments, or if you want to save your data in a new location without
# worrying about updating each script.
#
# Also provides a couple helper functions to make things easier.
#

import json
import sys
from datetime import datetime
from dateutil import tz

# The filename of where we should output door open/closed state.
doorstate_file = 'dooropen.txt'

# The filename of where sunrise/sunset data will live.
sunset_file = 'sunrise_data.json'

# The prefix of the filename where logs are written. Scripts can append names to
# the end of this name so they can be separated from each other by directories or whatever
# you might want.
log_file_prefix = 'log-'

# how many hours of daylight you want your chickens to have,
# for adding supplemental light in the short winter
needed_daylight = 12

# set this latitude and longitude to your location
latitude = '47.690416'
longitude = '-122.315576'

# wiringpi pins that we are using for automation; my outlets are labeled with marker with the
# matching wPi pin number, but yours may be different depending on your wiring.
pin_lights  = 2
pin_door    = 0
pin_outlet1 = 1 # unused
pin_outlet3 = 3 # unused

# just a helper that reads the JSON file as specified in the argument
def getJSONData(file):
    try:
        with open(file,'r') as f:
            data = json.load(f)
        f.close
    except IOError as e:
        print file, ' error: ', e.strerror
        sys.exit(1)
    return data

# just a helper that wrties data to the JSON file as specified in the arguments
def writeJSONData(file, data):
    try:
        with open(file,'w') as outfile:
            outfile.write(json.dumps(data,indent=4))
        outfile.close
    except IOError as e:
        print file, ' error: ', e.strerror
        sys.exit(1)

# will append the current time and the provided message to the file in log_file_prefix+name+.txt
def appendLog(name,message):
    fname = log_file_prefix+name+'.txt'
    try:
        with open(fname,'a') as outfile:
            outfile.write(str(datetime.now(tz.tzlocal()))+' '+message+"\n")
        outfile.close
    except IOError as e:
        print name, ' error: ', e.strerror
        sys.exit(1)