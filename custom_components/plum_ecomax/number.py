"""Platform for number integration."""

from __future__ import annotations

from collections.abc import Generator, Iterable
from dataclasses import dataclass
import logging
from typing import cast

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from pyplumio.const import ProductType
from pyplumio.helpers.parameter import Parameter
from pyplumio.structures.modules import ConnectedModules

from . import PlumEcomaxConfigEntry
from .connection import EcomaxConnection
from .const import ALL, CALORIFIC_KWH_KG
from .entity import (
    DescriptorT,
    EcomaxEntity,
    EcomaxEntityDescription,
    MixerEntity,
    SubDescriptorT,
    SubdeviceEntityDescription,
)

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class EcomaxNumberEntityDescription(EcomaxEntityDescription, NumberEntityDescription):
    """Describes an ecoMAX number."""


NUMBER_TYPES: tuple[EcomaxNumberEntityDescription, ...] = (
    EcomaxNumberEntityDescription(
        key="heating_target_temp",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_step=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        product_types={ProductType.ECOMAX_P},
        translation_key="target_heating_temp",
    ),
    EcomaxNumberEntityDescription(
        key="min_heating_target_temp",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_step=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        product_types={ProductType.ECOMAX_P},
        translation_key="min_heating_temp",
    ),
    EcomaxNumberEntityDescription(
        key="max_heating_target_temp",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_step=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        product_types={ProductType.ECOMAX_P},
        translation_key="max_heating_temp",
    ),
    EcomaxNumberEntityDescription(
        key="grate_heating_temp",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_step=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        product_types={ProductType.ECOMAX_P},
        translation_key="grate_mode_temp",
    ),
    EcomaxNumberEntityDescription(
        key="min_fuzzy_logic_power",
        native_step=1,
        native_unit_of_measurement=PERCENTAGE,
        product_types={ProductType.ECOMAX_P},
        translation_key="fuzzy_logic_min_power",
    ),
    EcomaxNumberEntityDescription(
        key="max_fuzzy_logic_power",
        native_step=1,
        native_unit_of_measurement=PERCENTAGE,
        product_types={ProductType.ECOMAX_P},
        translation_key="fuzzy_logic_max_power",
    ),
    EcomaxNumberEntityDescription(
        key="fuel_calorific_value",
        mode=NumberMode.BOX,
        native_step=0.1,
        native_unit_of_measurement=CALORIFIC_KWH_KG,
        product_types={ProductType.ECOMAX_P},
        translation_key="fuel_calorific_value",
    ),
    EcomaxNumberEntityDescription(
        key="heating_hysteresis",
        translation_key="heating_hysteresis",
        native_step=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        product_types={ProductType.ECOMAX_P},
    ),
    EcomaxNumberEntityDescription(
        key="h1_hysteresis",
        translation_key="h1_hysteresis",
        native_step=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        product_types={ProductType.ECOMAX_P},
    ),
    EcomaxNumberEntityDescription(
        key="h2_hysteresis",
        translation_key="h2_hysteresis",
        native_step=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        product_types={ProductType.ECOMAX_P},
    ),
    EcomaxNumberEntityDescription(
        key="heating_pump_enable_temp",
        translation_key="heating_pump_enable_temp",
        native_step=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        product_types={ProductType.ECOMAX_P},
    ),
    EcomaxNumberEntityDescription(
        key="water_heater_hysteresis",
        translation_key="water_heater_hysteresis",
        native_step=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        product_types={ProductType.ECOMAX_P},
    ),
)


class EcomaxNumber(EcomaxEntity, NumberEntity):
    """Represents an ecoMAX number."""

    entity_description: EcomaxNumberEntityDescription

    async def async_set_native_value(self, value: float) -> None:
        """Update current value."""
        self.device.set_nowait(self.entity_description.key, value)
        self._attr_native_value = value
        self.async_write_ha_state()

    async def async_update(self, value: Parameter) -> None:
        """Update entity state."""
        self._attr_native_value = cast(float, value.value)
        self._attr_native_min_value = cast(float, value.min_value)
        self._attr_native_max_value = cast(float, value.max_value)
        self.async_write_ha_state()


@dataclass(frozen=True, kw_only=True)
class EcomaxMixerNumberEntityDescription(
    EcomaxNumberEntityDescription, SubdeviceEntityDescription
):
    """Describes a mixer number."""


