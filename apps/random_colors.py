from colorsys import hls_to_rgb

import appdaemon.appapi as appapi
import appdaemon.plugins.hass.hassapi as hass
import random
import time

class RandomColors(hass.Hass, appapi.AppDaemon):
    def initialize(self):
        self.log("Init RandomColors with args: {}".format(self.args))
        self.control = self.get_app('LightControl')
        self.control.init(self.args)
        lights = self.args['lights']
        self.trigger = self.args['trigger']

        if 'offset' in self.args:
            self.offset = self.args['offset']
        else:
            self.offset = 0
       
        

        for light in lights:
            self.listen_state(self.light_start, self.trigger, old='off', new='on', light = light)
            self.listen_state(self.control.light_stop, self.trigger, old='off', new='on', light = light)
            self.listen_state(self.control.light_off, self.trigger, old='on', new='off', light = light)

    def light_start(self, entity, attribute, old, new, kwargs):
        light = kwargs['light']
        self.control.save_state(light)
        self.control.lighting = True

        self.brightness = self.get_state(self.trigger,
                                         attribute='brightness')


        if self.brightness and self.brightness < 255:
            self.bpm = self.brightness * (100/255)
            self.control.off_delay = 60 / self.bpm

        time.sleep(self.offset)
        hue = random.uniform(0.0, 1.0)
        while self.control.lighting:
            # change to a color at least +/- 0.2 different
            hue += random.uniform(0.2, 0.8)
            hue %= 1.0
            # bold colors only
            lightness = 0.5 #random.uniform(0.45, 0.5)
            saturation = 1 #random.uniform(0.75, 1.0)
            rgb = hls_to_rgb(hue, lightness, saturation)
            color = [int(255*c) for c in rgb] 

            self.control.light_flash(light,
                             color,
                             self.control.brightness,
                             self.control.on_delay,
                             self.control.transition,
                             self.control.off_delay,
                            )
