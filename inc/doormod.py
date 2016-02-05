# Helper functions for managing the door on the appropriate pin
#
from time import sleep
import wiringpi2 as wiringpi
import coop_settings

class Door:

    currentstate = -1

    def __init__(self):
        self.getdoor()

    # check the door's current state; we are just manually saving this data to a file
    # since there is no other way to know if the door was last opened or closed
    # TODO: replace this with a contact switch to get real data
    def getdoor(self):
        try:
            with open(coop_settings.doorstate_file,'r') as f:
                doorstate = f.readline()
                self.currentstate = doorstate.strip()
            f.close
        except IOError:
            self.currentstate = 0
        return self.currentstate

    # function for managing the door open/close state
    # technically, we don't know if the door is already opened or closed
    # this function just turns the motor for a few seconds regardless
    def changedoor(self,newstate):
        wiringpi.wiringPiSetup()
        wiringpi.pinMode(coop_settings.pin_door, 1) # output mode

        if newstate == 1: #open
            coop_settings.appendLog('door','opening the door')
        else:
            coop_settings.appendLog('door','closing the door')

        try:
            with open(coop_settings.doorstate_file,'w') as f:
              f.write(str(newstate))
            f.close
        except IOError as e:
            print file, ' error: ', e.strerror
            sys.exit(1)

        # low turns the motor on
        wiringpi.digitalWrite(coop_settings.pin_door, 0)
        # wait for it to finish running - a bigger door would require more to complete
        sleep(15)
        # high turns the motor back off so that it can run again later
        wiringpi.digitalWrite(coop_settings.pin_door, 1)
        self.currentstate = newstate