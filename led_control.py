import machine
import neopixel
import time
import math

try:
    from nv_led_config import MAX_BRIGHTNESS
except:
    MAX_BRIGHTNESS = 0.15

STEPS = 80
STEP_SIZE = math.pi/STEPS/2

DINO_HEAD_NECK = 6
DINO_HEAD_OFFSET = 20


class LED_Control(object):
    def __init__(self, pixel_length, data_pin):
        self.pixel_length = pixel_length
        self.np = neopixel.NeoPixel(machine.Pin(data_pin), pixel_length)

        self.max_brightness = MAX_BRIGHTNESS
        self.fade_map=[]
        self.config_brightness(self.max_brightness)

        self.last_position = 0
        self.state_enable = True

    def config_brightness(self, value):
        ''' brightness 0 to 1'''
        self.max_brightness = value
        self.fade_map = [int(math.sin(x * STEP_SIZE) * 255 * value) for x in range(0, STEPS)]

        with open('nv_led_config.py', 'w') as outfile:
            outfile.write('MAX_BRIGHTNESS=%.1f' % value)

    def get_colors(self, position, pixel_offset):
        position += pixel_offset
        quadrant = int(position / STEPS) % 3
        position = position % STEPS
        if quadrant == 0:
            color_red = self.fade_map[(position) % STEPS]
            color_green = 0
            color_blue = self.fade_map[-(position+1) % STEPS]
        elif quadrant == 1:
            color_red = self.fade_map[-(position + 1) % STEPS]
            color_green = self.fade_map[(position) % STEPS]
            color_blue = 0
        elif quadrant == 2:
            color_red = 0
            color_green = self.fade_map[-(position + 1) % STEPS]
            color_blue = self.fade_map[(position) % STEPS]
        return color_red, color_green, color_blue

    def async_flow(self):
        if self.state_enable:
            self.last_position += 1
            color_red, color_green, color_blue = self.get_colors(self.last_position, 0)
            head_red, head_green, head_blue = self.get_colors(self.last_position, DINO_HEAD_OFFSET)
            for led in range(0, self.pixel_length):
                if led < DINO_HEAD_NECK:
                    self.np[led] = (head_red, head_green, head_blue)
                else:
                    self.np[led] = (color_red, color_green, color_blue)
            self.np.write()

    def all_off(self):
        for led in range(0, self.pixel_length):
            self.np[led] = (0, 0, 0)
        self.np.write()

    def flow(self, timeout=0):
        time_delay = 0.025

        while True:
            for position in range(0,STEPS*3):
                color_red, color_green, color_blue = self.get_colors(position, 0)
                head_red, head_green, head_blue = self.get_colors(position, DINO_HEAD_OFFSET)
                for led in range(0, self.pixel_length):
                    if led < DINO_HEAD_NECK:
                        self.np[led] = (head_red, head_green, head_blue)
                    else:
                        self.np[led] = (color_red, color_green, color_blue)
                self.np.write()
                time.sleep(time_delay)