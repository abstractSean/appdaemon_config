import appdaemon.plugins.hass.hassapi as hass
import time

class GoalLight(hass.Hass):
    def initialize(self):
        self.setting_delay = .5
        self.recorded_state = dict()
        self.goaling = False
        self.trigger = 'light.goal_light'
        lights = self.args["goal_lights"]

        for light in lights:
            self.listen_state(self.goal_start, self.trigger, old='off', new='on', light = light)
            self.listen_state(self.goal_stop, self.trigger, old='off', new='on', light = light)
            self.listen_state(self.goal_off, self.trigger, old='on', new='off', light = light)
        
    def goal_start(self, entity, attribute, old, new, kwargs):
        light = kwargs['light']
        self.save_state(light)
        self.goaling = True
        self.turn_on(light)

        while self.goaling:
            time.sleep(.25)
            self.call_service('homeassistant/turn_on',
                              entity_id=light, 
                              rgb_color=[255, 0, 0],
                              brightness=255,
                              transition=1.0,
                             )
            time.sleep(1.25)
            self.turn_off(light)

    def goal_stop(self, entity, attribute, old, new, kwargs):
        time.sleep(30)
        if self.goaling:
            self.turn_off(self.trigger)
        
    def goal_off(self, entity, attribute, old, new, kwargs):
        light = kwargs['light']
        self.goaling = False
        time.sleep(1)
        self.restore_state(light)

    def save_state(self, entity):
        saved_state = dict()
        saved_attributes = dict()

        saved_state['state'] = self.get_state(entity)
        if saved_state['state'] == 'off':
            self.turn_on(entity)
            time.sleep(self.setting_delay)

        attributes = self.get_state(entity, attribute='attributes')

        if 'brightness' in attributes:
            saved_attributes['brightness'] = attributes['brightness']
        if 'rgb_color' in attributes:
            saved_attributes['rgb_color'] = attributes['rgb_color']
        elif 'hs_color' in attributes:
            saved_attributes['hs_color'] = attributes['hs_color']
        elif 'xy_color' in attributes:
            saved_attributes['xy_color'] = attributes['xy_color']

        saved_state['attributes'] = saved_attributes
        self.recorded_state[entity] = saved_state

        self.log(f'Saved {entity}')

    def restore_state(self, entity):
        if entity not in self.recorded_state:
            self.log(f'No saved state for {entity}')
            return False

        saved = self.recorded_state[entity]

        if self.get_state(entity) == 'off':
            self.turn_on(entity)

        status = self.call_service('homeassistant/turn_on',
                                   entity_id=entity, 
                                   **saved['attributes']
                                  )

        if saved['state'] == 'off':
            time.sleep(self.setting_delay)
            self.turn_off(entity)

        self.log(f'Restored {entity}')

