"""Sensors for Guangzhou Gas."""
from __future__ import annotations

import logging
from typing import Any, Mapping, Optional

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.helpers.typing import StateType

from .const import (
    DOMAIN,
    SENSOR_TYPES,
    EXTRA_STATE_ATTRIBUTES,
)
from .entity import GuangzhouGasEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Guangzhou Gas sensors.
    
    Args:
        hass: Home Assistant instance.
        entry: Config entry.
        async_add_entities: Callback to add entities.
    """
    _LOGGER.info("Setting up Guangzhou Gas sensors")
    
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    # 创建 16 个传感器实体
    entities = [
        GuangzhouGasBalanceSensor(coordinator, entry),
        GuangzhouGasGasUsageSensor(coordinator, entry),
        GuangzhouGasMeterStatusSensor(coordinator, entry),
        GuangzhouGasLastReadingSensor(coordinator, entry),
        GuangzhouGasLastRechargeSensor(coordinator, entry),
        GuangzhouGasTotalRechargeSensor(coordinator, entry),
        GuangzhouGasBillingCycleSensor(coordinator, entry),
        GuangzhouGasAutoPaymentSensor(coordinator, entry),
        GuangzhouGasSafetyInspectionSensor(coordinator, entry),
        GuangzhouGasLastRechargeTimeSensor(coordinator, entry),
        # 新增 6 个传感器
        GuangzhouGasUserNameSensor(coordinator, entry),
        GuangzhouGasUserNoSensor(coordinator, entry),
        GuangzhouGasAddressSensor(coordinator, entry),
        GuangzhouGasMeterNoSensor(coordinator, entry),
        GuangzhouGasMeterTypeSensor(coordinator, entry),
        GuangzhouGasLastWatchDateSensor(coordinator, entry),
    ]
    
    async_add_entities(entities)
    _LOGGER.info("Added %d sensors", len(entities))


class GuangzhouGasBalanceSensor(GuangzhouGasEntity, SensorEntity):
    """Sensor for gas balance."""
    
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_icon = "mdi:cash"
    _attr_native_unit_of_measurement = "元"
    
    @property
    def name(self) -> str:
        """Return sensor name."""
        return "燃气余额"
        
    @property
    def unique_id(self) -> Optional[str]:
        """Return unique ID."""
        user_no = self.coordinator.data.get("userNo", "unknown")
        return f"{DOMAIN}_{user_no}_balance"
        
    @property
    def native_value(self) -> StateType:
        """Return sensor state."""
        value = self.coordinator.data.get("money")
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
            
    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        """Return extra state attributes."""
        return {
            "用户名": self.coordinator.data.get("userName"),
            "用户号": self.coordinator.data.get("userNo"),
            "地址": self.coordinator.data.get("userAddress"),
        }


class GuangzhouGasGasUsageSensor(GuangzhouGasEntity, SensorEntity):
    """Sensor for gas usage in billing cycle."""
    
    _attr_device_class = SensorDeviceClass.GAS
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_icon = "mdi:fire"
    _attr_native_unit_of_measurement = "m³"
    
    @property
    def name(self) -> str:
        """Return sensor name."""
        return "阶梯周期用气量"
        
    @property
    def unique_id(self) -> Optional[str]:
        """Return unique ID."""
        user_no = self.coordinator.data.get("userNo", "unknown")
        return f"{DOMAIN}_{user_no}_gas_usage"
        
    @property
    def native_value(self) -> StateType:
        """Return sensor state."""
        value = self.coordinator.data.get("jieti_amount_benci")
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
            
    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        """Return extra state attributes."""
        return {
            "阶梯周期": self.coordinator.data.get("jieti_interval"),
            "用户名": self.coordinator.data.get("userName"),
        }


class GuangzhouGasMeterStatusSensor(GuangzhouGasEntity, SensorEntity):
    """Sensor for gas meter status."""
    
    _attr_icon = "mdi:gas-cylinder"
    
    @property
    def name(self) -> str:
        """Return sensor name."""
        return "燃气表状态"
        
    @property
    def unique_id(self) -> Optional[str]:
        """Return unique ID."""
        user_no = self.coordinator.data.get("userNo", "unknown")
        return f"{DOMAIN}_{user_no}_meter_status"
        
    @property
    def native_value(self) -> StateType:
        """Return sensor state."""
        return self.coordinator.data.get("rqbztdes")
            
    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        """Return extra state attributes."""
        return {
            "表号": self.coordinator.data.get("bm"),
            "表类型": self.coordinator.data.get("blx"),
            "用户名": self.coordinator.data.get("userName"),
        }


class GuangzhouGasLastReadingSensor(GuangzhouGasEntity, SensorEntity):
    """Sensor for last meter reading."""
    
    _attr_icon = "mdi:counter"
    _attr_native_unit_of_measurement = "m³"
    
    @property
    def name(self) -> str:
        """Return sensor name."""
        return "上次抄表读数"
        
    @property
    def unique_id(self) -> Optional[str]:
        """Return unique ID."""
        user_no = self.coordinator.data.get("userNo", "unknown")
        return f"{DOMAIN}_{user_no}_last_reading"
        
    @property
    def state(self) -> StateType:
        """Return sensor state."""
        value = self.coordinator.data.get("lastRecordWatchNum")
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
            
    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        """Return extra state attributes."""
        return {
            "抄表日期": self.coordinator.data.get("lastRecordWatchDate"),
            "用户名": self.coordinator.data.get("userName"),
        }


class GuangzhouGasLastRechargeSensor(GuangzhouGasEntity, SensorEntity):
    """Sensor for last recharge amount."""
    
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_icon = "mdi:cash-plus"
    _attr_native_unit_of_measurement = "元"
    
    @property
    def name(self) -> str:
        """Return sensor name."""
        return "最近充值金额"
        
    @property
    def unique_id(self) -> Optional[str]:
        """Return unique ID."""
        user_no = self.coordinator.data.get("userNo", "unknown")
        return f"{DOMAIN}_{user_no}_last_recharge"
        
    @property
    def native_value(self) -> StateType:
        """Return sensor state."""
        value = self.coordinator.data.get("zhczje")
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
            
    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        """Return extra state attributes."""
        return {
            "充值时间": self.coordinator.data.get("zhczsj"),
            "累计充值": self.coordinator.data.get("ljczye"),
            "用户名": self.coordinator.data.get("userName"),
        }


class GuangzhouGasTotalRechargeSensor(GuangzhouGasEntity, SensorEntity):
    """Sensor for total recharge amount."""
    
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_icon = "mdi:cash"
    _attr_native_unit_of_measurement = "元"
    
    @property
    def name(self) -> str:
        """Return sensor name."""
        return "累计充值金额"
        
    @property
    def unique_id(self) -> Optional[str]:
        """Return unique ID."""
        user_no = self.coordinator.data.get("userNo", "unknown")
        return f"{DOMAIN}_{user_no}_total_recharge"
        
    @property
    def native_value(self) -> StateType:
        """Return sensor state."""
        value = self.coordinator.data.get("ljczye")
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
            
    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        """Return extra state attributes."""
        return {
            "最近充值": self.coordinator.data.get("zhczje"),
            "充值时间": self.coordinator.data.get("zhczsj"),
            "用户名": self.coordinator.data.get("userName"),
        }


class GuangzhouGasBillingCycleSensor(GuangzhouGasEntity, SensorEntity):
    """Sensor for billing cycle."""
    
    _attr_icon = "mdi:calendar-range"
    
    @property
    def name(self) -> str:
        """Return sensor name."""
        return "阶梯周期"
        
    @property
    def unique_id(self) -> Optional[str]:
        """Return unique ID."""
        user_no = self.coordinator.data.get("userNo", "unknown")
        return f"{DOMAIN}_{user_no}_billing_cycle"
        
    @property
    def native_value(self) -> StateType:
        """Return sensor state."""
        return self.coordinator.data.get("jieti_interval")
            
    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        """Return extra state attributes."""
        return {
            "阶梯用气量": self.coordinator.data.get("jieti_amount_benci"),
            "用户名": self.coordinator.data.get("userName"),
        }


class GuangzhouGasAutoPaymentSensor(GuangzhouGasEntity, SensorEntity):
    """Sensor for auto payment status."""
    
    _attr_icon = "mdi:credit-card-check"
    
    @property
    def name(self) -> str:
        """Return sensor name."""
        return "自动扣费"
        
    @property
    def unique_id(self) -> Optional[str]:
        """Return unique ID."""
        user_no = self.coordinator.data.get("userNo", "unknown")
        return f"{DOMAIN}_{user_no}_auto_payment"
        
    @property
    def native_value(self) -> StateType:
        """Return sensor state."""
        return self.coordinator.data.get("feeWay")
            
    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        """Return extra state attributes."""
        return {
            "用户名": self.coordinator.data.get("userName"),
            "用户号": self.coordinator.data.get("userNo"),
        }


class GuangzhouGasSafetyInspectionSensor(GuangzhouGasEntity, SensorEntity):
    """Sensor for safety inspection status."""
    
    _attr_icon = "mdi:shield-check"
    
    @property
    def name(self) -> str:
        """Return sensor name."""
        return "安检状态"
        
    @property
    def unique_id(self) -> Optional[str]:
        """Return unique ID."""
        user_no = self.coordinator.data.get("userNo", "unknown")
        return f"{DOMAIN}_{user_no}_safety_inspection"
        
    @property
    def native_value(self) -> StateType:
        """Return sensor state."""
        return self.coordinator.data.get("safeInspectHas")
            
    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        """Return extra state attributes."""
        return {
            "用户名": self.coordinator.data.get("userName"),
            "用户号": self.coordinator.data.get("userNo"),
            "地址": self.coordinator.data.get("userAddress"),
        }


class GuangzhouGasLastRechargeTimeSensor(GuangzhouGasEntity, SensorEntity):
    """Sensor for last recharge time."""
    
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:clock-outline"
    
    @property
    def name(self) -> str:
        """Return sensor name."""
        return "最近充值时间"
        
    @property
    def unique_id(self) -> Optional[str]:
        """Return unique ID."""
        user_no = self.coordinator.data.get("userNo", "unknown")
        return f"{DOMAIN}_{user_no}_last_recharge_time"
        
    @property
    def native_value(self) -> StateType:
        """Return sensor state."""
        # API 返回的时间格式：20240520143000（YYYYMMDDHHMMSS）
        time_str = self.coordinator.data.get("zhczsj")
        if not time_str or len(time_str) != 14:
            return None
        
        try:
            from datetime import datetime
            dt = datetime.strptime(time_str, "%Y%m%d%H%M%S")
            return dt.isoformat()
        except (ValueError, TypeError):
            return None
            
    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        """Return extra state attributes."""
        return {
            "充值金额": self.coordinator.data.get("zhczje"),
            "累计充值": self.coordinator.data.get("ljczye"),
            "用户名": self.coordinator.data.get("userName"),
        }


class GuangzhouGasUserNameSensor(GuangzhouGasEntity, SensorEntity):
    """Sensor for user name."""

    _attr_icon = "mdi:account"

    @property
    def name(self) -> str:
        return "用户名"

    @property
    def unique_id(self) -> Optional[str]:
        user_no = self.coordinator.data.get("userNo", "unknown")
        return f"{DOMAIN}_{user_no}_user_name"

    @property
    def native_value(self) -> StateType:
        return self.coordinator.data.get("userName")

    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        return {
            "用户号": self.coordinator.data.get("userNo"),
            "地址": self.coordinator.data.get("userAddress"),
        }


class GuangzhouGasUserNoSensor(GuangzhouGasEntity, SensorEntity):
    """Sensor for user number."""

    _attr_icon = "mdi:identifier"

    @property
    def name(self) -> str:
        return "用户号"

    @property
    def unique_id(self) -> Optional[str]:
        user_no = self.coordinator.data.get("userNo", "unknown")
        return f"{DOMAIN}_{user_no}_user_no"

    @property
    def native_value(self) -> StateType:
        return self.coordinator.data.get("userNo")

    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        return {
            "用户名": self.coordinator.data.get("userName"),
            "地址": self.coordinator.data.get("userAddress"),
        }


class GuangzhouGasAddressSensor(GuangzhouGasEntity, SensorEntity):
    """Sensor for address."""

    _attr_icon = "mdi:map-marker"

    @property
    def name(self) -> str:
        return "地址"

    @property
    def unique_id(self) -> Optional[str]:
        user_no = self.coordinator.data.get("userNo", "unknown")
        return f"{DOMAIN}_{user_no}_address"

    @property
    def native_value(self) -> StateType:
        return self.coordinator.data.get("userAddress")

    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        return {
            "用户名": self.coordinator.data.get("userName"),
            "用户号": self.coordinator.data.get("userNo"),
        }


class GuangzhouGasMeterNoSensor(GuangzhouGasEntity, SensorEntity):
    """Sensor for meter number."""

    _attr_icon = "mdi:numeric"

    @property
    def name(self) -> str:
        return "表号"

    @property
    def unique_id(self) -> Optional[str]:
        user_no = self.coordinator.data.get("userNo", "unknown")
        return f"{DOMAIN}_{user_no}_meter_no"

    @property
    def native_value(self) -> StateType:
        return self.coordinator.data.get("bm")

    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        return {
            "用户名": self.coordinator.data.get("userName"),
            "表类型": self.coordinator.data.get("blx"),
        }


class GuangzhouGasMeterTypeSensor(GuangzhouGasEntity, SensorEntity):
    """Sensor for meter type."""

    _attr_icon = "mdi:gauge"

    @property
    def name(self) -> str:
        return "表类型"

    @property
    def unique_id(self) -> Optional[str]:
        user_no = self.coordinator.data.get("userNo", "unknown")
        return f"{DOMAIN}_{user_no}_meter_type"

    @property
    def native_value(self) -> StateType:
        return self.coordinator.data.get("blx")

    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        return {
            "用户名": self.coordinator.data.get("userName"),
            "表号": self.coordinator.data.get("bm"),
        }


class GuangzhouGasLastWatchDateSensor(GuangzhouGasEntity, SensorEntity):
    """Sensor for last watch date."""

    _attr_icon = "mdi:calendar-check"

    @property
    def name(self) -> str:
        return "上次抄表日期"

    @property
    def unique_id(self) -> Optional[str]:
        user_no = self.coordinator.data.get("userNo", "unknown")
        return f"{DOMAIN}_{user_no}_last_watch_date"

    @property
    def native_value(self) -> StateType:
        return self.coordinator.data.get("lastRecordWatchDate")

    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        return {
            "用户名": self.coordinator.data.get("userName"),
            "上次抄表读数": self.coordinator.data.get("lastRecordWatchNum"),
        }
