from datetime import timedelta
import requests
import json
from collections import defaultdict
import logging
import string

from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.const import (
    CONF_NAME,
    STATE_UNKNOWN,
    CONF_CURRENCY,
    CONF_RESOURCES,
)

_LOGGER = logging.getLogger(__name__)

ICON = "mdi:cash-multiple"

SCAN_INTERVAL = timedelta(seconds=30)

ATTRIBUTION = "Data provided by cryptonator api"

DEFAULT_COMPARE = "eur-doge"

CONF_COMPARE = "compare"

DOMAIN = "cryptostate"

CONF_ARG = "arg"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_RESOURCES, default=[]): vol.All(
        cv.ensure_list,
        [
            vol.Schema({
                vol.Required(CONF_COMPARE, default=DEFAULT_COMPARE): cv.string,
                vol.Optional(CONF_ARG, default=DOMAIN): cv.string,
            })
        ],
    )
})

url = "https://api.cryptonator.com/api/ticker/{0}"

def getData(compare):
    """Get The request from the api"""

    parsedUrl = url.format(compare)
    #The headers are used to simulate a human request
    req = requests.get(parsedUrl, headers={"User-Agent": "Mozilla/5.0 (Platform; Security; OS-or-CPU; Localization; rv:1.4) Gecko/20030624 Netscape/7.1 (ax)"}) 

    jsone = req.json()
    resp = json.dumps(jsone)
    respParsed = json.loads(resp)

    return respParsed["ticker"]["price"]

#    if (respParsed["success"] == True):
#        return respParsed["ticker"]["price"]
#    else:
#        _LOGGER.warn("Request unsuccessful")
#        _LOGGER.error(respParsed["error"])

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Setup the currency sensor"""

    entities = []

    for resource in config[CONF_RESOURCES]:
        compare_ = resource[CONF_COMPARE]
        name = resource[CONF_ARG]
        
        entities.append(CurrencySensor(hass, name, compare_))

    add_entities(entities, True)

class CurrencySensor(SensorEntity):
    
    def __init__(self, hass, name, compare):
        """Inizialize sensor"""
        self._state = STATE_UNKNOWN
        self._name = name
        self._hass = hass
        self._compare = compare

    @property
    def name(self):
        """Return the name sensor"""
        return self._name or DOMAIN

    @property
    def icon(self):
        """Return the default icon"""
        return ICON

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._compare

    @property
    def state(self):
        """Return the state of the sensor"""
        return self._state

    @property
    def device_state_attributes(self):
        return ATTRIBUTION

    def update(self):
        """Get the latest update fron the api"""

        self._state = getData(self._compare)
