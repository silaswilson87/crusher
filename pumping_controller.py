import time

import board
import digitalio

from util.debug import Debug
from util.pump_controller import PumpController
from util.remote_event_notifier import RemoteEventNotifier
from util.simple_timer import Timer
from util.water_level import WaterLevelController

bottom = 0
middle = 1
top = 2


class PumpingController:
    IDLE = "idle"
    READY_TO_PUMP = "ready"
    PUMPING_CANCELED = "canceled"
    PUMPING_STOPPED = "stopped"
    PUMPING_STARTED = "started"
    START_PUMPING = "start"
    STOP_PUMPING = "stop"
    PUMPING = "pumping"
    PUMPING_VERIFY   = "verify"
    PUMPING_VERIFIED = "verified"
    PUMPING_TIMED_OUT = "timed_out"
    UNKNOWN = "unknown"
    seconds_to_wait_for_pumping_verification = 300  # 5 Minutes

    def __init__(self, led: board.pin, pump: PumpController, water_levels: list[WaterLevelController], debug:Debug):
        self.led = digitalio.DigitalInOut(led)
        self.led.direction = digitalio.Direction.OUTPUT
        self.unknown_count = 0
        self.pump = pump
        self.water_levels = water_levels
        self.pumping_started_flag = False
        self.pumping_verified = False
        self.last_pump_state = self.IDLE
        self.debug = debug
        self.remote_notifier = RemoteEventNotifier(debug)
        self.timer = Timer()


    def stop_pumping(self):
        self.debug.print_debug("****stop_pumping****")
        self.pump.pump_off()
        self.timer.cancel_timer()
        self.last_pump_state = self.IDLE
        self.pumping_started_flag = False
        self.pumping_verified = False

    def blink(self):
        for times in range(0, 2):
            # three quick blinks
            for blink in range(0, 4):
                self.led.value = True
                time.sleep(0.05)
                self.led.value = False
                time.sleep(0.05)

            # one longer blink
            self.led.value = True
            time.sleep(0.5)
            self.led.value = False
            time.sleep(0.1)

    def create_status_object(self):
        water_level_state = self.get_water_state(self.pumping_started_flag, self.pumping_verified)
        return {
            "water_level_state":water_level_state,
            "pump_running":str(self.pump.running),
            "pumping_started_flag":str(self.pumping_started_flag),
            "pumping_verified":str(self.pumping_verified),
            "bottom_sensor_level": self.water_levels[bottom].water_level,
            "middle_sensor_level": self.water_levels[middle].water_level,
            "top_sensor_level": self.water_levels[top].water_level
        }

    # Uses water level in the three water measurement sensors to return a water state
    def get_water_state(self, pumping_started, pumping_verified):
        bottom_has_water = self.water_levels[bottom].water_present()
        middle_has_water = self.water_levels[middle].water_present()
        top_has_water    = self.water_levels[top].water_present()

        # NOTE: The middle water_level is not used until a pumping session has started,
        #       then it's used to make sure the pump has removed some water (in case pump isn't working)
        if not bottom_has_water and not middle_has_water and not top_has_water:
            return self.IDLE

        elif not pumping_started and bottom_has_water and not top_has_water:
            return self.READY_TO_PUMP

        # Once the pumping_started flag look for the bottom to have water, but the top two to not have water.
        # This state verifies the pump is working.
        # NOTE: We use the flag pumping_verified to allow the next elif to get executed after the verification
        elif not pumping_verified and pumping_started and bottom_has_water and not middle_has_water and not top_has_water:
            return self.PUMPING_VERIFIED

        # Once the pumping_started flag set, we stay pumping until the bottom water_level has no water
        elif not pumping_started and bottom_has_water and middle_has_water and top_has_water:
            return self.PUMPING

        elif pumping_started and bottom_has_water:
            return self.PUMPING

        else:
            self.debug.print_debug("UNKOWN STATE: bottom level:[%d], middle level:[%d], top level:[%d]" % \
                         (self.water_levels[bottom].water_level, self.water_levels[middle].water_level, self.water_levels[top].water_level))
            return self.UNKNOWN

    # This is the main pumping logic method
    def check_state(self):
        self.debug.print_debug("check_state: last_pump_state[%s], pumping_started_flag[%s], pumping_verified[%s]" % \
                         (self.last_pump_state, self.pumping_started_flag, self.pumping_verified))

        if self.pumping_started_flag:
            self.debug.print_debug("Pumping Elapsed: "+self.timer.get_elapsed())

        try:
            # At the start of very loop event, check-in with remote in case it wants to change our state
            # Plus let them know our current state, so the remote can validate our current state
            # NOTE: All remote_status command must be ACKed to ensure communication is healthy.
            #       After ack is received on remote, it goes into idle state waiting for normal status processing
            #       If ack is not received within remote timeout period, a notification email or text is sent.
            remote_status = self.remote_notifier.send_status_handshake(self.last_pump_state)
            self.debug.print_debug("remote_status "+remote_status)


            if (remote_status == self.PUMPING_CANCELED):
                # Canceled happens during pumping when pump verification times out on remote, and it attempts a stop us.
                # This should only happen if there is something wrong with pump, and it's not pumping.
                # NOTE: Both sides go into idle and this side will attempt to start pumping again
                #       if the water level measurements trigger the pump.
                # This is like a reset. There is no "permanent" stop pumping.
                self.stop_pumping()
                self.remote_notifier.send_pumping_canceled_ack()
                return self.PUMPING_CANCELED
            elif (remote_status == self.START_PUMPING):
                # For what ever reason, the remote can turn on pump
                # This has not been tested to see if this code will handle gracefully
                self.last_pump_state = self.PUMPING
                self.pump.pump_on()
                self.remote_notifier.send_start_pumping_ack()
                return self.PUMPING_STARTED
            elif (remote_status == self.STOP_PUMPING):
                # Remote can signal to stop pumping at anytime
                # NOTE: Both sides go into idle and this side will start pumping again
                #       if the water level measurements trigger the pump.
                # This is like a reset. There is no "permanent" stop pumping.
                self.stop_pumping()
                self.last_pump_state = self.IDLE
                self.remote_notifier.send_stop_pumping_ack()
                return self.PUMPING_STOPPED
        except Exception as e:
            print ("WARNING: Remote communication failed. Error: %s" % str(e) )


        # Timer starts when pumping starts.
        # Timer canceled as soon as the pumping verification happens
        if self.timer.is_timed_out():
            self.debug.print_debug("TIMED OUT. Elapsed: " + self.timer.get_elapsed())
            self.stop_pumping()
            try:
                self.remote_notifier.missed_pumping_verification()
            except Exception as e:
                print("WARNING: Remote communication failed. Error: %s" % str(e))
            return self.PUMPING_TIMED_OUT

        # After remote status and timer check, it's time to read the water levels
        # and see if we need to change state, i.e. start or stop pump
        water_level_state = self.get_water_state(self.pumping_started_flag, self.pumping_verified)
        # self.debug.print_debug("water_level_state "+water_level_state)

        # If we get weird, bogus reading and water level state can't be computed, then return to try again
        if water_level_state == self.UNKNOWN:
            self.unknown_count += 1
            if self.unknown_count > 4:
                self.unknown_count = 0
                try:
                    self.remote_notifier.send_unknown_status()
                except Exception as e:
                    print("WARNING: Remote communication failed. Error: %s" % str(e))

            return self.UNKNOWN

        self.unknown_count = 0

        # If we've been pumping and the bottom water measurement has no water, stop pumping
        if self.pumping_started_flag and water_level_state == self.IDLE:
            self.stop_pumping()
            self.remote_notifier.pumping_finished()
            return self.IDLE

        # If not pumping and none of the water measurements have water, then we are IDLE and can return here
        if not self.pumping_started_flag and water_level_state == self.IDLE:
            return self.IDLE

        # If the last state was idle and now the bottom water level sensor has water, then set READY_TO_PUMP
        elif self.last_pump_state == self.IDLE and water_level_state == self.READY_TO_PUMP:
            self.last_pump_state = self.READY_TO_PUMP
            self.pumping_verified = False
            self.remote_notifier.send_ready_to_pump()
            return self.READY_TO_PUMP

        # If the last state was READY_TO_PUMP and the top water level still has no water, then keep READY_TO_PUMP
        # Note: This elif gets executed many times until the top water measurement has water, and we start pumping.
        elif self.last_pump_state == self.READY_TO_PUMP and water_level_state == self.READY_TO_PUMP:
            self.last_pump_state = self.READY_TO_PUMP
            return self.READY_TO_PUMP

        # If we haven't started pumping and the last pump state is READY_TO_PUMP and
        # the top water measurement sensor has water, start pumping
        elif self.last_pump_state == self.READY_TO_PUMP and water_level_state == self.PUMPING:
            # WHen we start pumping, then start pumping verification timer
            self.debug.print_debug("starting timer")
            self.timer.start_timer(self.seconds_to_wait_for_pumping_verification)
            # Drop through and start pumping

        # It's possible to turn on and be ready to pump
        elif self.last_pump_state == self.IDLE and water_level_state == self.PUMPING:
            # WHen we start pumping, then start pumping verification timer
            self.debug.print_debug("starting timer")
            self.timer.start_timer(self.seconds_to_wait_for_pumping_verification)
            # Drop through and start pumping

        # After pumping has started, wait for the pumping verification.
        # The middle water measurement sensor should be fairly physically close to the top water measurement sensor,
        #      the water doesn't have to go down much to validate the pump is moving water out.
        # There is a flag to avoid doing this a second time.
        # NOTE: You should probably time how long it takes the pump to lower the water below the middle water
        #            measurement and set seconds_to_wait_for_pumping_verification accordingly.
        #            The timeout default is 5 minutes.
        elif not self.pumping_verified and \
                self.last_pump_state == self.PUMPING and water_level_state == self.PUMPING_VERIFIED:
            self.last_pump_state = self.PUMPING_VERIFIED
            # When we get the pumping verification, turn off timer (we don't need it anymore)
            self.timer.cancel_timer()
            self.remote_notifier.pumping_confirmed()
            self.pumping_verified = True
            # We didn't stop pump, we are still pumping, return that the verification state has been reached
            self.blink()
            return self.PUMPING_VERIFIED

        # In pumping state
        # Only blink when pumping
        self.pumping_started_flag = True
        self.last_pump_state = self.PUMPING
        self.pump.pump_on()
        self.blink()
        return self.PUMPING
