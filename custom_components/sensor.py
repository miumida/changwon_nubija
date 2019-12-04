import logging
import requests
import voluptuous as vol
import re

from bs4 import BeautifulSoup

import homeassistant.helpers.config_validation as cv

from datetime import timedelta
from datetime import datetime
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (CONF_NAME, CONF_API_KEY, CONF_ICON)
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

REQUIREMENTS = ['beautifulsoup4==4.6.0']

_LOGGER = logging.getLogger(__name__)

CONF_NAME  = 'name'
CONF_TERMINAL_INDEX = 'terminal_index'
CONF_INDEX = 'index'

BSE_URL = 'https://www.nubija.com/terminal/terminalState.do'

DEFAULT_NAME = ''
DEFAULT_ICON = 'mdi:bike'

MIN_TIME_BETWEEN_API_UPDATES    = timedelta(seconds=3600) #
MIN_TIME_BETWEEN_SENSOR_UPDATES = timedelta(seconds=3600) #

ATTR_NAME = 'name'
ATTR_SYNC_DATE = 'sync_date'

TMN_NAME_FORMAT = '{}'
TMN_VAL_FORMAT = 'K({}) / B({})'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_TERMINAL_INDEX, default=[]): vol.All(cv.ensure_list),
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    name  = config.get(CONF_NAME)
    terminal_index_list = config.get(CONF_TERMINAL_INDEX)

    sensors = []

    nubija = nubijaAPI(name, terminal_index_list)

    nubijaSensor = terminalSensor(name, nubija)
    nubijaSensor.update()
    sensors += [nubijaSensor]

    add_entities(sensors, True)

class nubijaAPI:

    def __init__(self, name, index_list):
        """Initialize the nubija API."""
        self._name       = name
        self._index_list = index_list
        self.result      = {}

    @Throttle(MIN_TIME_BETWEEN_API_UPDATES)
    def update(self):
        """Update function for updating api information."""
        try:
            dt = datetime.now()
            syncDate = dt.strftime("%Y-%m-%d %H:%M:%S")

            url = BSE_URL

            response = requests.get(url, timeout=30)
            response.raise_for_status()

            page = response.content

            soup = BeautifulSoup(page, 'html.parser')

            realtime = soup.find(id="realtime_area")
            terminals = realtime.find_all("a")

            terminal_dict = {}

            for tmn in terminals:
              if 'href' in tmn.attrs:
                nubijaTmp = tmn.attrs['href'].replace('javascript:showMapInfoWindow(', '').replace(');','').replace('  ', ' ')
                rslt = re.split(', ', nubijaTmp)

                for att in rslt:
                   att = att[1:-1]

                if self._index_list is not None:
                  if rslt[3][1:-1] not in self._index_list:
                    continue

                terminal_dict[rslt[3][1:-1]] = {
                  'name': rslt[0][1:-1],
                  'kios': rslt[1][1:-1],
                  'bycle':rslt[2][1:-1],
                  'index':rslt[3][1:-1],
                  'sync_date':syncDate }

            self.result = terminal_dict
            #_LOGGER.debug('nubija API Request Result: %s', self.result)
        except Exception as ex:
            _LOGGER.error('Failed to update nubija API status Error: %s', ex)
            raise

class terminalSensor(Entity):
    def __init__(self, name, api):
        self._name      = name
        self._api       = api
        self._icon      = DEFAULT_ICON
        self._state     = None
        self.terminals    = {}

    @property
    def entity_id(self):
        """Return the entity ID."""
        return 'sensor.changwon_nubija'

    @property
    def name(self):
        """Return the name of the sensor, if any."""
        return self._name

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def state(self):
        """Return the state of the sensor."""
        return '-'

    @property
    def attribution(self):
        """Return the attribution."""
        return 'Powered by miumida'

    @Throttle(MIN_TIME_BETWEEN_SENSOR_UPDATES)
    def update(self):
        """Get the latest state of the sensor."""
        if self._api is None:
            return

        self._api.update()
        nubija_dict = self._api.result

        self.terminals = nubija_dict

    @property
    def device_state_attributes(self):
        """Attributes."""
        return { TMN_NAME_FORMAT.format(self.terminals[key].get("name")): TMN_VAL_FORMAT.format(self.terminals[key].get('kios','-'), self.terminals[key].get('bycle','-')) for key in sorted(self.terminals.keys()) }
