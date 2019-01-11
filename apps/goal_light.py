import appdaemon.plugins.hass.hassapi as hass
from save_restore import SaveRestore
import time

class GoalLight(hass.Hass, SaveRestore):
    def initialize(self):
        self.setting_delay = .25
        self.recorded_state = dict()
        self.goaling = False
        self.trigger = self.args['trigger']
        self.duration = self.args['duration']
        lights = self.args['goal_lights']
        if 'offset' in self.args:
            self.offset = self.args['offset']
        else:
            self.offset = 0
        if 'color' in self.args:
            self.color = self.args['color']
        else:
            self.color = [255, 0, 0]

        for light in lights:
            self.listen_state(self.goal_start, self.trigger, old='off', new='on', light = light)
            self.listen_state(self.goal_stop, self.trigger, old='off', new='on', light = light)
            self.listen_state(self.goal_off, self.trigger, old='on', new='off', light = light)
        
    def goal_start(self, entity, attribute, old, new, kwargs):
        light = kwargs['light']
        self.save_state(light)
        self.goaling = True
        self.turn_on(light)
        time.sleep(self.offset)

        while self.goaling:
            time.sleep(.25)
            self.call_service('homeassistant/turn_on',
                              entity_id=light, 
                              rgb_color=self.color,
                              brightness=255,
                              transition=1.0,
                             )
            time.sleep(1.25)
            self.turn_off(light)

    def goal_stop(self, entity, attribute, old, new, kwargs):
        time.sleep(self.duration)
        if self.goaling:
            self.turn_off(self.trigger)
        
    def goal_off(self, entity, attribute, old, new, kwargs):
        light = kwargs['light']
        self.goaling = False
        time.sleep(2)
        self.restore_state(light)

