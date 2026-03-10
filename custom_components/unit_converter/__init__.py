from datetime import timedelta
import logging
from typing import Final

import voluptuous as vol

from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
    callback,
)
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_component import EntityComponent

from .const import DATA_COMPONENT, DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=30)
CONVERT_SERVICE_NAME: Final = "convert"
CONVERT_SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required("input"): str,
        vol.Required("target"): str,
    }
)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
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

    hass.services.async_register(
        DOMAIN,
        CONVERT_SERVICE_NAME,
        convert,
        schema=CONVERT_SERVICE_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )
    return True


@callback
def convert(call: ServiceCall) -> ServiceResponse:
    """Convert the input value to the target unit."""
    input = call.data["input"]
    target = call.data["target"]
    return {"result": f"converting {input} to {target}"}


class UnitConverterEntity(Entity):
    _attr_has_entity_name = True

    def __init__(self):
        pass

    def convert(self, **kwargs):
        pass
