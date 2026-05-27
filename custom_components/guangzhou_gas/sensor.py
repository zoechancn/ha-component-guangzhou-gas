"""Sensors for Guangzhou Gas."""
from __future__ import annotations

import logging
from datetime import datetime, date, timezone
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
    
    # 创建 36 个传感器实体（16 原有 + 20 新增）
    entities = [
        # 原有 16 个传感器
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
        GuangzhouGasUserNameSensor(coordinator, entry),
        GuangzhouGasUserNoSensor(coordinator, entry),
        GuangzhouGasAddressSensor(coordinator, entry),
        GuangzhouGasMeterNoSensor(coordinator, entry),
        GuangzhouGasMeterTypeSensor(coordinator, entry),
        GuangzhouGasLastWatchDateSensor(coordinator, entry),
        
        # 新增 20 个传感器
        GuangzhouGasCurrentBalanceSensor(coordinator, entry),
        GuangzhouGasFeeFlagSensor(coordinator, entry),
        GuangzhouGasFeeMoneySensor(coordinator, entry),
        GuangzhouGasSafetyInspectionDateSensor(coordinator, entry),
        GuangzhouGasStartFireDateSensor(coordinator, entry),
        GuangzhouGasCompanyNameSensor(coordinator, entry),
        GuangzhouGasPaymentAccountSensor(coordinator, entry),
        GuangzhouGasInsuranceFeeSensor(coordinator, entry),
        GuangzhouGasInsuranceExpireSensor(coordinator, entry),
        GuangzhouGasBillingCycleStartSensor(coordinator, entry),
        GuangzhouGasUserTypeSensor(coordinator, entry),
        GuangzhouGasInsuranceTypeSensor(coordinator, entry),
        GuangzhouGasInsuranceInvalidSensor(coordinator, entry),
        GuangzhouGasGasAddressStatusSensor(coordinator, entry),
        GuangzhouGasCustomerIdSensor(coordinator, entry),
        GuangzhouGasCurrentUsageDetailSensor(coordinator, entry),
        GuangzhouGasMeterLocationSensor(coordinator, entry),
        GuangzhouGasMeterLocationIdSensor(coordinator, entry),
        GuangzhouGasMeterIdDetailSensor(coordinator, entry),
        GuangzhouGasMeterSerialSensor(coordinator, entry),
    ]
    
    async_add_entities(entities)
    _LOGGER.info("Added %d sensors", len(entities))


# ========== 原有 16 个传感器 ==========

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
        return f"{DOMAIN}_{user_no}_last_charge"
        
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
            "累计充值": self.coordinator.data.get("lijczye"),
            "用户名": self.coordinator.data.get("userName"),
        }


