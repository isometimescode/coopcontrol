# Central place easy and central definition of file data. This is helpful when you run this
# script in multiple environments, or if you want to save your data in a new location without
# worrying about updating each script.
#
# Also provides a couple helper functions to make things easier.
#

import json
import sys

# The filename of where we should output door open/closed state.
doorstate_file = 'dooropen.txt'

# The filename of where sunrise/sunset data will live.
sunset_file = 'sunrise_data.json'

# The suffix of the filename where logs are written. Scripts can prepend names
# the beginning of this file name so they can be separated from each other.
log_file = 'log.txt'

# how many hours of daylight you want your chickens to have,
# for adding supplemental light in the short winter
needed_daylight = 12

# set this latitude and longitude to your location
latitude = '47.690416'
longitude = '-122.315576'

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