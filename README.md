# Automated Chicken Coop Control

## The Hardware

Following [some of these directions](http://www.instructables.com/id/Web-Controlled-8-Channel-Powerstrip/) I have 2 power outlets (4 receptacles total), a Raspberry Pi, and a 4-channel 5v relay module in a box on top of the coop. Since I only need to power the door and the lights right now, 4 outlets is plenty. The extra two are just in case I want to add a heated water dish in the future, or perhaps an automated feeding system.

Your Pi will need to be able to talk to the internet so that the `sunrise_data.py` code can get daily updates. I use the [EdiMax WiFi Adapter](http://amzn.com/B003MTTJOY) on my Pi, but there are many adapters to choose from.

## The Software

There are plenty of tutorials out there for setting up your Pi for SSH or as a webserver or any number of other things. I'm just going to go over what's needed to run the code for controlling the power strip. 

All of the crons here are written in Python, using the [wiringPi](http://wiringpi.com) library to control the pins. See [this tutorial](http://raspi.tv/2013/how-to-use-wiringpi2-for-python-on-the-raspberry-pi-in-raspbian) to set that up if you aren't already using it. 

### Installation

Copy all of the `*.py` files to your Raspberry Pi, update `coop_settings.py` as noted below, and setup some crons. I recommend running the code manually for each file just to make sure you have any required Python libraries installed. 

### coop_settings.py

This file is just the collection of settings used in the rest of the code. By itself it doesn't do anything.

Required Updates:

1. `latitude` and `longitude`: These need to be set to wherever you are. See (http://www.latlong.net/) if you don't know yours. 
2. `pin_lights` and `pin_door`: Depending on how you wired your Pi, you may have different pins than I used. These are the _wiringPi pins_ and not the GPIO or other pins. See (http://wiringpi.com/pins/) for more information. 

Optional Updates:

1. `needed_daylight`: I am calculating it at a 12 hour day, but here is where you could change it to 14 hours, 16 or even less than that, depending on your coop setup.

### sunrise_data.py

**Crontab**: Once a day at midnight

This script is meant to run once a day or on demand if needed (for example, if something breaks and you want to re-download the data). It uses the publically available [Sunrise API](http://sunrise-sunset.org/api) to get the correct data by latitude and longitude, and saves this to a file for use in all the other scripts. This script tries to be timezone-aware: this means that if your Pi is set to Pacific Time like mine, then it will save the data as PST in the log file. I just find this easier to read and calculate cron times.

If this script fails to get new data one night, the other code will run just fine, provided the previous' days data is still there. Day to day, sunrise and sunset change only slightly anyway, so a couple days of "old" data will not hurt anything. This gives me a little time to fix whatever might be wrong (for example, if the API is down or my internet is not working). In a pinch, you could also manually copy a new JSON file with updated data directly on to your Pi.

_sunrise_data.json_: This is just an example file of what the calculated time data looks like when output from the script.

### door.py

**Crontab**: Every day from early morning to evening (whatever before sunset or after sunset would be for you), 15 minute interval

This script is for opening the door at sunrise and closing it at sunset. Running at a regular interval through a cron, if the current time is between sunset and sunrise (i.e. daytime) then the door will be opened if its not already. You are safe to run this more often than every 15 minutes if you wan the door to change state closer to the actual sunrise/sunset time. Also, you can freely run the cron 24 hours a day without anything bad happening, I just don't do that because I know I will never need the door open at 1am :)

_Door motor_: I use the [Add-A-Motor D20](http://www.add-a-motor.com/) door on my coop. Since I don't have a sensor (magnetic contact switch) on it at the moment, I have to "guess" knowing when the door is really open and closed with a log file. A future upgrade would be to use another Pi pin to detect the actual state. If you use a different door setup, then you might not be able to use this script.

### lights.py

**Crontab**: Every day from several hours before sunrise to a little after sunrise, 15 minute interval

This script is for controlling the supplemental lights needed for winter laying. Here in the Pacific Northwest our days are pretty short in the winter, and if I want eggs I need additional lights for the chickens. I have an LED string light in the run and hen house that turns on in early morning and turns off at sunrise (when the door opens). Similar to the door.py script, running on a cron it checks if the time is between when you want the light to come on and sunrise, and makes sure to turn on the light when its not. 
