"""Base entities for Guangzhou Gas."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import GuangzhouGasDataUpdateCoordinator


class GuangzhouGasEntity(CoordinatorEntity[GuangzhouGasDataUpdateCoordinator]):
    """Base class shared by Guangzhou Gas entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: GuangzhouGasDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator-backed entity."""
        super().__init__(coordinator)
        self._entry = entry

    @property
    def device_info(self) -> DeviceInfo:
        """Return a stable, privacy-conscious gas meter device."""
        data = self.coordinator.data
        user_no = str(data.get("userNo", "unknown"))
        return DeviceInfo(
            identifiers={(DOMAIN, user_no)},
            name="广州燃气表",
            manufacturer="广州燃气",
            model=str(data.get("blx") or "燃气表"),
        )
