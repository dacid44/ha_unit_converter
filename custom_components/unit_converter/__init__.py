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
from homeassistant.helpers import intent

from .const import DATA_COMPONENT, DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=30)
CONVERT_UNITS_SERVICE_NAME: Final = "convert_units"
CONVERT_UNITS_SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required("input"): str,
        vol.Required("target"): str,
    }
)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Unit Converter component."""
    hass.services.async_register(
        DOMAIN,
        CONVERT_UNITS_SERVICE_NAME,
        convert_units_service,
        schema=CONVERT_UNITS_SERVICE_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )
    intent.async_register(hass, ConvertUnitsIntent())
    return True


@callback
def convert_units_service(call: ServiceCall) -> ServiceResponse:
    """Convert the input value to the target unit."""
    input = call.data["input"]
    target = call.data["target"]
    return {"result": convert_units(input, target)}


class ConvertUnitsIntent(intent.IntentHandler):
    """Handle ConvertUnits intents."""

    intent_type = "ConvertUnits"
    description = "Convert measurements to a different unit"
    slot_schema = {
        vol.Required("input"): intent.non_empty_string,
        vol.Required("target"): intent.non_empty_string,
    }

    async def async_handle(self, intent_obj: intent.Intent) -> intent.IntentResponse:
        """Handle the intent."""
        slots = self.async_validate_slots(intent_obj.slots)

        input = slots["input"]
        target = slots["target"]

        response = intent_obj.create_response()
        response.response_type = intent.IntentResponseType.QUERY_ANSWER
        response.async_set_speech(convert_units(input, target))

        return response


def convert_units(input: str, target: str) -> str:
    return f"converting {input} to {target}"
