"""Entity base class for Guangzhou Gas."""
from __future__ import annotations

from typing import Any, Mapping, Optional

from homeassistant.helpers.entity import Entity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import DeviceInfo


class GuangzhouGasEntity(Entity):
    """Base entity for Guangzhou Gas."""
    
    _attr_has_entity_name = True
    _attr_should_poll = False
    
    def __init__(
        self,
        coordinator: Any,  # GuangzhouGasDataUpdateCoordinator
        entry: ConfigEntry,
    ) -> None:
        """Initialize the entity.
        
        Args:
            coordinator: Data update coordinator.
            entry: Config entry.
        """
        self.coordinator = coordinator
        self._entry = entry
        self._attr_device_info = self._get_device_info()
        
    @property
    def available(self) -> bool:
        """Return if entity is available.
        
        Returns:
            True if coordinator data is available, False otherwise.
        """
        return self.coordinator.last_update_success
        
    @property
    def should_poll(self) -> bool:
        """Return if entity should poll for updates.
        
        Returns:
            False (uses coordinator).
        """
        return False
        
    @property
    def unique_id(self) -> Optional[str]:
        """Return unique ID for entity.
        
        Returns:
            Unique ID string.
        """
        # 格式: {domain}_{user_no}_{sensor_type}
        user_no = self.coordinator.data.get("userNo", "unknown")
        sensor_type = self._get_sensor_type()
        return f"{DOMAIN}_{user_no}_{sensor_type}"
        
    def _get_device_info(self) -> DeviceInfo:
        """Get device info from coordinator data.
        
        Returns:
            DeviceInfo dictionary.
        """
        data = self.coordinator.data
        user_no = data.get("userNo", "unknown")
        user_name = data.get("userName", "Unknown")
        meter_type = data.get("blx", "Unknown")
        
        return {
            "identifiers": {(DOMAIN, user_no)},
            "name": f"广州燃气 - {user_name}",
            "model": meter_type,
            "manufacturer": "广州燃气",
            # sw_version: API 未提供，暂不使用
            # via_device: 无中间设备
        }
        
    def _get_sensor_type(self) -> str:
        """Get sensor type identifier.
        
        Returns:
            Sensor type string (should be overridden by subclasses).
        """
        return "unknown"
        
    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
