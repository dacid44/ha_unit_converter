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

from pint import UnitRegistry, UndefinedUnitError

from .const import DOMAIN
from .convert import convert_units, how_many, ConvertException

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=30)
CONVERT_UNITS_SERVICE_NAME: Final = "convert_units"
CONVERT_UNITS_SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required("input"): str,
        vol.Required("target"): str,
    }
)

ureg = UnitRegistry()


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
    intent.async_register(hass, HowManyUnits())
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

        input = slots["input"]["value"]
        target = slots["target"]["value"]

        try:
            result = convert_units(input, target)
        except ConvertException as e:
            response = intent_obj.create_response()
            response.response_type = intent.IntentResponseType.ERROR
            response.async_set_error(intent.IntentResponseErrorCode.FAILED_TO_HANDLE)
            response.async_set_speech(str(e))
            return response

        response = intent_obj.create_response()
        response.response_type = intent.IntentResponseType.QUERY_ANSWER
        response.async_set_speech(result)
        return response


class HowManyUnits(intent.IntentHandler):
    """Handle HowManyUnits intents."""

    intent_type = "HowManyUnits"
    description = "Calculate how many of one unit are in another unit"
    slot_schema = {
        vol.Required("smaller"): intent.non_empty_string,
        vol.Required("larger"): intent.non_empty_string,
    }

    async def async_handle(self, intent_obj: intent.Intent) -> intent.IntentResponse:
        """Handle the intent."""
        slots = self.async_validate_slots(intent_obj.slots)

        smaller = slots["smaller"]["value"]
        larger = slots["larger"]["value"]

        try:
            result = how_many(smaller, larger)
        except ConvertException as e:
            response = intent_obj.create_response()
            response.response_type = intent.IntentResponseType.ERROR
            response.async_set_error(intent.IntentResponseErrorCode.FAILED_TO_HANDLE)
            response.async_set_speech(str(e))
            return response

        response = intent_obj.create_response()
        response.response_type = intent.IntentResponseType.QUERY_ANSWER
        response.async_set_speech(result)
        return response
