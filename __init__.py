from os.path import dirname, join

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

from os.path import dirname, join
from requests import get, post
from fuzzywuzzy import fuzz
import json

__author__ = 'robconnolly, btotharye'
LOGGER = getLogger(__name__)

class HomeAssistantClient(object):
    def __init__(self, host, password, portnum, ssl=False):
        self.ssl = ssl
        if self.ssl:
            portnum
            self.url = "https://%s:%d" % (host, portnum)
        else:
            self.url = "http://%s:%d" % (host, portnum)
        self.headers = {
            'x-ha-access': password,
            'Content-Type': 'application/json'
        }

    def find_entity(self, entity, types):
        if self.ssl:
            req = get("%s/api/states" %
                      self.url, headers=self.headers, verify=True)
        else:
            req = get("%s/api/states" % self.url, headers=self.headers)

        if req.status_code == 200:
            best_score = 0
            best_entity = None
            for state in req.json():
                try:
                    if state['entity_id'].split(".")[0] in types:
                        LOGGER.debug("Entity Data: %s" % state)
                        score = fuzz.ratio(
                            entity,
                            state['attributes']['friendly_name'].lower())
                        if score > best_score:
                            best_score = score
                            best_entity = {
                                "id": state['entity_id'],
                                "dev_name": state['attributes']
                                ['friendly_name'],
                                "state": state['state']}
                except KeyError:
                    pass
            return best_entity
    #
    # checking the entity attributes to be used in the response dialog.
    #

    def find_entity_attr(self, entity):
        if self.ssl:
            req = get("%s/api/states" %
                      self.url, headers=self.headers, verify=True)
        else:
            req = get("%s/api/states" % self.url, headers=self.headers)

        if req.status_code == 200:
            for attr in req.json():
                if attr['entity_id'] == entity:
                    entity_attrs = attr['attributes']
                    if attr['entity_id'].startswith('light.'):
                        unit_measur = entity_attrs['brightness']
                        sensor_name = entity_attrs['friendly_name']
                        sensor_state = attr['state']
                        return unit_measur, sensor_name, sensor_state
                    else:
                        try:
                            unit_measur = entity_attrs['unit_of_measurement']
                            sensor_name = entity_attrs['friendly_name']
                            sensor_state = attr['state']
                            return unit_measur, sensor_name, sensor_state
                        except BaseException:
                            unit_measur = 'null'
                            sensor_name = entity_attrs['friendly_name']
                            sensor_state = attr['state']
                            return unit_measur, sensor_name, sensor_state
        return None

    def execute_service(self, domain, service, data):
        if self.ssl:
            post("%s/api/services/%s/%s" % (self.url, domain, service),
                 headers=self.headers, data=json.dumps(data),
                 verify=self.verify)
        else:
            post("%s/api/services/%s/%s" % (self.url, domain, service),
                 headers=self.headers, data=json.dumps(data))

# TODO - Localization

