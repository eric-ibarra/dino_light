import machine
import neopixel
import time
import math

STEPS = 80
STEP_SIZE = math.pi/STEPS/2

DINO_HEAD_NECK = 6
DINO_HEAD_OFFSET = 20


class LED_Control(object):
    def __init__(self, pixel_length, data_pin):
        self.pixel_length = pixel_length
        self.np = neopixel.NeoPixel(machine.Pin(data_pin), pixel_length)

        self.max_brightness = 0.15 # was 0.75
        self.fade_map=[]
        self.config_brightness(self.max_brightness)

    def config_brightness(self, value):
        ''' brightness 0 to 1'''
        self.max_brightness = value
        self.fade_map = [int(math.sin(x * STEP_SIZE) * 255 * value) for x in range(0, STEPS)]

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

    def flow(self, timeout=0):
        pixel_offset = 0
        loops=5
        time_delay = 0.025

        #for i in range(0, loops):
        while True:
            #red
            for position in range(0,STEPS*3):
                #color_blue = self.fade_map[-(position + pixel_offset+1) % STEPS]
                #color_red = self.fade_map[(position + pixel_offset) % STEPS]
                color_red, color_green, color_blue = self.get_colors(position, 0)
                head_red, head_green, head_blue = self.get_colors(position, DINO_HEAD_OFFSET)
                for led in range(0, self.pixel_length):
                    if led < DINO_HEAD_NECK:
                        self.np[led] = (head_red, head_green, head_blue)
                    else:
                        self.np[led] = (color_red, color_green, color_blue)
                self.np.write()
                time.sleep(time_delay)
            '''
            #green
            for position in range(0,STEPS):
                color_red = self.fade_map[-(position + pixel_offset+1) % STEPS]
                color_green = self.fade_map[(position + pixel_offset) % STEPS]
                for led in range(0, self.pixel_length):
                    self.np[led] = (color_red, color_green, 0)
                self.np.write()
                time.sleep(time_delay)
            # blue
            for position in range(0,STEPS):
                color_green = self.fade_map[-(position + pixel_offset+1) % STEPS]
                color_blue = self.fade_map[(position + pixel_offset) % STEPS]
                for led in range(0, self.pixel_length):
                    self.np[led] = (0, color_green, color_blue)
                self.np.write()
                time.sleep(time_delay)
            '''


        #for position in range(0, STEPS*loops):
        #    for led in range(0, self.pixel_length):
        #        self.np[led] = (fade_map[(position + pixel_offset)%STEPS], fade_map[(position + pixel_offset + 120)%STEPS], fade_map[(position + pixel_offset + 240)%STEPS])
        #    self.np.write()
        #    time.sleep(0.1)