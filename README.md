# Automated Chicken Coop Control

## The Hardware

Following [some of these directions](http://www.instructables.com/id/Web-Controlled-8-Channel-Powerstrip/) I have 2 power outlets (4 receptacles total), a Raspberry Pi 2, and a 4-channel 5v relay module in a box on top of the coop. Since I only need to power the door and the lights right now, 4 outlets is plenty. The extra two are just in case I want to add a heated water dish in the future, or perhaps an automated feeding system.

Your Pi will need to be able to talk to the internet so that the sunrise code can get daily updates. I use the [EdiMax WiFi Adapter](http://amzn.com/B003MTTJOY) on my Pi, but there are many adapters to choose from.

### Door Motor

I use the [Add-A-Motor D20](http://www.add-a-motor.com/) door on my coop. Since I don't have a sensor (magnetic contact switch) on it at the moment, I have to "guess" knowing when the door is really open and closed with a log file. A future upgrade would be to use another Pi pin with a sensor to detect the actual state. If you use a different door setup, then you might not be able to use the door module as is currently written.

## The Software

There are plenty of tutorials out there for setting up your Pi for SSH or as a webserver or any number of other things. I'm just going to go over what's needed to run the code for controlling the power strip. All of the included code is written in _Python_.

### Installation

:warning:
I setup my Pi to export the BCM pins I'm using so that non-root users can run wiringPi. If you want to know more, see the [gpio export command](http://wiringpi.com/the-gpio-utility) and the [wiringPiSetupSys() function](http://wiringpi.com/reference/setup/). I also found that I needed to add my raspberry pi user to the "gpio" group. This is only needed for the web-facing code as it runs as a different user; if you don't use that then you can ignore this part.

To handle this initialization when my pi restarts, I'm using the bash script in `bin/gpio_init.sh` and run it like this in the crontab: `@reboot /full/path/bin/gpio_init.sh /full/path &`. The output goes to `/var/log/syslog`.

1. Copy all of the files from the repo onto your Pi. You can use `git clone` or copy it manually if you don't have git.
2. Update the [settings file](#settings) for your location.
3. I run this code in a [virtual environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/). You don't have to but it just keeps things separate.
```
$ cd coopcontrol
$ virtualenv venv
```
4. Load the required libraries like wiringpi via pip: `pip install -r requirements.txt`
5. Run the setup code to create the coopcontrol module: `venv/bin/python setup.py install`
6. Create some default files for logs and door status. This assumes the door is currently open and that you are using the default data directory. Note that you will need to change the group and write permissions if you need something like the _www-data_ user to read/write these files.
```
$ echo -n 1 > data/doorstatus.txt
$ touch data/equipment-log.txt
```
7. Test the sunrise API code. The json file should have information for the current date.
```
$ venv/bin/python bin/sunrise_data.py -s data/settings.json
$ cat data/sunrise_data.json
...
```
8. Test the light/door code. The equipment log should say what happened.
```
$ venv/bin/python bin/scheduler.py -s data/settings.json
$ cat data/equipment-log.txt
...
```

### Settings

The `data/settings.json` file is just the collection of settings used in the rest of the code.

#### Must Change
1. `latitude` and `longitude`: These need to be set to wherever you are. See (http://www.latlong.net/) if you don't know yours.
2. `light-bcm-pin` and `door-bcm-pin`: Depending on how you wired your Pi, you may have different pins than I used. These are the _BCM pins_ and not the GPIO or wiringpi pins. See (http://wiringpi.com/pins/) for more information. Note that this is so the code can be run as a non-root user. See [installation](#installation) above with note about wiringPi.

#### Optional Change
1. `ideal-day`: Number of daylight hours needed for laying; I use 12 and that works fine, but if you feel you need 14 or even 16, this is where you change it.
2. `data-directory`: This is the log and settings directory. Leave it blank for the default (`coopcontrol/data/`) or specify a new absolute path as needed for your setup.
3. `log-level`: The logging.LEVEL like DEBUG or INFO. DEBUG is nice for initial setup or testing. INFO is quieter, and WARNING will just output errors and nothing else.

### Crontab

**bin/scheduler.py**
Runs every day from early morning to evening (whatever before sunset or after sunset would be for you), 10 minute interval. Example crontab:
`0/10 5-20 * * * /full/path/venv/bin/python /full/path/scheduler.py -s /full/path/data/settings.json`

This will check the sunrise data and then check if the door/light should be on or off. You could safely run it more often than every ten minutes if you want finer time control. You could also run it all 24 hours of a day, I just know that I'll never want the lights or door open at 1am :)

**bin/sunrise_data.py**
Runs every day midnight. Example crontab:
`0 0 * * * /full/path/venv/bin/python /full/path/sunrise_data.py -s /full/path/data/settings.json`

This script is meant to run once a day or on demand if needed (for example, if something breaks and you want to re-download the data). It uses the publicly available [Sunrise API](http://sunrise-sunset.org/api) to get the correct data by latitude and longitude, and saves this to a file for use in all the other scripts. This script tries to be timezone-aware: this means that if your Pi is set to Pacific Time like mine, then it will save the data as PST in the log file. I just find this easier to read and calculate cron times.

If this script fails to get new data one night, the other code will run just fine, provided the previous' days data is still there. Day to day, sunrise and sunset change only slightly anyway, so a couple days of "old" data will not hurt anything. This gives me a little time to fix whatever might be wrong (for example, if the API is down or my internet is not working). In a pinch, you could also manually copy a new JSON file with updated data directly on to your Pi.

See _data/sunrise_data.json_ for an example file of what the calculated time data looks like when output from the script.