MIXER_NUMBER_TYPES: tuple[EcomaxMixerNumberEntityDescription, ...] = (
    EcomaxMixerNumberEntityDescription(
        key="mixer_target_temp",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_step=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        product_types={ProductType.ECOMAX_P},
        translation_key="target_mixer_temp",
    ),
    EcomaxMixerNumberEntityDescription(
        key="min_target_temp",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_step=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        product_types={ProductType.ECOMAX_P},
        translation_key="min_mixer_temp",
    ),
    EcomaxMixerNumberEntityDescription(
        key="max_target_temp",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_step=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        product_types={ProductType.ECOMAX_P},
        translation_key="max_mixer_temp",
    ),
    EcomaxMixerNumberEntityDescription(
        key="circuit_target_temp",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_step=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        product_types={ProductType.ECOMAX_I},
        translation_key="target_circuit_temp",
    ),
    EcomaxMixerNumberEntityDescription(
        key="min_target_temp",
        device_class=NumberDeviceClass.TEMPERATURE,
        indexes={2, 3},
        native_step=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        product_types={ProductType.ECOMAX_I},
        translation_key="min_circuit_temp",
    ),
    EcomaxMixerNumberEntityDescription(
        key="max_target_temp",
        device_class=NumberDeviceClass.TEMPERATURE,
        indexes={2, 3},
        native_step=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        product_types={ProductType.ECOMAX_I},
        translation_key="max_circuit_temp",
    ),
    EcomaxMixerNumberEntityDescription(
        key="day_target_temp",
        device_class=NumberDeviceClass.TEMPERATURE,
        indexes={2, 3},
        native_step=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        product_types={ProductType.ECOMAX_I},
        translation_key="day_target_circuit_temp",
    ),
    EcomaxMixerNumberEntityDescription(
        key="night_target_temp",
        device_class=NumberDeviceClass.TEMPERATURE,
        indexes={2, 3},
        native_step=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        product_types={ProductType.ECOMAX_I},
        translation_key="night_target_circuit_temp",
    ),
)


class MixerNumber(MixerEntity, EcomaxNumber):
    """Represents a mixer number."""

    entity_description: EcomaxMixerNumberEntityDescription

    def __init__(
        self,
        connection: EcomaxConnection,
        description: EcomaxMixerNumberEntityDescription,
        index: int,
    ):
        """Initialize a new mixer number."""
        self.index = index
        super().__init__(connection, description)


def get_by_product_type(
    product_type: ProductType,
    descriptions: Iterable[DescriptorT],
) -> Generator[DescriptorT, None, None]:
    """Filter descriptions by the product type."""
    for description in descriptions:
        if (
            description.product_types == ALL
            or product_type in description.product_types
        ):
            yield description


def get_by_modules(
    connected_modules: ConnectedModules,
    descriptions: Iterable[DescriptorT],
) -> Generator[DescriptorT, None, None]:
    """Filter descriptions by connected modules."""
    for description in descriptions:
        if getattr(connected_modules, description.module, None) is not None:
            yield description


def get_by_index(
    index: int, descriptions: Iterable[SubDescriptorT]
) -> Generator[SubDescriptorT, None, None]:
    """Filter mixer/circuit descriptions by the index."""
    index += 1
    for description in descriptions:
        if description.indexes == ALL or index in description.indexes:
            yield description


def async_setup_ecomax_numbers(connection: EcomaxConnection) -> list[EcomaxNumber]:
    """Set up the ecoMAX numbers."""
    return [
        EcomaxNumber(connection, description)
        for description in get_by_modules(
            connection.device.modules,
            get_by_product_type(connection.product_type, NUMBER_TYPES),
        )
    ]


def async_setup_mixer_numbers(connection: EcomaxConnection) -> list[MixerNumber]:
    """Set up the mixer numbers."""
    return [
        MixerNumber(connection, description, index)
        for index in connection.device.mixers
        for description in get_by_index(
            index,
            get_by_modules(
                connection.device.modules,
                get_by_product_type(connection.product_type, MIXER_NUMBER_TYPES),
            ),
        )
    ]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PlumEcomaxConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> bool:
    """Set up the number platform."""
    _LOGGER.debug("Starting setup of number platform...")

    connection = entry.runtime_data.connection
    entities = async_setup_ecomax_numbers(connection)

    # Add mixer/circuit numbers.
    if connection.has_mixers and await connection.async_setup_mixers():
        entities += async_setup_mixer_numbers(connection)

    async_add_entities(entities)
    return True
