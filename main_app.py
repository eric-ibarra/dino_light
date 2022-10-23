import machine
import network
import time

from uos import uname
from machine import Pin, PWM
from umqttsimple import MQTTClient, MQTTException
import ubinascii

from network_config import SSID, PHRASE
from mqtt_config import MQTT_SERVER, MQTT_USER, MQTT_PW, CONFIG_SERVER
from ota_update import check_update_needed, download_app

from led_control import LED_Control
from version import APP_VERSION

APP_FILES = ['main_app.py', 'ota_update.py', 'led_control.py', 'umqttsimple.py', 'version.py']

client_id = ubinascii.hexlify(machine.unique_id())
topic_sub = b'dino_light'
topic_pub = b'hello'

last_message = 0
message_interval = 1


BRIGHTNESS_INCREMENT = 0.1
#D_IO = [i for i in range(0,10)]
IO_APP_PIN = 15
NEOPIXEL_DATA_PIN = 13

DINO_LENGTH = 22

class wlan(object):
    def __init__(self):
        self.sta_if = None
        self.active = lambda x: x

        self.mac_addr = None

    def connect_network(self):
        self.sta_if = network.WLAN(network.STA_IF)
        #self.sta_if.ifconfig(('192.168.86.44', '255.255.255.0', '192.168.86.1', '8.8.8.8'))
        self.sta_if.active(True)

        mac = self.sta_if.config('mac')
        mac_addr = 0
        for byte in mac:
            mac_addr <<= 8
            mac_addr |= byte
        self.mac_addr = mac_addr

        self.sta_if.connect(SSID, PHRASE)
        self.active = self.sta_if.active

        count = 50
        while not self.sta_if.isconnected() and count:
            time.sleep(0.1)
            count -= 1


def run_app(platform_type, mac_addr):
    global last_message, message_interval, client
    global led

    print('run app')
    led = LED_Control(DINO_LENGTH, NEOPIXEL_DATA_PIN)

    print('enable pwm')
    Pin(2, Pin.OUT, value=1)
    pwm0 = PWM(Pin(2))
    pwm0.freq(2)
    pwm0.duty(500)

    try:
        client = connect_and_subscribe(mac_addr)
    except MQTTException as e:
        print('MQTT exception')
        print(e)
    except OSError as e:
        print(e)
        restart_and_reconnect()

    while True:
        try:
            if (time.time() - last_message) > message_interval:
                client.check_msg()
                last_message = time.time()
        except Exception as e:
            restart_and_reconnect()
        led.async_flow()
        time.sleep(0.025)

def user_main(reset_reason):
    global wifi

    platform_type = uname().sysname
    print('run app')
    try:
        wifi = wlan()
        wifi.connect_network()
    except OSError as e:
        print(e)
        restart_and_reconnect()

    print('Connection successful %d' % wifi.mac_addr)
    print(wifi.sta_if.ifconfig())

    # Check for OTA updates
    if check_update_needed(CONFIG_SERVER, APP_VERSION, wifi.mac_addr):
        download_app(CONFIG_SERVER, APP_FILES, wifi.mac_addr)

    run_app(platform_type, wifi.mac_addr)

# MQTT stuff
def sub_cb(topic, msg):
    global led, wifi, client
    print((topic, msg))
    if topic != topic_sub:
        return

    if msg == b'on':
        led.state_enable = True
    elif msg == b'off':
        led.state_enable = False
        led.all_off()

    elif msg == b'brightness_up':
        if led.max_brightness + BRIGHTNESS_INCREMENT < 1:
            led.config_brightness(led.max_brightness + BRIGHTNESS_INCREMENT)
        else:
            led.config_brightness(1)
    elif msg == b'brightness_down':
        if led.max_brightness - BRIGHTNESS_INCREMENT > 0:
            led.config_brightness(led.max_brightness - BRIGHTNESS_INCREMENT)
        else:
            led.config_brightness(0)
    elif msg == b'force_update':
        APP_FILES.append('%s_mqtt_config.py' % wifi.mac_addr)
        download_app(CONFIG_SERVER, APP_FILES, wifi.mac_addr)
    elif msg == b'version':
        msg = b'%s: %d' % (wifi.mac_addr, APP_VERSION)
        client.publish(b'response', msg)


def connect_and_subscribe(mac_addr):
    global client_id, topic_sub
    topic_sub = b'%s/dino_light' % mac_addr
    client = MQTTClient(client_id, MQTT_SERVER, 0, MQTT_USER, MQTT_PW)
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(topic_sub)
    print('Connected to %s MQTT broker, subscribed to %s topic' % (MQTT_SERVER, topic_sub))
    return client

def restart_and_reconnect():
    print('Failed to connect to MQTT broker. Reconnecting...')
    time.sleep(10)
    machine.reset()