class HomeAssistantSkill2(MycroftSkill):

    def __init__(self):
        super(HomeAssistantSkill2, self).__init__(name="HomeAssistantSkill2")
        self.ha = HomeAssistantClient(self.config.get('host'),
            self.config.get('password'), self.config.get('portnum') ,ssl=self.config.get('ssl', False))

    def initialize(self):
        movietime_intent = IntentBuilder("MovieTimeIntent").require("MovieTimeKeyword").build()
        self.register_intent(movietime_intent, self.handle_movietime_intent)

        bedtime_intent = IntentBuilder("BedTimeIntent").require("BedTimeKeyword").build()
        self.register_intent(bedtime_intent, self.handle_bedtime_intent)

	todo_list_intent = IntentBuilder("TodoListIntent").require("TodoListKeyword").build()
        self.register_intent(todo_list_intent, self.handle_todo_list_intent)
		
	movie_list_intent = IntentBuilder("MovieListIntent").require("MovieListKeyword").build()
        self.register_intent(movie_list_intent, self.handle_movie_list_intent)

	## add to home assistant

	stop_spotify_intent = IntentBuilder("StopSpotifyIntent").require("StopSpotifyKeyword").build()
        self.register_intent(stop_spotify_intent, self.handle_stop_spotify_intent)
		
	next_song_intent = IntentBuilder("NextSongIntent").require("NextSongKeyword").build()
        self.register_intent(next_song_intent, self.handle_next_song_intent)
		
	volume_high_intent = IntentBuilder("VolumeHighIntent").require("VolumeHighKeyword").build()
        self.register_intent(volume_high_intent, self.handle_volume_high_intent)

	volume_mid_intent = IntentBuilder("VolumeMidIntent").require("VolumeMidKeyword").build()
        self.register_intent(volume_mid_intent, self.handle_volume_mid_intent)

	volume_low_intent = IntentBuilder("VolumeLowIntent").require("VolumeLowKeyword").build()
        self.register_intent(volume_low_intent, self.handle_volume_low_intent)

	going_out_intent = IntentBuilder("GoingOutIntent").require("GoingOutKeyword").build()
        self.register_intent(going_out_intent, self.handle_going_out_intent)
		
    def handle_movietime_intent(self, message):
	entity = 'movie_time'
	LOGGER.debug("Entity: %s" % entity)
	ha_entity = self.ha.find_entity(entity, ['scene'])
	ha_data = {'entity_id': ha_entity['id']}        
	self.speak('enjoy the show')
	self.ha.execute_service("homeassistant", "turn_on", ha_data)

    def handle_bedtime_intent(self, message):
        entity = 'bed_time'
        LOGGER.debug("Entity: %s" % entity)
        ha_entity = self.ha.find_entity(entity, ['scene'])
        ha_data = {'entity_id': ha_entity['id']}
        self.speak('have a good sleep')
        self.ha.execute_service("homeassistant", "turn_on", ha_data)
		
    def handle_todo_list_intent(self, message):
        entity = 'to_do_list'
        LOGGER.debug("Entity: %s" % entity)
        ha_entity = self.ha.find_entity(entity, ['scene'])
	self.speak('have a good sleep')
        ha_data = {'entity_id': ha_entity['id']}
        self.ha.execute_service("homeassistant", "turn_on", ha_data)

    def handle_movie_list_intent(self, message):
        entity = 'movie_watch_script'
        LOGGER.debug("Entity: %s" % entity)
        ha_entity = self.ha.find_entity(entity, ['scene'])
        ha_data = {'entity_id': ha_entity['id']}
        self.ha.execute_service("homeassistant", "turn_on", ha_data)

	### add to home assistant 
    def handle_stop_spotify_intent(self, message):
        entity = 'stop_spotify'
        LOGGER.debug("Entity: %s" % entity)
        ha_entity = self.ha.find_entity(entity, ['scene'])
        ha_data = {'entity_id': ha_entity['id']}
        self.ha.execute_service("homeassistant", "turn_on", ha_data)

    def handle_next_song_intent(self, message):
        entity = 'next_song'
        LOGGER.debug("Entity: %s" % entity)
        ha_entity = self.ha.find_entity(entity, ['scene'])
        ha_data = {'entity_id': ha_entity['id']}
        self.ha.execute_service("homeassistant", "turn_on", ha_data)

    def handle_volume_high_intent(self, message):
        entity = 'volume_high'
        LOGGER.debug("Entity: %s" % entity)
        ha_entity = self.ha.find_entity(entity, ['scene'])
        ha_data = {'entity_id': ha_entity['id']}
        self.ha.execute_service("homeassistant", "turn_on", ha_data)

    def handle_volume_mid_intent(self, message):
        entity = 'volume_medium'
        LOGGER.debug("Entity: %s" % entity)
        ha_entity = self.ha.find_entity(entity, ['scene'])
        ha_data = {'entity_id': ha_entity['id']}
        self.ha.execute_service("homeassistant", "turn_on", ha_data)

    def handle_volume_low_intent(self, message):
        entity = 'volume_low'
        LOGGER.debug("Entity: %s" % entity)
        ha_entity = self.ha.find_entity(entity, ['scene'])
        ha_data = {'entity_id': ha_entity['id']}
        self.ha.execute_service("homeassistant", "turn_on", ha_data)

    def handle_going_out_intent(self, message):
        entity = 'going_out'
        LOGGER.debug("Entity: %s" % entity)
        ha_entity = self.ha.find_entity(entity, ['scene'])
        ha_data = {'entity_id': ha_entity['id']}
        self.ha.execute_service("homeassistant", "turn_on", ha_data)
	self.speak('see you when you get back')
		
    def stop(self):
        pass


def create_skill():
    return HomeAssistantSkill2()