class GuangzhouGasTotalRechargeSensor(GuangzhouGasEntity, SensorEntity):
    """Sensor for total recharge amount."""
    
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.TOTAL
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
        return f"{DOMAIN}_{user_no}_total_charge"
        
    @property
    def native_value(self) -> StateType:
        """Return sensor state."""
        value = self.coordinator.data.get("lijczye")
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
            "周期开始": self.coordinator.data.get("jietiTimeBenci"),
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
            "扣费账号": self.coordinator.data.get("backAccount"),
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
            "安检日期": self.coordinator.data.get("safeInspectDate"),
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
        return f"{DOMAIN}_{user_no}_last_charge_time"
        
    @property
    def native_value(self) -> StateType:
        """Return sensor state."""
        # API 返回的时间格式：20240512211243（YYYYMMDDHHMMSS）
        time_str = self.coordinator.data.get("zhczsj")
        _LOGGER.debug("Last recharge time: %s", time_str)
        if not time_str or len(time_str) != 14:
            _LOGGER.debug("Invalid zhczsj format: %s (length: %s)", time_str, len(time_str) if time_str else 0)
            return None
        
        try:
            dt = datetime.strptime(time_str, "%Y%m%d%H%M%S")
            # Home Assistant 2024.x+ 要求返回 datetime 对象（带时区）
            return dt.replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            _LOGGER.error("Failed to parse zhczsj: %s", time_str)
            return None
            
    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        """Return extra state attributes."""
        return {
            "充值金额": self.coordinator.data.get("zhczje"),
            "累计充值": self.coordinator.data.get("lijczye"),
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


# ========== 新增 20 个传感器 ==========

class GuangzhouGasCurrentBalanceSensor(GuangzhouGasEntity, SensorEntity):
    """Sensor for current balance."""
    
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_icon = "mdi:cash-check"
    _attr_native_unit_of_measurement = "元"
    
    @property
    def name(self) -> str:
        return "当期余额"
        
    @property
    def unique_id(self) -> Optional[str]:
        user_no = self.coordinator.data.get("userNo", "unknown")
        return f"{DOMAIN}_{user_no}_current_balance"
        
    @property
    def native_value(self) -> StateType:
        """Return sensor state."""
        value = self.coordinator.data.get("dqye")
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
            
    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        return {
            "用户名": self.coordinator.data.get("userName"),
            "用户号": self.coordinator.data.get("userNo"),
        }


class GuangzhouGasFeeFlagSensor(GuangzhouGasEntity, SensorEntity):
    """Sensor for fee flag."""
    
    _attr_icon = "mdi:alert-circle"
    
    @property
    def name(self) -> str:
        return "欠费标志"
        
    @property
    def unique_id(self) -> Optional[str]:
        user_no = self.coordinator.data.get("userNo", "unknown")
        return f"{DOMAIN}_{user_no}_fee_flag"
        
    @property
    def native_value(self) -> StateType:
        return self.coordinator.data.get("feeFlag")
            
    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        return {
            "欠费金额": self.coordinator.data.get("feeMoney"),
            "用户名": self.coordinator.data.get("userName"),
        }


class GuangzhouGasFeeMoneySensor(GuangzhouGasEntity, SensorEntity):
    """Sensor for fee money."""
    
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_icon = "mdi:cash-remove"
    _attr_native_unit_of_measurement = "元"
    
    @property
    def name(self) -> str:
        return "欠费金额"
        
    @property
    def unique_id(self) -> Optional[str]:
        user_no = self.coordinator.data.get("userNo", "unknown")
        return f"{DOMAIN}_{user_no}_fee_money"
        
    @property
    def native_value(self) -> StateType:
        """Return sensor state."""
        value = self.coordinator.data.get("feeMoney")
        if value is None or value == 0:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
            
    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        return {
            "欠费标志": self.coordinator.data.get("feeFlag"),
            "用户名": self.coordinator.data.get("userName"),
        }


class GuangzhouGasSafetyInspectionDateSensor(GuangzhouGasEntity, SensorEntity):
    """Sensor for safety inspection date."""
    
    _attr_device_class = SensorDeviceClass.DATE
    _attr_icon = "mdi:shield-check"
    
    @property
    def name(self) -> str:
        return "安检日期"
        
    @property
    def unique_id(self) -> Optional[str]:
        user_no = self.coordinator.data.get("userNo", "unknown")
        return f"{DOMAIN}_{user_no}_safety_inspection_date"
        
    @property
    def native_value(self) -> StateType:
        """Return sensor state."""
        date_str = self.coordinator.data.get("safeInspectDate")
        _LOGGER.debug("Safety inspection date: %s", date_str)
        if not date_str:
            return None
        
        # API 返回格式：2025-06-13 00:00:00
        try:
            dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
            # Home Assistant 2024.x+ 要求返回 date 对象
            return dt.date()
        except (ValueError, TypeError):
            _LOGGER.error("Failed to parse safeInspectDate: %s", date_str)
            return None
            
    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        return {
            "安检状态": self.coordinator.data.get("safeInspectHas"),
            "用户名": self.coordinator.data.get("userName"),
        }


class GuangzhouGasStartFireDateSensor(GuangzhouGasEntity, SensorEntity):
    """Sensor for start fire date."""
    
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:fire"
    
    @property
    def name(self) -> str:
        return "点火日期"
        
    @property
    def unique_id(self) -> Optional[str]:
        user_no = self.coordinator.data.get("userNo", "unknown")
        return f"{DOMAIN}_{user_no}_start_fire_date"
        
    @property
    def native_value(self) -> StateType:
        """Return sensor state."""
        time_str = self.coordinator.data.get("startFireDate")
        _LOGGER.debug("Start fire date: %s", time_str)
        if not time_str:
            return None
        
        # API 返回格式：2025-06-12 01:42:17
        try:
            dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
            # Home Assistant 2024.x+ 要求返回 datetime 对象（带时区）
            return dt.replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            _LOGGER.error("Failed to parse startFireDate: %s", time_str)
            return None
            
    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        return {
            "用户名": self.coordinator.data.get("userName"),
            "用户号": self.coordinator.data.get("userNo"),
        }


class GuangzhouGasCompanyNameSensor(GuangzhouGasEntity, SensorEntity):
    """Sensor for company name."""
    
    _attr_icon = "mdi:domain"
    
    @property
    def name(self) -> str:
        return "燃气公司"
        
    @property
    def unique_id(self) -> Optional[str]:
        user_no = self.coordinator.data.get("userNo", "unknown")
        return f"{DOMAIN}_{user_no}_company_name"
        
    @property
    def native_value(self) -> StateType:
        return self.coordinator.data.get("bmmc")
        
    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        return {
            "用户名": self.coordinator.data.get("userName"),
            "用户号": self.coordinator.data.get("userNo"),
        }


class GuangzhouGasPaymentAccountSensor(GuangzhouGasEntity, SensorEntity):
    """Sensor for payment account."""
    
    _attr_icon = "mdi:bank"
    
    @property
    def name(self) -> str:
        return "扣费账号"
        
    @property
    def unique_id(self) -> Optional[str]:
        user_no = self.coordinator.data.get("userNo", "unknown")
        return f"{DOMAIN}_{user_no}_payment_account"
        
    @property
    def native_value(self) -> StateType:
        return self.coordinator.data.get("backAccount")
        
    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        return {
            "自动扣费": self.coordinator.data.get("feeWay"),
            "用户名": self.coordinator.data.get("userName"),
        }


class GuangzhouGasInsuranceFeeSensor(GuangzhouGasEntity, SensorEntity):
    """Sensor for insurance fee."""
    
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_icon = "mdi:shield-plus"
    _attr_native_unit_of_measurement = "元"
    
    @property
    def name(self) -> str:
        return "保险金额"
        
    @property
    def unique_id(self) -> Optional[str]:
        user_no = self.coordinator.data.get("userNo", "unknown")
        return f"{DOMAIN}_{user_no}_insurance_fee"
        
    @property
    def native_value(self) -> StateType:
        """Return sensor state."""
        value = self.coordinator.data.get("bxje")
        if value is None or value == 0:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
            
    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        return {
            "保险缴费类型": self.coordinator.data.get("bxjglx"),
            "保险截止日期": self.coordinator.data.get("bxjzrq"),
            "保险失效日期": self.coordinator.data.get("bxsxrq"),
            "用户名": self.coordinator.data.get("userName"),
        }


class GuangzhouGasInsuranceExpireSensor(GuangzhouGasEntity, SensorEntity):
    """Sensor for insurance expire date."""
    
    _attr_device_class = SensorDeviceClass.DATE
    _attr_icon = "mdi:calendar-clock"
    
    @property
    def name(self) -> str:
        return "保险截止日期"
        
    @property
    def unique_id(self) -> Optional[str]:
        user_no = self.coordinator.data.get("userNo", "unknown")
        return f"{DOMAIN}_{user_no}_insurance_expire"
        
    @property
    def native_value(self) -> StateType:
        """Return sensor state."""
        date_str = self.coordinator.data.get("bxjzrq")
        _LOGGER.debug("Insurance expire date: %s", date_str)
        if not date_str:
            return None
        
        # API 返回格式：2026-06-05
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            # Home Assistant 2024.x+ 要求返回 date 对象
            return dt.date()
        except (ValueError, TypeError):
            _LOGGER.error("Failed to parse bxjzrq: %s", date_str)
            return None
            
    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        return {
            "保险金额": self.coordinator.data.get("bxje"),
            "保险缴费类型": self.coordinator.data.get("bxjglx"),
            "保险失效日期": self.coordinator.data.get("bxsxrq"),
            "用户名": self.coordinator.data.get("userName"),
        }


class GuangzhouGasBillingCycleStartSensor(GuangzhouGasEntity, SensorEntity):
    """Sensor for billing cycle start date."""
    
    _attr_icon = "mdi:calendar-start"
    
    @property
    def name(self) -> str:
        return "阶梯周期开始"
        
    @property
    def unique_id(self) -> Optional[str]:
        user_no = self.coordinator.data.get("userNo", "unknown")
        return f"{DOMAIN}_{user_no}_billing_cycle_start"
        
    @property
    def native_value(self) -> StateType:
        return self.coordinator.data.get("jietiTimeBenci")
            
    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        return {
            "阶梯周期": self.coordinator.data.get("jieti_interval"),
            "阶梯用气量": self.coordinator.data.get("jieti_amount_benci"),
            "用户名": self.coordinator.data.get("userName"),
        }


class GuangzhouGasUserTypeSensor(GuangzhouGasEntity, SensorEntity):
    """Sensor for user type."""
    
    _attr_icon = "mdi:account-group"
    
    @property
    def name(self) -> str:
        return "用户类型"
        
    @property
    def unique_id(self) -> Optional[str]:
        user_no = self.coordinator.data.get("userNo", "unknown")
        return f"{DOMAIN}_{user_no}_user_type"
        
    @property
    def native_value(self) -> StateType:
        return self.coordinator.data.get("userType")
        
    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        return {
            "用户名": self.coordinator.data.get("userName"),
            "用户号": self.coordinator.data.get("userNo"),
        }


class GuangzhouGasInsuranceTypeSensor(GuangzhouGasEntity, SensorEntity):
    """Sensor for insurance type."""
    
    _attr_icon = "mdi:shield-sync"
    
    @property
    def name(self) -> str:
        return "保险缴费类型"
        
    @property
    def unique_id(self) -> Optional[str]:
        user_no = self.coordinator.data.get("userNo", "unknown")
        return f"{DOMAIN}_{user_no}_insurance_type"
        
    @property
    def native_value(self) -> StateType:
        return self.coordinator.data.get("bxjglx")
            
    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        return {
            "保险金额": self.coordinator.data.get("bxje"),
            "保险截止日期": self.coordinator.data.get("bxjzrq"),
            "保险失效日期": self.coordinator.data.get("bxsxrq"),
            "用户名": self.coordinator.data.get("userName"),
        }


class GuangzhouGasInsuranceInvalidSensor(GuangzhouGasEntity, SensorEntity):
    """Sensor for insurance invalid date."""
    
    _attr_device_class = SensorDeviceClass.DATE
    _attr_icon = "mdi:calendar-remove"
    
    @property
    def name(self) -> str:
        return "保险失效日期"
        
    @property
    def unique_id(self) -> Optional[str]:
        user_no = self.coordinator.data.get("userNo", "unknown")
        return f"{DOMAIN}_{user_no}_insurance_invalid"
        
    @property
    def native_value(self) -> StateType:
        """Return sensor state."""
        date_str = self.coordinator.data.get("bxsxrq")
        _LOGGER.debug("Insurance invalid date: %s", date_str)
        if not date_str:
            return None
        
        # API 返回格式：2025-06-05
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            # Home Assistant 2024.x+ 要求返回 date 对象
            return dt.date()
        except (ValueError, TypeError):
            _LOGGER.error("Failed to parse bxsxrq: %s", date_str)
            return None
            
    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        return {
            "保险金额": self.coordinator.data.get("bxje"),
            "保险缴费类型": self.coordinator.data.get("bxjglx"),
            "保险截止日期": self.coordinator.data.get("bxjzrq"),
            "用户名": self.coordinator.data.get("userName"),
        }


class GuangzhouGasGasAddressStatusSensor(GuangzhouGasEntity, SensorEntity):
    """Sensor for gas address status."""
    
    _attr_icon = "mdi:home-check-outline"
    
    @property
    def name(self) -> str:
        return "用气地址状态"
        
    @property
    def unique_id(self) -> Optional[str]:
        user_no = self.coordinator.data.get("userNo", "unknown")
        return f"{DOMAIN}_{user_no}_gas_address_status"
        
    @property
    def native_value(self) -> StateType:
        return self.coordinator.data.get("yqdzztdes")
        
    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        return {
            "用气地址ID": self.coordinator.data.get("yqdzId"),
            "地址": self.coordinator.data.get("userAddress"),
            "用户名": self.coordinator.data.get("userName"),
        }


class GuangzhouGasCustomerIdSensor(GuangzhouGasEntity, SensorEntity):
    """Sensor for customer ID."""
    
    _attr_icon = "mdi:identifier"
    
    @property
    def name(self) -> str:
        return "客户ID"
        
    @property
    def unique_id(self) -> Optional[str]:
        user_no = self.coordinator.data.get("userNo", "unknown")
        return f"{DOMAIN}_{user_no}_customer_id"
        
    @property
    def native_value(self) -> StateType:
        return self.coordinator.data.get("khId")
        
    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        return {
            "用户名": self.coordinator.data.get("userName"),
            "用户号": self.coordinator.data.get("userNo"),
        }


class GuangzhouGasCurrentUsageDetailSensor(GuangzhouGasEntity, SensorEntity):
    """Sensor for current usage (from gas detail API)."""
    
    _attr_device_class = SensorDeviceClass.GAS
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_icon = "mdi:fire-circle"
    _attr_native_unit_of_measurement = "m³"
    
    @property
    def name(self) -> str:
        return "本期用气量"
        
    @property
    def unique_id(self) -> Optional[str]:
        user_no = self.coordinator.data.get("userNo", "unknown")
        return f"{DOMAIN}_{user_no}_current_usage_detail"
        
    @property
    def native_value(self) -> StateType:
        """Return sensor state."""
        value = self.coordinator.data.get("bzqyyql")
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
            
    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        return {
            "阶梯周期用气量": self.coordinator.data.get("jieti_amount_benci"),
            "用户名": self.coordinator.data.get("userName"),
        }


class GuangzhouGasMeterLocationSensor(GuangzhouGasEntity, SensorEntity):
    """Sensor for meter location (from gas detail API - more accurate)."""
    
    _attr_icon = "mdi:map-marker-question"
    
    @property
    def name(self) -> str:
        return "表具安装位置"
        
    @property
    def unique_id(self) -> Optional[str]:
        user_no = self.coordinator.data.get("userNo", "unknown")
        return f"{DOMAIN}_{user_no}_meter_location"
        
    @property
    def native_value(self) -> StateType:
        return self.coordinator.data.get("rqbAzwz")
        
    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        return {
            "表具位置ID": self.coordinator.data.get("rqbWzId"),
            "表具ID": self.coordinator.data.get("rqbId"),
            "用户名": self.coordinator.data.get("userName"),
        }


class GuangzhouGasMeterLocationIdSensor(GuangzhouGasEntity, SensorEntity):
    """Sensor for meter location ID."""
    
    _attr_icon = "mdi:map-marker-outline"
    
    @property
    def name(self) -> str:
        return "表具位置ID"
        
    @property
    def unique_id(self) -> Optional[str]:
        user_no = self.coordinator.data.get("userNo", "unknown")
        return f"{DOMAIN}_{user_no}_meter_location_id"
        
    @property
    def native_value(self) -> StateType:
        return self.coordinator.data.get("rqbWzId")
        
    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        return {
            "表具安装位置": self.coordinator.data.get("rqbAzwz"),
            "表具ID": self.coordinator.data.get("rqbId"),
            "用户名": self.coordinator.data.get("userName"),
        }


class GuangzhouGasMeterIdDetailSensor(GuangzhouGasEntity, SensorEntity):
    """Sensor for meter ID (from gas detail API)."""
    
    _attr_icon = "mdi:numeric-1-circle"
    
    @property
    def name(self) -> str:
        return "表具ID"
        
    @property
    def unique_id(self) -> Optional[str]:
        user_no = self.coordinator.data.get("userNo", "unknown")
        return f"{DOMAIN}_{user_no}_meter_id_detail"
        
    @property
    def native_value(self) -> StateType:
        return self.coordinator.data.get("rqbId")
        
    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        return {
            "表具编号": self.coordinator.data.get("rqbbgh"),
            "表号": self.coordinator.data.get("bm"),
            "用户名": self.coordinator.data.get("userName"),
        }


class GuangzhouGasMeterSerialSensor(GuangzhouGasEntity, SensorEntity):
    """Sensor for meter serial number."""
    
    _attr_icon = "mdi:barcode"
    
    @property
    def name(self) -> str:
        return "表具编号"
        
    @property
    def unique_id(self) -> Optional[str]:
        user_no = self.coordinator.data.get("userNo", "unknown")
        return f"{DOMAIN}_{user_no}_meter_serial"
        
    @property
    def native_value(self) -> StateType:
        return self.coordinator.data.get("rqbbgh")
        
    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        return {
            "表具ID": self.coordinator.data.get("rqbId"),
            "表号": self.coordinator.data.get("bm"),
            "用户名": self.coordinator.data.get("userName"),
        }
