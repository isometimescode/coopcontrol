# Main cron for running equipment on a schedule. Checks each piece of equipment in the coop
# and decides if its time to turn it on or off.
#
# Check available options:
# python scheduler.py -h
#
# Crontab: every 10 minutes during the daytime
# 0/10 5-20 * * * python /full/path/scheduler.py -s /some/path/data/settings.json
#
#

import logging
import argparse
from datetime import datetime
from dateutil import tz
from coopcontrol import door,light

sysparse = argparse.ArgumentParser(description="Check each piece of equipment in the coop "
                                   "and decide if it should be on or off.")
sysparse.add_argument('-s', '--settings', required=True,
                      help=("The location of the settings.json file containing information like "
                      "the BCM pins for your coop. Ex: "
                      "/tmp/files/settings.json"))
sysargs = sysparse.parse_args()


def check_item(item):
    current_time = datetime.now(tz.tzlocal())

    start = item.get_start_time()
    end = item.get_end_time()

    if start <= current_time < end:
        logging.debug('within the start and end time, %s should be %s',
                      item.__class__.__name__,
                      item.get_status_name(1))
        item.set_status(1)
    else:
        logging.debug('outside the start and end time, %s should be %s',
                      item.__class__.__name__,
                      item.get_status_name(0))
        item.set_status(0)


def main():
    check_item(light.Light(sysargs.settings))
    check_item(door.Door(sysargs.settings))


if __name__ == '__main__':
    main()