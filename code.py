import os
import time

import board

from pumping_controller import PumpingController
from util.button import Button
from util.debug import Debug
from util.properties import Properties
from util.pump_controller import PumpController
from util.pumping_display import PumpingDisplay
from util.simple_timer import Timer
from util.water_level import WaterLevelReader
debug = Debug()
properties = Properties(debug)


# print(str(dir(board)))

display = PumpingDisplay()
debug.check_debug_enable()
debug.print_debug("CircuitPython version " + str(os.uname().version))

# buttons = Button([board.D5, board.D6, board.D9])
# buttons = Button([board.D10, board.D6, board.D9])

# Create the pump control object
# Can be any GPIO pin, match accordingly
pump = PumpController(board.D12)

# Create the three (bottom, middle, and top), water sensor controllers
# Needs all the A pins, match bottm, middle, top sensors accord
water_level_readers = [WaterLevelReader("Bottom", properties, board.D5, board.D5, debug),  # Bottom sensor
                       WaterLevelReader("Top", properties, board.D6, board.D6, debug)]  # Top sensor

# Create the pumping controller
pumping = PumpingController(properties, board.LED, pump, water_level_readers, debug)

# response = pumping.remote_notifier.connect().get("http://wifitest.adafruit.com/testwifi/index.html")
# response = pumping.remote_notifier.do_get("http://wifitest.adafruit.com/testwifi/index.html")
# print("GET response "+response.text)

this_address = pumping.remote_notifier.ip_address

timer = Timer()

program_start_time = time.monotonic()
pump_start_time = time.monotonic()
pumping_state = "Not Started"
loop_count = 0
timer.start_time = None
while True:
    # debug.print_debug("Timer elapsed " + str(timer.get_elapsed())+" -- is timing "+str(timer.is_timing()))
    loop_count += 1
    debug.check_debug_enable()
    if (timer.is_timed_out()):
        # If the pump isn't functional, the server side will send out a notification after its timeout.
        # This if adds a second timeout. The incoming water rate is very slow.
        # An extra minute gives everything an extra chance to function as expected.
        time.sleep(properties.defaults["sleep_seconds"])
        # Timeout code below waits for "sleep_seconds" seconds, then we start over,
        # if pumping isn't verified successfully, the code below will wait another 60 seconds.
        # The timeout loop will loop for forever or until pumping verification is successful .
        timer.cancel_timer()
    # Communicate with remote and check current water level state, and turn on/off pump according to water level.
    try:
        pumping_state = pumping.check_water_level_state()
        http_status = "#%sC:%sE#:%d" % (
        "{:,}".format(pumping.remote_notifier.transaction_count), pumping.remote_notifier.last_status_code,
        pumping.remote_notifier.error_count)
        display.display_status(this_address, pumping_state, program_start_time, pump_start_time, water_level_readers, http_status)
        if pumping_state == pumping.REMOTE_NOTIFIER_ERROR:
            display.display_error(pumping.error_string)
            # This is a hard error. Getting an event id is required.
            # Restart the pumping life cycle, go back to idle
            pumping_state = pumping.IDLE
            timer.cancel_timer()
        elif pumping_state == pumping.ENGAGE_PUMP or pumping_state == pumping.PUMPING_VERIFIED:
            if not timer.is_timing():
                timer.start_timer(properties.defaults["sleep_seconds_timeout"])
            pump_start_time = time.monotonic()
            # time.sleep(1) # When pumping, check water status often as the pump removes water quickly
            continue
        elif pumping_state == pumping.PUMPING_TIMED_OUT:
            # timer.start_timer(pumping.seconds_to_wait_for_pumping_verification)
            display.display_error(
                "Pumping verification timed out. Wait`                                                                `ing to check pump")
            time.sleep(properties.defaults["sleep_seconds_timeout"])
            continue
        elif pumping_state == pumping.IDLE:
            timer.cancel_timer()

    except Exception as e:
        error = str(e)
        display.display_error(error)
        print("ERROR: pumping failed. Error: %s" % error)
        pumping_state = "error"
        time.sleep(20)
        continue

    debug.print_debug("Pumping State: " + pumping_state)

    pumping.wait_for_water_level_state_change(debug, properties)
    # if debug.is_debug():
    #     target_elapsed = properties.defaults["sleep_seconds_debug"]
    # else:
    #     target_elapsed = properties.defaults["sleep_seconds"]
    #time.sleep(target_elapsed)

    # start = time.time()
    # end = time.time()
    # while end - start < target_elapsed:
    #     if(buttons.button_pushed()):
    #         print("core - button pressed")
    #     time.sleep(1)
    #     end = time.time()
