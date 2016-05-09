#!/bin/bash
#
# Do some initial work to manage the GPIO pins, then start the web service.
# This is so that the non-root user (like www-data) can access the GPIO pins.
#
# See: http://wiringpi.com/reference/setup/  -- wiringPiSetupSys
#      http://wiringpi.com/the-gpio-utility/ -- gpio export
#

exec 1> >(logger -s -t $(basename $0)) 2>&1

# expected to be set to something like
# /some/place/coopcontrol
readonly HOME=$1

if [[ -z $HOME || ! -d $HOME ]]; then
    echo "No directory specified" >&2
    exit 1
fi

# make sure to include any that are running doors and lights
gpio_used=(17 27 22 18 23)

for pin in ${gpio_used[@]}; do
        /usr/local/bin/gpio export $pin out
        /usr/local/bin/gpio -g write $pin 1
done

# turn on camera outlet wpi 3/BCM 22
/usr/local/bin/gpio write 3 0

# just confirms the change by printing output like
# GPIO Pins exported:
#   17: out  1  none
/usr/local/bin/gpio exports

# initialize magnetic door switch wpi 4/BCM 23
# its an input, pull-up
/usr/local/bin/gpio mode 4 up

# restarts python webapp socket
sudo -u www-data $HOME/venv/bin/python $HOME/www/service/webapp.fcgi $HOME/data/settings.json &
