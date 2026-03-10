from datetime import timedelta
import logging
from typing import Final

import voluptuous as vol

from homeassistant import core
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_component import EntityComponent

from .const import DATA_COMPONENT, DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=30)
SERVICE_CONVERT: Final = "convert"


async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """Set up the Unit Converter component."""
    # @TODO: Add setup code.

    component = hass.data[DATA_COMPONENT] = EntityComponent[UnitConverterEntity](
        _LOGGER, DOMAIN, hass, SCAN_INTERVAL
    )
    # component.async_register_entity_service(
    #     SERVICE_CONVERT,
    #     {vol.Required("input"): str, vol.Required("target"): str},
    # )
    await component.async_setup(config)
    return True


class UnitConverterEntity(Entity):
    _attr_has_entity_name = True

    def __init__(self):
        pass

    def convert(self, **kwargs):
        pass
