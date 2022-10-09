import machine
import network
import time

from uos import uname
from machine import Pin, PWM

from network_config import SSID, PHRASE
from led_control import LED_Control

#D_IO = [i for i in range(0,10)]
IO_APP_PIN = 15
NEOPIXEL_DATA_PIN = 13

DINO_LENGTH = 22

class wlan(object):
    def __init__(self):
        self.sta_if = None
        self.active = lambda x: x

    def connect_network(self):
        self.sta_if = network.WLAN(network.STA_IF)
        self.sta_if.ifconfig(('192.168.86.44', '255.255.255.0', '192.168.86.1', '8.8.8.8'))
        self.sta_if.active(True)

        self.sta_if.connect(SSID, PHRASE)
        self.active = self.sta_if.active

        count = 50
        while not self.sta_if.isconnected() and count:
            time.sleep(0.1)
            count -= 1

def run_app(platform_type):
    print('enable pwm')
    Pin(2, Pin.OUT, value=1)
    pwm0 = PWM(Pin(2))
    pwm0.freq(2)
    pwm0.duty(500)

    wlan_if = wlan()
    wlan_if.connect_network()

def user_main(reset_reason):
    run_app_flag = machine.Pin(IO_APP_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
    time.sleep(0.10)
    #time.sleep(5)

    #if reset_reason == machine.DEEPSLEEP_RESET:
    #    print('woke from a deep sleep')
    #elif reset_reason == machine.PWRON_RESET:
    #    set_pwm(100)

    # only run app if run-pin is set (used for sleep modes)
    #platform_type = uname().sysname
    #if run_app_flag.value() == 0 or reset_reason == machine.DEEPSLEEP_RESET:
    #else:
    #    print('App not selected to run')
    print('run app')
    led = LED_Control(DINO_LENGTH, NEOPIXEL_DATA_PIN)
    led.flow()

    #run_app(platform_type)


def set_pwm(duty):
    pwm0 = PWM(Pin(2))
    pwm0.freq(2)
    pwm0.duty(duty)

