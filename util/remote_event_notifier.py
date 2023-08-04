import gc
import json
# import uuid
import ipaddress
import ssl
import microcontroller
import socketpool
import adafruit_requests
import wifi
import time
from util.debug import Debug
from util.properties import Properties


class RemoteEventNotifier:
    def __init__(self, properties: Properties, debug: Debug):
        self.properties = properties
        self.transaction_count = 0
        self.error_count = 0
        self.debug = debug
        self.requests = None
        self.debug.print_debug("init in RemoteEventNotifier")
        self.ip_address = "None"
        self.event_id = 0
        self.remote_url = self.properties.defaults["remote_url"]
        self.properties.read_defaults()
        self.last_status_code = "N"
        self.last_error = "N"
        # dies early if can't connect to wifi, sets ip_address if connected
        self.pool = socketpool.SocketPool(wifi.radio)

        self.connect()
        self.do_hello()

    def connect(self):
        self.requests = adafruit_requests.Session(self.pool, ssl.create_default_context())
        while not wifi.radio.ipv4_address:
            self.debug.print_debug("\n===============================")
            self.debug.print_debug("Connecting to WiFi...")
            try:
                wifi.radio.connect(self.properties.defaults["ssid"], self.properties.defaults["password"])
                self.ip_address = str(wifi.radio.ipv4_address)
                self.need_to_connect = False
                self.last_status_code = "Connected"
                self.last_error = "N"
            except ConnectionError as e:
                self.last_error = str(e)
                self.need_to_connect = True
                print("Connection Error:", e)
                print("Retrying in 10 seconds")
                time.sleep(10)
                gc.collect()
        self.debug.print_debug("Connected! Need to connect flag: " + str(self.need_to_connect) + "\n")

        # try:
        #     ssid = self.properties.defaults["ssid"]
        #     self.debug.print_debug(f"Connecting to {ssid}")
        #     wifi.radio.connect(self.properties.defaults["ssid"], self.properties.defaults["password"])
        #     self.ip_address = str(wifi.radio.ipv4_address)
        # except Exception as e:
        #     print ("WARNING: Didn't connect to wifi. Error: %s" % str(e) )
        #     self.ip_address = "NOT FOUND"
        #     raise e
        # try:
        #     pool = socketpool.SocketPool(wifi.radio)
        #     for network in wifi.radio.start_scanning_networks():
        #         self.debug.print_debug \
        #             ("\t%s\t\tRSSI: %d\tChannel: %d" % (network.ssid, network.rssi, network.channel))
        #     wifi.radio.stop_scanning_networks()
        #     self.session =adafruit_requests.Session(pool, ssl.create_default_context())
        #     return self.session
        # except Exception as e:
        #     print ("WARNING: Didn't create session. Error: %s" % str(e) )
        #     raise e

    def do_hello(self):
        response = self.requests.get(self.remote_url + "/component/hello")
        self.debug.print_debug("Hello Response: " + response.text)
        self.transaction_count += 1

    def success(self, response):
        return response.status_code >= 200 and response.status_code < 300

    def reset_id(self):
        self.event_id = 0

    def do_post(self, api_action: str, pump_state: str, event_id_action: str, misc_status):
        self.debug.print_debug("POST")
        # when the program starts, the water level can be in any kind of state,
        # this logic tries to synchronize some of the unknowns
        if self.need_to_connect:
            self.connect()

        headers = {'Content-Type': 'application/json'}
        post_body = {}
        # Don't change the contents of post_body without coordinating with the server side
        post_body["action"] = api_action
        post_body["eventId"] = self.event_id
        post_body["pumpState"] = pump_state
        post_body["componentId"] = "1"
        post_body["miscStatus"] = misc_status
        post_body["errorCount"] = str(self.error_count)
        post_body["lastError"] = self.last_error
        self.debug.print_debug("post_body " + str(post_body))
        # eventid = str(uuid.uuid4())
        url = '{}/component/mission?mission=Pump1Mission'.format(self.remote_url)
        self.debug.print_debug("Post url: " + url)

        tries = 0
        # Wi-Fi can be a little flaky so try a few times before recording an error
        while tries < 5:
            try:
                response = self.requests.post(url=url, headers=headers, data=json.dumps(post_body))
                self.debug.print_debug("post response code: " + str(response.status_code) + " text " + response.text)
                # return (response.status_code,response.text)
                self.last_status_code = str(response.status_code)
                self.transaction_count += 1
                return response
            except Exception as e:
                tries += 1
                self.last_error = str(e)
                time.sleep(3)

        self.debug.print_debug("do_post exception  " + " error " + self.last_error)
        self.need_to_connect = True
        self.error_count += 1
        if self.error_count > 200:
            microcontroller.reset()  # When 200 error threshold is hit, then reboot the device.

    def do_get(self, api_verb: str):
        self.debug.print_debug("GET")
        if self.need_to_connect:
            self.connect()

        url = '{}/component/mission?mission=Pump1Mission&component_id=1&event_id={}&verb={}}'.format(
            self.remote_url, self.event_id, api_verb)
        self.debug.print_debug("Get url: " + url)

        tries = 0
        # Wi-Fi can be a little flaky so try a few times before recording an error
        while tries < 5:
            try:
                response = self.requests.get(url)
                self.debug.print_debug("get return code " + str(response.status_code) + " text " + response.text)
                self.last_status_code = str(response.status_code)
                self.transaction_count += 1
                return response
            except Exception as e:
                tries += 1
                self.last_error = str(e)
                self.last_status_code = "E"
                self.need_to_connect = True
                time.sleep(3)

        self.debug.print_debug("do_post exception  " + " error " + self.last_error)
        self.need_to_connect = True
        self.error_count += 1
        if self.error_count > 200:
            microcontroller.reset()  # When 200 error threshold is hit, then reboot the device.

    def send_status_handshake(self, pump_state: str, misc_status: json):
        self.debug.print_debug("status_handshake " + str(pump_state))
        return self.do_post("status_handshake", pump_state, "", misc_status)

    def send_unknown_status(self, pump_state: str):
        self.debug.print_debug("send_unknown_status")
        return self.do_post("send_unknown_status", pump_state, "", "None")

    def send_pumping_canceled_ack(self, pump_state: str):
        self.debug.print_debug("send_pumping_canceled_ack")
        return self.do_post("pumping_canceled_ack", pump_state, "reset", "None")

    def send_start_pumping_ack(self, pump_state: str):
        self.debug.print_debug("send_start_pumping_ack")
        return self.do_post("start_pumping_ack", pump_state, "", "None")

    def send_stop_pumping_ack(self, pump_state: str):
        self.debug.print_debug("send_stop_pumping_ack")
        return self.do_post("stop_pumping_ack", pump_state, "reset", "None")

    def send_ready_to_pump(self, pump_state: str):
        # This is the point in the lifecyle where an event id is assigned.
        # We only go forward once we get the event id from the server
        self.debug.print_debug("send_ready_to_pump")
        # TODO - at some poing (when doing another deployment, change read_ to ready_
        return self.do_post("ready_to_pump", pump_state, "new", "None")

    def start_pumping(self, pump_state: str):
        self.debug.print_debug("start_pumping")
        return self.do_post("start_pumping", pump_state, "", "None")

    def pumping_confirmed(self, pump_state: str):
        self.debug.print_debug("pumping_confirmed")
        return self.do_post("pumping_confirmed", pump_state, "", "None")

    def pumping_finished(self, pump_state: str):
        self.debug.print_debug("pumping_finished")
        return self.do_post("pumping_finished", pump_state, "reset", "None")

    def missed_pumping_verification(self, pump_state: str):
        self.debug.print_debug("missed_pumping_verification")
        return self.do_post("missed_pumping_verification", pump_state, "", "None")
