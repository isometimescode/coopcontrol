# Automated Chicken Coop Control

## The Package: `coopcontrol`

This package is used by the cron scripts and web scripts to manipulate the raspberry pi pins/outlets. The code in this directory isn't run directly. However, when you run `python setup.py install` it will make the package available to all the scripts in the `bin` and `www/service` directories like:

```
$ coopcontrol/venv/bin/python
>>> from coopcontrol import light
>>> print light.Light('coopcontrol/data/settings.json').get_start_time()
2016-02-26 05:49:26-08:00
```
