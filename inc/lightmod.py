# Helper functions for managing the lights on the appropriate pin
#
import wiringpi2 as wiringpi
import coop_settings

class Light:

    currentstate = -1

    # this is for convenience in reading; basically you set the relay pin to "low" for "active"
    # and set the pin to "high" to make it "inactive"
    on  = 0 # or low
    off = 1 # or high

    def __init__(self):
        self.getlight()

    def getlight(self):
        wiringpi.wiringPiSetup()
        wiringpi.pinMode(coop_settings.pin_lights, 1) # output mode
        self.currentstate = wiringpi.digitalRead(coop_settings.pin_lights)
        return self.currentstate

    def changelight(self,newstate):
        wiringpi.wiringPiSetup()
        wiringpi.pinMode(coop_settings.pin_lights, 1) # output mode

        if newstate == self.on:
            coop_settings.appendLog('light','setting pin#'+str(coop_settings.pin_lights)+' to on')
            wiringpi.digitalWrite(coop_settings.pin_lights, self.on)
            self.currentstate = newstate
        else:
            coop_settings.appendLog('light','setting pin#'+str(coop_settings.pin_lights)+' to off')
            wiringpi.digitalWrite(coop_settings.pin_lights, self.off)
            self.currentstate = newstate
