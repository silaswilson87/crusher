import board
import digitalio
import analogio
import time
import os

from pumping_controller import PumpingController
from util.debug import Debug
from util.pump_controller import PumpController
from util.water_level import WaterLevelReader

debug = Debug()

# Create the pump control object
# Can be any GPIO pin, match accordingly
pump = PumpController(board.D5)

# Create the three (bottom, middle, and top), water sensor controllers
# Needs all the A pins, match bottom, middle, top sensors accordingly
water_level_readers = [WaterLevelReader(board.A0, board.A1, debug),  # Bottom sensor
                       WaterLevelReader(board.A2, board.A3, debug),  # Middle sensor
                       WaterLevelReader(board.A4, board.A5, debug)]  # Top sensor

# Create the pumping controller
pumping = PumpingController(board.LED, pump, water_level_readers, debug)

while True:
    debug.check_debug_enable()
    # Communicate with remote and check current water level state,
    # and turn on/off pump according to water level.
    pumping_state = pumping.check_state()
    debug.print_debug("Pumping State: "+pumping_state)
    if debug.is_debug():
        time.sleep(20)
    else:
        time.sleep(60)


