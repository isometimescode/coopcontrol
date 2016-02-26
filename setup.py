# Creates the coopcontrol package so it can be used in bin scripts and webservices.
#

from setuptools import setup

setup(
    name='coopcontrol',
    version='1.0',
    description='Automated chicken coop with a raspberry pi and 5V relays',
    url='http://github.com/isometimescode/coopcontrol',
    author='Toni Wells',
    author_email='isometimescode@users.noreply.github.com',
    license='GNU GPLv2+',
    packages=['coopcontrol'],
    zip_safe=False
)