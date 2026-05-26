"""Tests for Guangzhou Gas sensors."""
from __future__ import annotations

import pytest
from typing import Any, Dict, Optional
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.helpers.typing import StateType

from custom_components.guangzhou_gas.const import DOMAIN
from custom_components.guangzhou_gas.sensor import (
    GuangzhouGasBalanceSensor,
    GuangzhouGasGasUsageSensor,
    GuangzhouGasMeterStatusSensor,
    GuangzhouGasLastReadingSensor,
    GuangzhouGasLastRechargeSensor,
    GuangzhouGasTotalRechargeSensor,
    GuangzhouGasBillingCycleSensor,
    GuangzhouGasAutoPaymentSensor,
    GuangzhouGasSafetyInspectionSensor,
    GuangzhouGasLastRechargeTimeSensor,
)


# 模拟协调器数据
MOCK_COORDINATOR_DATA = {
    "userName": "测试用户",
    "userNo": "711111111",
    "userAddress": "广州市天河区测试路1号",
    "money": "100.50",
    "bm": "BM11111111",
    "blx": "IC卡表",
    "rqbztdes": "正常",
    "jieti_interval": "2024-01-01 至 2024-12-31",
    "jieti_amount_benci": "120",
    "lastRecordWatchNum": "1000",
    "lastRecordWatchDate": "2024-01-15",
    "zhczje": "200",
    "zhczsj": "20240520143000",
    "ljczye": "500",
    "feeWay": "银行代扣",
    "safeInspectHas": "已安检"
}


class MockCoordinator:
    """Mock DataUpdateCoordinator for testing."""
    
    def __init__(self, data: Dict[str, Any] = None):
        """Initialize mock coordinator."""
        self.data = data or MOCK_COORDINATOR_DATA.copy()
        self.last_update_success = True
        self._listeners = []
    
    def async_add_listener(self, listener):
        """Add listener."""
        self._listeners.append(listener)
        return lambda: None


class MockConfigEntry:
    """Mock ConfigEntry for testing."""
    
    def __init__(self, entry_id: str = "test_entry_id"):
        """Initialize mock config entry."""
        self.entry_id = entry_id
        self.data = {
            "nickname": "test_user",
            "accept_key": "test_key",
            "unionid": "test_unionid",
            "scan_interval": 10800,
        }


