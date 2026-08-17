"""Sensor platform for Guangzhou Gas."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import DOMAIN
from .coordinator import GuangzhouGasDataUpdateCoordinator
from .data import clean_value, date_value, datetime_value, decimal_value, first_value
from .entity import GuangzhouGasEntity

ValueConverter = Callable[[Any], StateType]


@dataclass(frozen=True, kw_only=True)
class GuangzhouGasSensorEntityDescription(SensorEntityDescription):
    """Describe a Guangzhou Gas sensor."""

    value_keys: tuple[str, ...]
    value_converter: ValueConverter = clean_value
    attribute_keys: Mapping[str, tuple[str, ...]] | None = None


def _diagnostic(
    *,
    key: str,
    translation_key: str,
    value_keys: tuple[str, ...],
    icon: str,
    device_class: SensorDeviceClass | None = None,
    native_unit_of_measurement: str | None = None,
    value_converter: ValueConverter = clean_value,
    attribute_keys: Mapping[str, tuple[str, ...]] | None = None,
) -> GuangzhouGasSensorEntityDescription:
    """Create a disabled-by-default diagnostic sensor description."""
    return GuangzhouGasSensorEntityDescription(
        key=key,
        translation_key=translation_key,
        value_keys=value_keys,
        icon=icon,
        device_class=device_class,
        native_unit_of_measurement=native_unit_of_measurement,
        value_converter=value_converter,
        attribute_keys=attribute_keys,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    )


SENSORS: tuple[GuangzhouGasSensorEntityDescription, ...] = (
    # The device page deliberately keeps only information people act on.
    GuangzhouGasSensorEntityDescription(
        key="balance",
        translation_key="balance",
        value_keys=("money",),
        value_converter=decimal_value,
        icon="mdi:meter-gas",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement="元",
        attribute_keys={
            "账户余额": ("dqye",),
            "最近充值金额": ("zhczje",),
            "最近充值时间": ("zhczsj",),
        },
    ),
    GuangzhouGasSensorEntityDescription(
        key="gas_usage",
        translation_key="gas_usage",
        value_keys=("jieti_amount_benci", "bzqyyql"),
        value_converter=decimal_value,
        icon="mdi:fire",
        device_class=SensorDeviceClass.GAS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement="m³",
        attribute_keys={
            "阶梯周期": ("jieti_interval",),
            "周期开始": ("jietiTimeBenci",),
        },
    ),
    GuangzhouGasSensorEntityDescription(
        key="meter_status",
        translation_key="meter_status",
        value_keys=("rqbztdes",),
        icon="mdi:meter-gas-outline",
        attribute_keys={"表类型": ("blx",), "安装位置": ("rqbAzwz",)},
    ),
    GuangzhouGasSensorEntityDescription(
        key="last_reading",
        translation_key="last_reading",
        value_keys=("lastRecordWatchNum",),
        value_converter=decimal_value,
        icon="mdi:counter",
        device_class=SensorDeviceClass.GAS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement="m³",
        attribute_keys={"抄表日期": ("lastRecordWatchDate",)},
    ),
    GuangzhouGasSensorEntityDescription(
        key="last_charge",
        translation_key="last_recharge",
        value_keys=("zhczje",),
        value_converter=decimal_value,
        icon="mdi:cash-plus",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement="元",
        attribute_keys={
            "充值时间": ("zhczsj",),
            "累计充值": ("ljczye", "lijczye"),
        },
    ),
    GuangzhouGasSensorEntityDescription(
        key="billing_cycle",
        translation_key="billing_cycle",
        value_keys=("jieti_interval",),
        icon="mdi:calendar-range",
    ),
    GuangzhouGasSensorEntityDescription(
        key="safety_inspection",
        translation_key="safety_inspection",
        value_keys=("safeInspectHas",),
        icon="mdi:shield-check",
        attribute_keys={"安检日期": ("safeInspectDate",)},
    ),
    GuangzhouGasSensorEntityDescription(
        key="fee_money",
        translation_key="fee_money",
        value_keys=("feeMoney",),
        value_converter=decimal_value,
        icon="mdi:cash-alert",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement="元",
        attribute_keys={"欠费状态": ("feeFlag",)},
    ),
    _diagnostic(
        key="total_charge",
        translation_key="total_recharge",
        value_keys=("ljczye", "lijczye"),
        value_converter=decimal_value,
        icon="mdi:cash-multiple",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement="元",
    ),
    _diagnostic(
        key="auto_payment",
        translation_key="auto_payment",
        value_keys=("feeWay",),
        icon="mdi:credit-card-check",
        attribute_keys={"扣费账号": ("backAccount",)},
    ),
    _diagnostic(
        key="last_charge_time",
        translation_key="last_recharge_time",
        value_keys=("zhczsj",),
        value_converter=datetime_value,
        icon="mdi:clock-outline",
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
    _diagnostic(
        key="user_name",
        translation_key="user_name",
        value_keys=("userName",),
        icon="mdi:account",
    ),
    _diagnostic(
        key="user_no",
        translation_key="user_no",
        value_keys=("userNo",),
        icon="mdi:identifier",
    ),
    _diagnostic(
        key="address",
        translation_key="address",
        value_keys=("userAddress", "address"),
        icon="mdi:map-marker",
    ),
    _diagnostic(
        key="meter_no",
        translation_key="meter_no",
        value_keys=("bm", "rqbbgh"),
        icon="mdi:barcode",
    ),
    _diagnostic(
        key="meter_type",
        translation_key="meter_type",
        value_keys=("blx",),
        icon="mdi:meter-gas",
    ),
    _diagnostic(
        key="last_watch_date",
        translation_key="last_watch_date",
        value_keys=("lastRecordWatchDate",),
        value_converter=date_value,
        icon="mdi:calendar-check",
        device_class=SensorDeviceClass.DATE,
    ),
    _diagnostic(
        key="current_balance",
        translation_key="current_balance",
        value_keys=("dqye",),
        value_converter=decimal_value,
        icon="mdi:wallet",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement="元",
    ),
    _diagnostic(
        key="fee_flag",
        translation_key="fee_flag",
        value_keys=("feeFlag",),
        icon="mdi:alert-circle-outline",
    ),
    _diagnostic(
        key="safety_inspection_date",
        translation_key="safety_inspection_date",
        value_keys=("safeInspectDate",),
        value_converter=date_value,
        icon="mdi:calendar-shield",
        device_class=SensorDeviceClass.DATE,
    ),
    _diagnostic(
        key="start_fire_date",
        translation_key="start_fire_date",
        value_keys=("startFireDate",),
        value_converter=datetime_value,
        icon="mdi:fire-circle",
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
    _diagnostic(
        key="company_name",
        translation_key="company_name",
        value_keys=("bmmc",),
        icon="mdi:office-building",
    ),
    _diagnostic(
        key="payment_account",
        translation_key="payment_account",
        value_keys=("backAccount",),
        icon="mdi:bank",
    ),
    _diagnostic(
        key="insurance_fee",
        translation_key="insurance_fee",
        value_keys=("bxje",),
        value_converter=decimal_value,
        icon="mdi:shield-plus",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement="元",
    ),
    _diagnostic(
        key="insurance_expire",
        translation_key="insurance_expire",
        value_keys=("bxjzrq",),
        value_converter=date_value,
        icon="mdi:calendar-clock",
        device_class=SensorDeviceClass.DATE,
    ),
    _diagnostic(
        key="billing_cycle_start",
        translation_key="billing_cycle_start",
        value_keys=("jietiTimeBenci",),
        value_converter=date_value,
        icon="mdi:calendar-start",
        device_class=SensorDeviceClass.DATE,
    ),
    _diagnostic(
        key="user_type",
        translation_key="user_type",
        value_keys=("userType",),
        icon="mdi:account-group",
    ),
    _diagnostic(
        key="insurance_type",
        translation_key="insurance_type",
        value_keys=("bxjglx",),
        icon="mdi:shield-sync",
    ),
    _diagnostic(
        key="insurance_invalid",
        translation_key="insurance_invalid",
        value_keys=("bxsxrq",),
        value_converter=date_value,
        icon="mdi:calendar-remove",
        device_class=SensorDeviceClass.DATE,
    ),
    _diagnostic(
        key="gas_address_status",
        translation_key="gas_address_status",
        value_keys=("yqdzztdes", "yqdzztDes"),
        icon="mdi:home-check-outline",
    ),
    _diagnostic(
        key="customer_id",
        translation_key="customer_id",
        value_keys=("khId",),
        icon="mdi:identifier",
    ),
    _diagnostic(
        key="current_usage_detail",
        translation_key="current_usage_detail",
        value_keys=("bzqyyql",),
        value_converter=decimal_value,
        icon="mdi:fire-circle",
        device_class=SensorDeviceClass.GAS,
        native_unit_of_measurement="m³",
    ),
    _diagnostic(
        key="meter_location",
        translation_key="meter_location",
        value_keys=("rqbAzwz",),
        icon="mdi:map-marker-question",
    ),
    _diagnostic(
        key="meter_location_id",
        translation_key="meter_location_id",
        value_keys=("rqbWzId",),
        icon="mdi:map-marker-outline",
    ),
    _diagnostic(
        key="meter_id_detail",
        translation_key="meter_id_detail",
        value_keys=("rqbId",),
        icon="mdi:numeric-1-circle",
    ),
    _diagnostic(
        key="meter_serial",
        translation_key="meter_serial",
        value_keys=("rqbbgh",),
        icon="mdi:barcode-scan",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Guangzhou Gas sensors from a config entry."""
    coordinator: GuangzhouGasDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        GuangzhouGasSensor(coordinator, entry, description) for description in SENSORS
    )


class GuangzhouGasSensor(GuangzhouGasEntity, SensorEntity):
    """A sensor backed by the Guangzhou Gas update coordinator."""

    entity_description: GuangzhouGasSensorEntityDescription

    def __init__(
        self,
        coordinator: GuangzhouGasDataUpdateCoordinator,
        entry: ConfigEntry,
        description: GuangzhouGasSensorEntityDescription,
    ) -> None:
        """Initialize a described sensor while preserving legacy unique IDs."""
        super().__init__(coordinator, entry)
        self.entity_description = description
        user_no = coordinator.data.get("userNo", "unknown")
        self._attr_unique_id = f"{DOMAIN}_{user_no}_{description.key}"

    @property
    def native_value(self) -> StateType:
        """Return the normalized sensor state."""
        value = first_value(self.coordinator.data, self.entity_description.value_keys)
        return self.entity_description.value_converter(value)

    @property
    def extra_state_attributes(self) -> Mapping[str, StateType] | None:
        """Expose only attributes that add context to the primary value."""
        if not self.entity_description.attribute_keys:
            return None
        attributes = {
            name: first_value(self.coordinator.data, keys)
            for name, keys in self.entity_description.attribute_keys.items()
        }
        return {name: value for name, value in attributes.items() if value is not None}
