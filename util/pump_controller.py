import board
import digitalio


class PumpController:
    def __init__(self, pump_pin:board.pin):
        self.relay = digitalio.DigitalInOut(pump_pin)
        self.relay.direction = digitalio.Direction.OUTPUT

        self.debug = False

    def pump_on(self):
        if self.debug: print("True")
        self.relay.value = True

    def pump_off(self):
        if self.debug: print("False")
        self.relay.value = False
