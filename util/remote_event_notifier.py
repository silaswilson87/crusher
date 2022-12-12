import json

import uuid
import ipaddress
import ssl
import wifi
import socketpool
import adafruit_requests
from util.debug import Debug

class RemoteEventNotifier:
    def __init__(self, debug:Debug):
        self.remote_url = None
        self.event_id = None
        self.debug = debug
        self.read_defaults()
        self.connect()

    def read_defaults(self):
        try:
            # Reads json file and creates if json file doesn't exist
            with open('secrets.json', ) as f:
                self.defaults = json.load(f)
        except Exception as e:
            # print ("Let's just ignore all exceptions, like this one: %s" % str(e))
            print ("WARNING: Didn't read secrets.json, using default values. Error: %s" % str(e) )
            self.defaults = {
                "ssid":"Fios-4LC2c",
                "password":"password",
                "remote_url": "http:192.168.1.100:/"
            }
            # Can't write to the feather file system
            # with open('defaults.json', 'w', encoding='utf-8') as f:
            #     json.dump(self.defaults, f, ensure_ascii=False, indent=4)

        self.remote_url = self.defaults["remote_url"]
        self.debug.print_debug("read_defaults: ssid[%s], password[%s], remote_url[%s]" % \
                         (self.defaults["ssid"], self.defaults["password"], self.defaults["remote_url"]))

        self.debug.print_debug("Available WiFi networks:")

        for network in wifi.radio.start_scanning_networks():
          self.debug.print_debug("\t%s\t\tRSSI: %d\tChannel: %d" % (str(network.ssid, "utf-8"), network.rssi, network.channel))
        wifi.radio.stop_scanning_networks()
        self.connect()
        return self.defaults

    def connect(self):
        try:
            self.debug.print_debug("Connecting to %s" % self.defaults["ssid"])
            wifi.radio.connect(self.defaults["ssid"], self.defaults["password"])
            self.debug.print_debug("Connected to %s!" % self.defaults["ssid"])
            self.debug.print_debug("My IP address is "+wifi.radio.ipv4_address)
        except Exception as e:
            print ("WARNING: Didn't connect to wifi. Error: %s" % str(e) )
            raise e
        try:
            pool = socketpool.SocketPool(wifi.radio)
            return adafruit_requests.Session(pool, ssl.create_default_context())
        except Exception as e:
            print ("WARNING: Didn't create session. Error: %s" % str(e) )
            raise e

    def do_post(self, path:str, payload):
        try:
            eventid = str(uuid.uuid4())
            response = self.connect().post(self.remote_url + "/"+ eventid + path, payload)
            self.debug.print_debug("get return code "+response.status_code)
            return (response.status_code,response.text)
        except Exception as e:
            self.debug.print_debug("do_post exception " + str(e))
            raise e

    def do_get(self, path:str):
        try:
            eventid = str(uuid.uuid4())
            response = self.connect().get(self.remote_url + "/"+ eventid + path)
            print("get return code "+response.status_code)
            return (response.status_code,response.text)
        except Exception as e:
            self.debug.print_debug("do_get exception " + str(e))
            raise e

    def send_status_handshake(self, status):
        self.debug.print_debug("send_status_handshake "+str(status))
        return self.do_post("/status",status)


    def send_pumping_canceled_ack(self):
        self.debug.print_debug("send_pumping_canceled_ack")
        return self.do_post("/pumping_canceled_ack",self.generate_default_post_body())

    def send_start_pumping_ack(self):
        self.debug.print_debug("send_start_pumping_ack")
        return self.do_post("/start_pumping_ack",self.generate_default_post_body())

    def send_stop_pumping_ack(self):
        self.debug.print_debug("send_stop_pumping_ack")
        return self.do_post("/stop_pumping_ack",self.generate_default_post_body())

    def send_ready_to_pump(self):
        self.debug.print_debug("send_ready_to_pump")
        return self.do_post("/read_to_pump",self.generate_default_post_body())

    def start_pumping(self):
        self.debug.print_debug("start_pumping")
        return self.do_post("/start_pumping",self.generate_default_post_body())

    def pumping_confirmed(self):
        self.debug.print_debug("pumping_confirmed")
        return self.do_post("/pumping_confirmed",self.generate_default_post_body())

    def pumping_finished(self):
        self.debug.print_debug("pumping_finished")
        return self.do_post("/pumping_finished",self.generate_default_post_body())

    def missed_pumping_verification(self):
        self.debug.print_debug("missed_pumping_verification")
        return self.do_post("/missed_pumping_verification",self.generate_default_post_body())

    def generate_default_post_body(self):
        return {
            "parent_event_id": self.event_id
        }
