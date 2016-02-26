# Using the sunrise-sunset.org API, this script writes some data out to a local file.
# By default will get data for today. Note: running this will always overwrite
# the existing file with new data.
#
# Check available options:
# python sunrise_data.py -h
#
# Crontab: runs every day at midnight
# 0 0 * * * python /full/path/sunrise_data.py -s /some/path/data/settings.json
#

import urllib2
import json
import sys
import logging
from os import path
from datetime import datetime, timedelta
from dateutil import parser, tz
import argparse

sysparse = argparse.ArgumentParser(description="Retrieve and store sunrise/sunset/daylight data")
sysparse.add_argument('-s', '--settings', required=True,
                      help=("The location of the settings.json file containing information like "
                      "latitude and longitude for your location. Ex: "
                      "/tmp/files/settings.json"))
sysparse.add_argument('-l', '--loglevel', default="WARNING",
                      help="Optionally set the log level to DEBUG for testing.")
sysparse.add_argument('-d', '--date', default="today",
                      help="An optional date to check, default is today.")
sysargs = sysparse.parse_args()


def get_api_data(settings,api_date):
    """
    Get results from sunrise JSON api or exits on failure.

    Args:
        settings: the JSON data from the settings file
        api_date: the date to check, like "today" or "2016-01-01"

    Returns:
        JSON response from API. Example:
        {
          "results": {
            "sunrise": "2016-02-23T15:00:16+00:00",
            "sunset": "2016-02-24T01:44:50+00:00",
            "solar_noon": "2016-02-23T20:22:33+00:00",
            "day_length": 38674,
            "civil_twilight_begin": "2016-02-23T14:29:08+00:00",
            "civil_twilight_end": "2016-02-24T02:15:58+00:00",
            "nautical_twilight_begin": "2016-02-23T13:53:21+00:00",
            "nautical_twilight_end": "2016-02-24T02:51:44+00:00",
            "astronomical_twilight_begin": "2016-02-23T13:17:39+00:00",
            "astronomical_twilight_end": "2016-02-24T03:27:26+00:00"
          },
          "status": "OK"
        }

    Raises:
        HTTPError, URLError
    """

    sunrise_url = ('http://api.sunrise-sunset.org/json?date='+api_date+
        '&formatted=0'+
        '&lat='+settings['latitude']+
        '&lng='+settings['longitude'])

    logging.debug("checking url %s", sunrise_url)

    try:
        data = json.load(urllib2.urlopen(sunrise_url,None,2))
    except (urllib2.HTTPError,urllib2.URLError) as e:
        logging.warning('API error: %s', e.reason)
        sys.exit(1)

    if data and data['status'] != 'OK':
        logging.warning('Error in response: %s',data['status'])
        sys.exit(1)

    return data


def get_settings_data(filename):
    """
    Load the JSON settings data

    Args:
        filename: the file to check

    Returns:
        settings hash

    Raises:
        IOError on file error
    """

    try:
        with open(filename,'r') as f:
            settings_data = json.load(f)
        f.close
    except IOError as e:
        # we print the error here because without the settings data
        # we have no logging information
        print('error: %s', e.strerror)
        sys.exit(1)

    # set a default path if necessary
    if 'data-directory' not in settings_data or not settings_data['data-directory']:
        settings_data['data-directory'] = path.abspath(path.dirname(filename))

    return settings_data


def writeJSONData(settings,data):
    """
    Output the data to a file in JSON pretty format.

    Args:
        data: the data to save to the file

    Raises:
        IOError on file error
    """

    file = path.join(path.abspath(settings['data-directory']),'sunrise_data.json')
    logging.debug("writing results to %s", file)

    try:
        with open(file,'w') as outfile:
            outfile.write(json.dumps(data,indent=4,sort_keys=True))
        outfile.close
    except IOError as e:
        logging.warning('error: %s', e.strerror)
        sys.exit(1)


def main():
    settings = get_settings_data(sysargs.settings)

    if sysargs.loglevel:
        logging.getLogger().setLevel(getattr(logging, sysargs.loglevel.upper(), logging.WARNING))

    api_data = get_api_data(settings,sysargs.date)

    # the results look like 2015-12-10T15:47:11+00:00
    # so we need to convert from UTC to whatever the local time is
    utc = parser.parse(api_data['results']['sunrise'])
    sunrise_lcl = utc.astimezone(tz.tzlocal())

    utc = parser.parse(api_data['results']['sunset'])
    sunset_lcl = utc.astimezone(tz.tzlocal())

    # this data is also in api_data['results']['day_length']
    daylight_hours = (sunset_lcl - sunrise_lcl).total_seconds() / 60 / 60

    if daylight_hours < settings['ideal-day']:
        light_lcl = sunrise_lcl - timedelta(hours=(settings['ideal-day']-daylight_hours))
        light_lcl = light_lcl.strftime("%H:%M:%S%z")
    else:
        light_lcl = 0

    # write it out to a cache file, basically just makes it so we don't have
    # to talk to the sunrise API all the time
    data = {}
    data['date_local']         = sunrise_lcl.strftime("%Y-%m-%d")
    data['sunrise_localtime']  = sunrise_lcl.strftime("%H:%M:%S%z")
    data['sunset_localtime']   = sunset_lcl.strftime("%H:%M:%S%z")
    data['daylight_hours']     = daylight_hours
    data['light_on_localtime'] = light_lcl

    writeJSONData(settings,data)


if __name__ == '__main__':
    main()