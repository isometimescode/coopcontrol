# Note on why this class has to override get_status and set_status:
#
# I use the Add-A-Motor Chicken Coop Motor (D20) which simply operates in the opposite direction
# whenever it receives power. Because of this, we can't have the power on all the time; it
# needs to be switched on and off again when the motor should be run.
#

from simple import Simple
from time import sleep
from os import path
import logging
import wiringpi2 as wiringpi
from dateutil import parser, tz

class Door(Simple):
    """Control the Door: current status, open, close"""

    def __init__(self,settings_file):
        Simple.__init__(self,settings_file)

        self.on_string   = "open"
        self.off_string  = "closed"

        self.get_status()


    def set_status(self,new_status):
        """
        Set the state of the door to open or closed, if its not already in that state.

        Args:
            new_status: 0 for closed, 1 for open.

        Raises:
            IOError: File access issues
        """

        if new_status == self.status:
            return

        if new_status == 1: #open
            logging.info("door opening")
        else:
            logging.info("door closing")

        self.init_output()

        # low turns the motor on
        wiringpi.digitalWrite(self.write_bcm_pin, 0)

        # this is simply to wait for the motor to finish running
        # we can't tell if its really finished so this sleep is just a guess
        # TODO while loop until read_bcm_pin is ready?
        sleep(10)

        # high turns the motor back off so that it can run again later
        wiringpi.digitalWrite(self.write_bcm_pin, 1)
        self.status = int(new_status)


    def get_start_time(self):
        """
        Determine the time the door should open.

        Returns:
            Datetime
        """

        return parser.parse(self.sun_data['sunrise_localtime'])

    def get_end_time(self):
        """
        Determine the time the door should close.

        Returns:
            Datetime
        """

        return parser.parse(self.sun_data['sunset_localtime'])