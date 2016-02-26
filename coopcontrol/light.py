from simple import Simple
from dateutil import parser, tz
import logging

class Light(Simple):
    """Control the light status, on or off"""

    def __init__(self,settings_file):
        Simple.__init__(self,settings_file)

        self.on_string  = "on"
        self.off_string = "off"

        self.get_status()

    def get_start_time(self):
        """
        Determine the time the light should turn on.

        Returns:
            Datetime
        """

        # no extra light is needed, so make the start the same as the end
        if self.sun_data['light_on_localtime'] == 0:
            return self.get_end_time()

        return parser.parse(self.sun_data['light_on_localtime'])

    def get_end_time(self):
        """
        Determine the time the light should turn off.

        Returns:
            Datetime
        """

        return parser.parse(self.sun_data['sunrise_localtime'])