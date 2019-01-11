import appdaemon.plugins.hass.hassapi as hass
from save_restore import SaveRestore
import time

class ColorFlash(hass.Hass, SaveRestore):
    def initialize(self):
        self.setting_delay = .25
        self.recorded_state = dict()
        self.lighting = False
        self.trigger = self.args['trigger']
        self.duration = self.args['duration']
        lights = self.args['lights']

        if 'offset' in self.args:
            self.offset = self.args['offset']
        else:
            self.offset = 0

        if 'colors' in self.args:
            self.colors = self.args['colors']
        else:
            self.colors = [[255, 0, 0]]

        if 'brightness' in self.args:
            self.brightness = self.args['brightness']
        else:
            self.brightness = 255
        
        if 'on_delay' in self.args:
            self.on_delay = self.args['on_delay']
        else:
            self.on_delay = 0.25

        if 'transition' in self.args:
            self.transition = self.args['transition']
        else:
            self.transition = 1.0
        
        if 'off_delay' in self.args:
            self.off_delay = self.transition + self.args['off_delay']
        else:
            self.off_delay = 1.25

        
        for light in lights:
            self.listen_state(self.light_start, self.trigger, old='off', new='on', light = light)
            self.listen_state(self.light_stop, self.trigger, old='off', new='on', light = light)
            self.listen_state(self.light_off, self.trigger, old='on', new='off', light = light)
        
    def light_start(self, entity, attribute, old, new, kwargs):
        light = kwargs['light']
        self.save_state(light)
        self.lighting = True

        time.sleep(self.offset)
        while self.lighting:
            for color in self.colors:
                self.light_flash(light,
                                 color,
                                 self.brightness,
                                 self.on_delay,
                                 self.transition,
                                 self.off_delay,
                                )

    def light_stop(self, entity, attribute, old, new, kwargs):
        time.sleep(self.duration)
        if self.lighting:
            self.turn_off(self.trigger)
        
    def light_off(self, entity, attribute, old, new, kwargs):
        light = kwargs['light']
        self.lighting = False
        max_cycle = self.on_delay + self.transition + self.off_delay
        time.sleep(max_cycle)
        self.restore_state(light)

    def light_flash(self, light, color, brightness, on_delay, transition, off_delay):
        if self.lighting: 
            time.sleep(on_delay)
            self.call_service('homeassistant/turn_on',
                              entity_id=light, 
                              rgb_color=color,
                              brightness=brightness,
                              transition=transition,
                             )
            time.sleep(off_delay)
            if 'blink' in self.args:
                self.turn_off(light)

