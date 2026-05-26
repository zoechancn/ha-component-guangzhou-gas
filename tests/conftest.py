"""Pytest configuration - mock homeassistant before imports.
This file is loaded by pytest before any test files.
"""
import sys
from unittest.mock import MagicMock, AsyncMock

# =============================================================================
# Mock ALL homeassistant modules BEFORE any imports
# This must be at the TOP of conftest.py with NO other imports above
# =============================================================================

# ---- Mock classes ----
class MockEntity:
    """Mock homeassistant.helpers.entity.Entity."""
    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_name = None
    _attr_unique_id = None
    _attr_device_info = None
    _attr_icon = None
    
    def __init__(self):
        self.hass = None
        self._attr_available = True
        self.coordinator = None
        self._entry = None
    
    @property
    def name(self):
        return self._attr_name
    
    @property
    def unique_id(self):
        return self._attr_unique_id
    
    @property
    def device_info(self):
        return self._attr_device_info
    
    @property
    def should_poll(self):
        return self._attr_should_poll
    
    @property
    def available(self):
        return self._attr_available
    
    @available.setter
    def available(self, value):
        self._attr_available = value
    
    async def async_added_to_hass(self):
        pass
    
    def async_on_remove(self, func):
        pass


class MockSensorEntity(MockEntity):
    """Mock SensorEntity."""
    _attr_device_class = None
    _attr_state_class = None
    _attr_native_unit_of_measurement = None
    _attr_native_value = None
    
    @property
    def native_value(self):
        return self._attr_native_value
    
    @property
    def state(self):
        return self._attr_native_value


class MockConfigEntry:
    """Mock ConfigEntry."""
    def __init__(self, version=1, minor_version=0, domain="", title="", data=None, source="", state=1, unique_id=""):
        self.version = version
        self.minor_version = minor_version
        self.domain = domain
        self.title = title
        self.data = data or {}
        self.source = source
        self.state = state
        self.unique_id = unique_id
        self.entry_id = "test_entry_id"
    
    def add_update_listener(self, func):
        pass


class MockDataUpdateCoordinator:
    """Mock DataUpdateCoordinator."""
    def __init__(self, hass, logger, name=None, update_interval=None):
        self.hass = hass
        self.logger = logger
        self.name = name
        self.update_interval = update_interval
        self.data = None
        self.last_update_success = True
        self._listeners = []
    
    async def async_config_entry_first_refresh(self):
        self.data = {}
        return True
    
    async def _async_update_data(self):
        return {}
    
    def async_add_listener(self, listener):
        self._listeners.append(listener)
        return lambda: None


class ConfigEntryAuthFailed(Exception):
    pass


class UpdateFailed(Exception):
    pass


# ---- Create mock modules ----
mock_ha_core = MagicMock()
mock_ha_core.HomeAssistant = type("HomeAssistant", (), {"__init__": lambda self: None})
mock_ha_core.ConfigEntryAuthFailed = ConfigEntryAuthFailed
mock_ha_core.UpdateFailed = UpdateFailed

mock_entity = MagicMock()
mock_entity.Entity = MockEntity

mock_entity_platform = MagicMock()
mock_entity_platform.AddEntitiesCallback = MagicMock()

mock_update_coordinator = MagicMock()
mock_update_coordinator.DataUpdateCoordinator = MockDataUpdateCoordinator
mock_update_coordinator.ConfigEntryAuthFailed = ConfigEntryAuthFailed
mock_update_coordinator.UpdateFailed = UpdateFailed

mock_sensor = MagicMock()
mock_sensor.SensorEntity = MockSensorEntity
mock_sensor.SensorDeviceClass = type("SensorDeviceClass", (), {
    "MONETARY": "monetary",
    "GAS": "gas", 
    "TIMESTAMP": "timestamp"
})
mock_sensor.SensorStateClass = type("SensorStateClass", (), {
    "TOTAL_INCREASING": "total_increasing",
    "MEASUREMENT": "measurement"
})

mock_typing = MagicMock()
mock_typing.DeviceInfo = dict
mock_typing.StateType = object

mock_aiohttp_client = MagicMock()
mock_aiohttp_client.async_get_clientsession = AsyncMock(return_value=MagicMock())

mock_config_validation = MagicMock()
mock_config_validation.ConfigValidation = MagicMock()

mock_config_entries = MagicMock()
mock_config_entries.ConfigEntry = MockConfigEntry
mock_config_entries.ConfigFlow = type("ConfigFlow", (), {"__init__": lambda self: None})
mock_config_entries.FlowResult = dict

mock_data_entry_flow = MagicMock()
mock_data_entry_flow.FlowResult = dict

# ---- Inject mocks into sys.modules BEFORE any other imports ----
sys.modules["homeassistant"] = mock_ha_core
sys.modules["homeassistant.core"] = mock_ha_core
sys.modules["homeassistant.config_entries"] = mock_config_entries
sys.modules["homeassistant.data_entry_flow"] = mock_data_entry_flow
sys.modules["homeassistant.helpers"] = MagicMock()
sys.modules["homeassistant.helpers.entity"] = mock_entity
sys.modules["homeassistant.helpers.entity_platform"] = mock_entity_platform
sys.modules["homeassistant.helpers.update_coordinator"] = mock_update_coordinator
sys.modules["homeassistant.helpers.typing"] = mock_typing
sys.modules["homeassistant.helpers.aiohttp_client"] = mock_aiohttp_client
sys.modules["homeassistant.helpers.config_validation"] = mock_config_validation
sys.modules["homeassistant.components"] = MagicMock()
sys.modules["homeassistant.components.sensor"] = mock_sensor

# Mock voluptuous
sys.modules["voluptuous"] = MagicMock()
sys.modules["homeassistant.helpers.config_validation"].vol = MagicMock()
sys.modules["homeassistant.helpers.config_validation"].cv = MagicMock()

# =============================================================================
# NOW we can safely import custom_components
# =============================================================================

import json
import os
from typing import Any, Dict

# Test data
MOCK_CONFIG = {
    "nickname": "test_user",
    "accept_key": "test_accept_key", 
    "unionid": "test_unionid",
    "scan_interval": 10800,
}

MOCK_USER_INFO_DATA = {
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


@pytest.fixture
def mock_config():
    return MOCK_CONFIG.copy()


@pytest.fixture
def mock_coordinator_data():
    return MOCK_USER_INFO_DATA.copy()


def load_fixture(filename: str) -> Dict[str, Any]:
    """Load a fixture file."""
    fixture_path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
    with open(fixture_path, "r", encoding="utf-8") as f:
        return json.load(f)
