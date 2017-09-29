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
                    try:
                        unit_measur = attr['attributes']['unit_of_measurement']
                        sensor_name = attr['attributes']['friendly_name']
                        sensor_state = attr['state']
                        return unit_measur, sensor_name, sensor_state
                    except BaseException:
                        unit_measur = 'null'
                        sensor_name = attr['attributes']['friendly_name']
                        sensor_state = attr['state']
                        return unit_measur, sensor_name, sensor_state

        return None

    def execute_service(self, domain, service, data):
        if self.ssl:
            post("%s/api/services/%s/%s" % (self.url, domain, service),
                 headers=self.headers, data=json.dumps(data), verify=True)
        else:
            post("%s/api/services/%s/%s" % (self.url, domain, service),
                 headers=self.headers, data=json.dumps(data))

# TODO - Localization

class HomeAssistantSkill2(MycroftSkill):

    def __init__(self):
        super(HomeAssistantSkill2, self).__init__(name="HomeAssistantSkill2")
        self.ha = HomeAssistantClient(self.config.get('host'),
            self.config.get('password'), ssl=self.config.get('ssl', False))

    def initialize(self):
        intent = IntentBuilder("LightingIntent").require("VolumeUpKeyword").build()
        self.register_intent(intent, self.handle_volume_intent)

    def handle_volume_intent(self, message):
        self.speak('volume tunred up')
        self.ha.execute_service("homeassistant", "turn_on", "scene.volume_up")

    def stop(self):
        pass


def create_skill():
    return HomeAssistantSkill2()
