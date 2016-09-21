import wiringpi2 as wiringpi
import logging
import json
from os import path

class Simple:
    """Control a simple output pin: current status, on, or off"""

    # this is for convenience in reading; basically you set the relay pin to "low" for "active"
    # and set the pin to "high" to make it "inactive"
    ON  = 0 # or low
    OFF = 1 # or high

    def __init__(self,settings_file):
        """
        Given the provided settings file, initilize our object for manipulating
        the equipment on this rapsberry pi.

        Args:
            settings_file: JSON file for PIN IDs, data log locations

        Raises:
            IOError on file errors
        """

        self.status        = -1
        self.write_bcm_pin = -1
        self.read_bcm_pin  = -1
        self.on_string     = ""
        self.off_string    = ""

        # read the provided settings JSON file for all our details
        with open(settings_file,'r') as f:
            settings_data = json.load(f)
        f.close

        # if unspecified, all logs and data defaults to the same place as the settings file
        if 'data-directory' in settings_data and settings_data['data-directory']:
            self.data_path = path.abspath(settings_data['data-directory'])
        else:
            self.data_path = path.dirname(settings_file)

        if 'log-level' in settings_data:
            loglevel = getattr(logging, settings_data['log-level'].upper(), logging.INFO)
        else:
            loglevel = logging.INFO

        logfile = path.join(self.data_path,'equipment-log.txt')

        logging.basicConfig(filename=logfile,
                            level=loglevel,
                            format='%(asctime)s; %(levelname)s; %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')

        self.read_sun_data()

        shortname = self.__class__.__name__.lower()
        if shortname+'-bcm-pin' in settings_data:
            self.write_bcm_pin = settings_data[shortname+'-bcm-pin']

        if shortname+'-read-bcm-pin' in settings_data:
            self.read_bcm_pin = settings_data[shortname+'-read-bcm-pin']
        else:
            self.read_bcm_pin = self.write_bcm_pin


    def get_status_name(self,num_status=-1):
        if num_status == -1:
            num_status = self.status

        if num_status == 1:
            return self.on_string

        if num_status == 0:
            return self.off_string

        return "undefined"

    def get_status(self):
        """
        Get the current status of this object.

        Returns:
            0 for closed
            1 for open
        """

        self.init_input()

        # we have to translate the pin reading to a status
        self.status = int(wiringpi.digitalRead(self.read_bcm_pin) == self.ON)
        return self.status


    def set_status(self,new_status):
        """
        Set the state of the object to open or closed, if its not already in that state.

        Args:
            new_status: 0 for closed/off, 1 for open/on.
        """

        if self.status == new_status:
            return

        self.init_output()

        if new_status == 1:
            logging.info('setting pin#%s to on',str(self.write_bcm_pin))
            wiringpi.digitalWrite(self.write_bcm_pin, self.ON)
        else:
            logging.info('setting pin#%s to off',str(self.write_bcm_pin))
            wiringpi.digitalWrite(self.write_bcm_pin, self.OFF)

        self.status = int(new_status)


    def init_output(self):
        """Set the pin as output mode"""

        wiringpi.wiringPiSetupSys()
        wiringpi.pinMode(self.write_bcm_pin, 1) # output mode

    def init_input(self):
        """Set the pin as input mode"""

        wiringpi.wiringPiSetupSys()
        wiringpi.pinMode(self.read_bcm_pin, 0) # input mode

    def read_sun_data(self):
        """
        Read the sunrise and sunset data from the cache file

        Returns:
            True on file read, False if not

        Raises:
            IOError on file errors
        """

        file = path.join(self.data_path,'sunrise_data.json')

        try:
            with open(file,'r') as f:
                data = json.load(f)
            f.close
        except IOError as e:
            logging.warning('error: %s', e.strerror)
            return False

        self.sun_data = data
        return True

