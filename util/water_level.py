import board
import digitalio
import analogio
import time

from util.debug import Debug

LOW_VALUE = 36000
EMPTY_VALUE = 11000


class WaterLevelController:
    DRY = "dry"
    WET = "wet"

    def __init__(self, enable_pin:board.pin,water_level_pin:board.pin, debug:Debug):
        self.water_enable = digitalio.DigitalInOut(enable_pin)
        self.water_enable.switch_to_output()
        self.water_level_sensor = analogio.AnalogIn(water_level_pin)
        self.debug = debug
        self.water_level = None
        self.dry_level = EMPTY_VALUE
        self.wet_level = LOW_VALUE

    # Allows the outside to easily tweak the on/off level triggers if/when defaults don't work for a give sensor
    def set_dry_wet(self, dry: int, wet: int):
        self.dry_level = dry
        self.wet_level = wet

    def get_water_level(self):
        self.water_enable.value = True
        self.water_level = self.water_level_sensor.value
        self.water_enable.value = False
        self.debug.print_debug("water level value "+str(self.water_level))
        return self.water_level

    def get_water_state(self):
        level = self.get_water_level()
        if level <= self.dry_level:
            return self.DRY
        return self.WET

    def water_present(self):
        water_present = self.get_water_state() != self.DRY
        return water_present
