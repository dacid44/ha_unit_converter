from homeassistant.util.hass_dict import HassKey
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.helpers.entity_component import EntityComponent

    from . import UnitConverterEntity

DOMAIN = "unit_converter"
DATA_COMPONENT: HassKey[EntityComponent[UnitConverterEntity]] = HassKey(DOMAIN)