@pytest.fixture
def mock_coordinator() -> MockCoordinator:
    """Create a mock coordinator."""
    return MockCoordinator(MOCK_COORDINATOR_DATA.copy())


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Create a mock config entry."""
    return MockConfigEntry()


# ==================== 燃气余额传感器测试 ====================

class TestGuangzhouGasBalanceSensor:
    """Test GuangzhouGasBalanceSensor."""
    
    @pytest.mark.asyncio
    async def test_sensor_creation(self, mock_coordinator: MockCoordinator, mock_config_entry: MockConfigEntry):
        """Test sensor creation."""
        sensor = GuangzhouGasBalanceSensor(mock_coordinator, mock_config_entry)
        assert sensor is not None
        assert sensor.name == "燃气余额"
        assert sensor.icon == "mdi:cash"
        assert sensor.native_unit_of_measurement == "元"
        assert sensor.device_class == SensorDeviceClass.MONETARY
    
    @pytest.mark.asyncio
    async def test_native_value_success(self, mock_coordinator: MockCoordinator, mock_config_entry: MockConfigEntry):
        """Test native_value with valid data."""
        sensor = GuangzhouGasBalanceSensor(mock_coordinator, mock_config_entry)
        assert sensor.native_value == 100.50
    
    @pytest.mark.asyncio
    async def test_native_value_none(self, mock_coordinator: MockCoordinator, mock_config_entry: MockConfigEntry):
        """Test native_value with None data."""
        mock_coordinator.data["money"] = None
        sensor = GuangzhouGasBalanceSensor(mock_coordinator, mock_config_entry)
        assert sensor.native_value is None
    
    @pytest.mark.asyncio
    async def test_native_value_invalid(self, mock_coordinator: MockCoordinator, mock_config_entry: MockConfigEntry):
        """Test native_value with invalid data."""
        mock_coordinator.data["money"] = "invalid"
        sensor = GuangzhouGasBalanceSensor(mock_coordinator, mock_config_entry)
        assert sensor.native_value is None
    
    @pytest.mark.asyncio
    async def test_unique_id(self, mock_coordinator: MockCoordinator, mock_config_entry: MockConfigEntry):
        """Test unique_id."""
        sensor = GuangzhouGasBalanceSensor(mock_coordinator, mock_config_entry)
        assert sensor.unique_id == f"{DOMAIN}_711111111_balance"
    
    @pytest.mark.asyncio
    async def test_extra_state_attributes(self, mock_coordinator: MockCoordinator, mock_config_entry: MockConfigEntry):
        """Test extra_state_attributes."""
        sensor = GuangzhouGasBalanceSensor(mock_coordinator, mock_config_entry)
        attrs = sensor.extra_state_attributes
        assert attrs["用户名"] == "测试用户"
        assert attrs["用户号"] == "711111111"
        assert attrs["地址"] == "广州市天河区测试路1号"
    
    @pytest.mark.asyncio
    async def test_available(self, mock_coordinator: MockCoordinator, mock_config_entry: MockConfigEntry):
        """Test available property."""
        sensor = GuangzhouGasBalanceSensor(mock_coordinator, mock_config_entry)
        assert sensor.available is True
        
        mock_coordinator.last_update_success = False
        assert sensor.available is False


# ==================== 阶梯周期用气量传感器测试 ====================

class TestGuangzhouGasGasUsageSensor:
    """Test GuangzhouGasGasUsageSensor."""
    
    @pytest.mark.asyncio
    async def test_sensor_creation(self, mock_coordinator: MockCoordinator, mock_config_entry: MockConfigEntry):
        """Test sensor creation."""
        sensor = GuangzhouGasGasUsageSensor(mock_coordinator, mock_config_entry)
        assert sensor.name == "阶梯周期用气量"
        assert sensor.icon == "mdi:fire"
        assert sensor.native_unit_of_measurement == "m³"
        assert sensor.device_class == SensorDeviceClass.GAS
        assert sensor.state_class == SensorEntity.StateClass.TOTAL_INCREASING
    
    @pytest.mark.asyncio
    async def test_native_value_success(self, mock_coordinator: MockCoordinator, mock_config_entry: MockConfigEntry):
        """Test native_value with valid data."""
        sensor = GuangzhouGasGasUsageSensor(mock_coordinator, mock_config_entry)
        assert sensor.native_value == 120.0
    
    @pytest.mark.asyncio
    async def test_native_value_none(self, mock_coordinator: MockCoordinator, mock_config_entry: MockConfigEntry):
        """Test native_value with None data."""
        mock_coordinator.data["jieti_amount_benci"] = None
        sensor = GuangzhouGasGasUsageSensor(mock_coordinator, mock_config_entry)
        assert sensor.native_value is None


# ==================== 燃气表状态传感器测试 ====================

class TestGuangzhouGasMeterStatusSensor:
    """Test GuangzhouGasMeterStatusSensor."""
    
    @pytest.mark.asyncio
    async def test_sensor_creation(self, mock_coordinator: MockCoordinator, mock_config_entry: MockConfigEntry):
        """Test sensor creation."""
        sensor = GuangzhouGasMeterStatusSensor(mock_coordinator, mock_config_entry)
        assert sensor.name == "燃气表状态"
        assert sensor.icon == "mdi:gas-cylinder"
    
    @pytest.mark.asyncio
    async def test_native_value(self, mock_coordinator: MockCoordinator, mock_config_entry: MockConfigEntry):
        """Test native_value."""
        sensor = GuangzhouGasMeterStatusSensor(mock_coordinator, mock_config_entry)
        assert sensor.native_value == "正常"
    
    @pytest.mark.asyncio
    async def test_native_value_none(self, mock_coordinator: MockCoordinator, mock_config_entry: MockConfigEntry):
        """Test native_value with None."""
        mock_coordinator.data["rqbztdes"] = None
        sensor = GuangzhouGasMeterStatusSensor(mock_coordinator, mock_config_entry)
        assert sensor.native_value is None


# ==================== 上次抄表读数传感器测试 ====================

class TestGuangzhouGasLastReadingSensor:
    """Test GuangzhouGasLastReadingSensor."""
    
    @pytest.mark.asyncio
    async def test_sensor_creation(self, mock_coordinator: MockCoordinator, mock_config_entry: MockConfigEntry):
        """Test sensor creation."""
        sensor = GuangzhouGasLastReadingSensor(mock_coordinator, mock_config_entry)
        assert sensor.name == "上次抄表读数"
        assert sensor.icon == "mdi:counter"
        assert sensor.native_unit_of_measurement == "m³"
    
    @pytest.mark.asyncio
    async def test_state_success(self, mock_coordinator: MockCoordinator, mock_config_entry: MockConfigEntry):
        """Test state with valid data."""
        # 注意：这个传感器使用 state 而不是 native_value
        sensor = GuangzhouGasLastReadingSensor(mock_coordinator, mock_config_entry)
        assert sensor.state == 1000.0
    
    @pytest.mark.asyncio
    async def test_state_none(self, mock_coordinator: MockCoordinator, mock_config_entry: MockConfigEntry):
        """Test state with None data."""
        mock_coordinator.data["lastRecordWatchNum"] = None
        sensor = GuangzhouGasLastReadingSensor(mock_coordinator, mock_config_entry)
        assert sensor.state is None


# ==================== 最近充值金额传感器测试 ====================

class TestGuangzhouGasLastRechargeSensor:
    """Test GuangzhouGasLastRechargeSensor."""
    
    @pytest.mark.asyncio
    async def test_sensor_creation(self, mock_coordinator: MockCoordinator, mock_config_entry: MockConfigEntry):
        """Test sensor creation."""
        sensor = GuangzhouGasLastRechargeSensor(mock_coordinator, mock_config_entry)
        assert sensor.name == "最近充值金额"
        assert sensor.icon == "mdi:cash-plus"
        assert sensor.native_unit_of_measurement == "元"
        assert sensor.device_class == SensorDeviceClass.MONETARY
    
    @pytest.mark.asyncio
    async def test_native_value_success(self, mock_coordinator: MockCoordinator, mock_config_entry: MockConfigEntry):
        """Test native_value with valid data."""
        sensor = GuangzhouGasLastRechargeSensor(mock_coordinator, mock_config_entry)
        assert sensor.native_value == 200.0


# ==================== 累计充值金额传感器测试 ====================

class TestGuangzhouGasTotalRechargeSensor:
    """Test GuangzhouGasTotalRechargeSensor."""
    
    @pytest.mark.asyncio
    async def test_sensor_creation(self, mock_coordinator: MockCoordinator, mock_config_entry: MockConfigEntry):
        """Test sensor creation."""
        sensor = GuangzhouGasTotalRechargeSensor(mock_coordinator, mock_config_entry)
        assert sensor.name == "累计充值金额"
        assert sensor.state_class == SensorEntity.StateClass.TOTAL_INCREASING
    
    @pytest.mark.asyncio
    async def test_native_value_success(self, mock_coordinator: MockCoordinator, mock_config_entry: MockConfigEntry):
        """Test native_value with valid data."""
        sensor = GuangzhouGasTotalRechargeSensor(mock_coordinator, mock_config_entry)
        assert sensor.native_value == 500.0


# ==================== 阶梯周期传感器测试 ====================

class TestGuangzhouGasBillingCycleSensor:
    """Test GuangzhouGasBillingCycleSensor."""
    
    @pytest.mark.asyncio
    async def test_sensor_creation(self, mock_coordinator: MockCoordinator, mock_config_entry: MockConfigEntry):
        """Test sensor creation."""
        sensor = GuangzhouGasBillingCycleSensor(mock_coordinator, mock_config_entry)
        assert sensor.name == "阶梯周期"
        assert sensor.icon == "mdi:calendar-range"
    
    @pytest.mark.asyncio
    async def test_native_value(self, mock_coordinator: MockCoordinator, mock_config_entry: MockConfigEntry):
        """Test native_value."""
        sensor = GuangzhouGasBillingCycleSensor(mock_coordinator, mock_config_entry)
        assert sensor.native_value == "2024-01-01 至 2024-12-31"


# ==================== 自动扣费传感器测试 ====================

class TestGuangzhouGasAutoPaymentSensor:
    """Test GuangzhouGasAutoPaymentSensor."""
    
    @pytest.mark.asyncio
    async def test_sensor_creation(self, mock_coordinator: MockCoordinator, mock_config_entry: MockConfigEntry):
        """Test sensor creation."""
        sensor = GuangzhouGasAutoPaymentSensor(mock_coordinator, mock_config_entry)
        assert sensor.name == "自动扣费"
        assert sensor.icon == "mdi:credit-card-check"
    
    @pytest.mark.asyncio
    async def test_native_value(self, mock_coordinator: MockCoordinator, mock_config_entry: MockConfigEntry):
        """Test native_value."""
        sensor = GuangzhouGasAutoPaymentSensor(mock_coordinator, mock_config_entry)
        assert sensor.native_value == "银行代扣"


# ==================== 安检状态传感器测试 ====================

class TestGuangzhouGasSafetyInspectionSensor:
    """Test GuangzhouGasSafetyInspectionSensor."""
    
    @pytest.mark.asyncio
    async def test_sensor_creation(self, mock_coordinator: MockCoordinator, mock_config_entry: MockConfigEntry):
        """Test sensor creation."""
        sensor = GuangzhouGasSafetyInspectionSensor(mock_coordinator, mock_config_entry)
        assert sensor.name == "安检状态"
        assert sensor.icon == "mdi:shield-check"
    
    @pytest.mark.asyncio
    async def test_native_value(self, mock_coordinator: MockCoordinator, mock_config_entry: MockConfigEntry):
        """Test native_value."""
        sensor = GuangzhouGasSafetyInspectionSensor(mock_coordinator, mock_config_entry)
        assert sensor.native_value == "已安检"


# ==================== 最近充值时间传感器测试 ====================

class TestGuangzhouGasLastRechargeTimeSensor:
    """Test GuangzhouGasLastRechargeTimeSensor."""
    
    @pytest.mark.asyncio
    async def test_sensor_creation(self, mock_coordinator: MockCoordinator, mock_config_entry: MockConfigEntry):
        """Test sensor creation."""
        sensor = GuangzhouGasLastRechargeTimeSensor(mock_coordinator, mock_config_entry)
        assert sensor.name == "最近充值时间"
        assert sensor.icon == "mdi:clock-outline"
        assert sensor.device_class == SensorDeviceClass.TIMESTAMP
    
    @pytest.mark.asyncio
    async def test_native_value_success(self, mock_coordinator: MockCoordinator, mock_config_entry: MockConfigEntry):
        """Test native_value with valid time string."""
        sensor = GuangzhouGasLastRechargeTimeSensor(mock_coordinator, mock_config_entry)
        # 20240520143000 -> 2024-05-20T14:30:00
        result = sensor.native_value
        assert result is not None
        assert "2024-05-20T14:30:00" == result
    
    @pytest.mark.asyncio
    async def test_native_value_invalid_format(self, mock_coordinator: MockCoordinator, mock_config_entry: MockConfigEntry):
        """Test native_value with invalid time format."""
        mock_coordinator.data["zhczsj"] = "invalid"
        sensor = GuangzhouGasLastRechargeTimeSensor(mock_coordinator, mock_config_entry)
        assert sensor.native_value is None
    
    @pytest.mark.asyncio
    async def test_native_value_none(self, mock_coordinator: MockCoordinator, mock_config_entry: MockConfigEntry):
        """Test native_value with None."""
        mock_coordinator.data["zhczsj"] = None
        sensor = GuangzhouGasLastRechargeTimeSensor(mock_coordinator, mock_config_entry)
        assert sensor.native_value is None
    
    @pytest.mark.asyncio
    async def test_native_value_wrong_length(self, mock_coordinator: MockCoordinator, mock_config_entry: MockConfigEntry):
        """Test native_value with wrong length time string."""
        mock_coordinator.data["zhczsj"] = "20240520"  # 只有8位，不是14位
        sensor = GuangzhouGasLastRechargeTimeSensor(mock_coordinator, mock_config_entry)
        assert sensor.native_value is None


# ==================== 所有传感器创建测试 ====================

class TestAllSensorsCreation:
    """Test all sensors can be created."""
    
    @pytest.mark.asyncio
    async def test_create_all_sensors(self, mock_coordinator: MockCoordinator, mock_config_entry: MockConfigEntry):
        """Test creating all 10 sensors."""
        sensors = [
            GuangzhouGasBalanceSensor(mock_coordinator, mock_config_entry),
            GuangzhouGasGasUsageSensor(mock_coordinator, mock_config_entry),
            GuangzhouGasMeterStatusSensor(mock_coordinator, mock_config_entry),
            GuangzhouGasLastReadingSensor(mock_coordinator, mock_config_entry),
            GuangzhouGasLastRechargeSensor(mock_coordinator, mock_config_entry),
            GuangzhouGasTotalRechargeSensor(mock_coordinator, mock_config_entry),
            GuangzhouGasBillingCycleSensor(mock_coordinator, mock_config_entry),
            GuangzhouGasAutoPaymentSensor(mock_coordinator, mock_config_entry),
            GuangzhouGasSafetyInspectionSensor(mock_coordinator, mock_config_entry),
            GuangzhouGasLastRechargeTimeSensor(mock_coordinator, mock_config_entry),
        ]
        
        assert len(sensors) == 10
        
        for sensor in sensors:
            assert sensor is not None
            assert sensor.name is not None
            assert sensor.unique_id is not None
            assert sensor.coordinator is not None
