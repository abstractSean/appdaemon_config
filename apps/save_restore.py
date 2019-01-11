import time

class SaveRestore:
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

