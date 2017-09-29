from os.path import dirname, join

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

from os.path import dirname, join
from requests import get, post
from fuzzywuzzy import fuzz
import json

__author__ = ''
LOGGER = getLogger(__name__)


class HomeAssistantClient(object):
    def __init__(self, host, password, port=8123, ssl=False):
        self.ssl = ssl
        if self.ssl:
            self.url = "https://%s:%d" % (host, port)
        else:
            self.url = "http://%s:%d" % (host, port)
        self.headers = {
            'x-ha-access': password,
            'Content-Type': 'application/json'
        }

    def find_entity(self, entity, types):
        if self.ssl:
            req = get("%s/api/states" % self.url, headers=self.headers, verify=False)
        else:
            req = get("%s/api/states" % self.url, headers=self.headers)

        if req.status_code == 200:
            best_score = 0
            best_entity = None
            for state in req.json():
                try:
                    if state['entity_id'].split(".")[0] in types:
                        LOGGER.debug("Entity Data: %s" % state)
                        score = fuzz.ratio(entity, state['attributes']['friendly_name'].lower())
                        if score > best_score:
                            best_score = score
                            best_entity = { "id": state['entity_id'],
                                            "dev_name": state['attributes']['friendly_name'],
                                            "state": state['state'] }
                except KeyError:
                    pass
            return best_entity

        return None

    def execute_service(self, domain, service, data):
        if self.ssl:
            post("%s/api/services/%s/%s" % (self.url, domain, service), headers=self.headers, data=json.dumps(data), verify=False)
        else:
            post("%s/api/services/%s/%s" % (self.url, domain, service), headers=self.headers, data=json.dumps(data))

# TODO - Localization
class HomeAssistantSkill2(MycroftSkill):

    def __init__(self):
        super(HomeAssistantSkill, self).__init__(name="HomeAssistantSkill2")
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