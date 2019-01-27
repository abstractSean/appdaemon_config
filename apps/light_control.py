import appdaemon.appapi as appapi
import appdaemon.plugins.hass.hassapi as hass
import time


class LightControl(hass.Hass, appapi.AppDaemon):
    def initialize(self):

        self.setting_delay = .25
        self.recorded_state = dict()
        self.lighting = False

    def init(self, args):
        self.duration = args['duration']
        self.trigger = args['trigger']
        
        if 'colors' in args:
            self.colors = args['colors']
        else:
            self.colors = [[255, 0, 0]]

        if 'brightness' in args:
            self.brightness = args['brightness']
        else:
            self.brightness = 255
        
        if 'on_delay' in args:
            self.on_delay = args['on_delay']
        else:
            self.on_delay = 0.25

        if 'transition' in args:
            self.transition = args['transition']
        else:
            self.transition = 1.0
        
        if 'off_delay' in args:
            self.off_delay = self.transition + args['off_delay']
        else:
            self.off_delay = 1.25
        
        if 'blink' in args:
            self.blink = args['blink']
        else:
            self.blink = False


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
            if self.blink:
                self.turn_off(light)

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
        if 'color_temp' in attributes:
            saved_attributes['color_temp'] = attributes['color_temp']
        if 'rgb_color' in attributes:
            saved_attributes['rgb_color'] = attributes['rgb_color']
        elif 'hs_color' in attributes:
            saved_attributes['hs_color'] = attributes['hs_color']
        elif 'xy_color' in attributes:
            saved_attributes['xy_color'] = attributes['xy_color']

        saved_state['attributes'] = saved_attributes
        self.recorded_state[entity] = saved_state

        self.log(f'Saved {entity} with state: {saved_state}')

    def restore_state(self, entity):
        if entity not in self.recorded_state:
            self.log(f'No saved state for {entity}')
            return False

        saved = self.recorded_state[entity]

        self.turn_on(entity)

        status = self.call_service('homeassistant/turn_on',
                                   entity_id=entity, 
                                   **saved['attributes']
                                  )

        if saved['state'] == 'off':
            time.sleep(self.setting_delay)
            self.turn_off(entity)

        self.log(f'Restored {entity} with state {saved}')

