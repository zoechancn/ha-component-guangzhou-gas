"""Support for Guangzhou Gas."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    CONF_NICKNAME,
    CONF_ACCEPT_KEY,
    CONF_UNIONID,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
)
from .coordinator import GuangzhouGasDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# 配置 Schema（如果使用 YAML 配置，本集成使用 config_flow，不需要）
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required("nickname"): cv.string,
                vol.Required("accept_key"): cv.string,
                vol.Required("unionid"): cv.string,
                vol.Optional("scan_interval", default=10800): cv.positive_int,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Guangzhou Gas component from YAML configuration.
    
    Args:
        hass: Home Assistant instance.
        config: Configuration dictionary.
        
    Returns:
        True if setup successful, False otherwise.
    """
    _LOGGER.info("Setting up Guangzhou Gas component from YAML")
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Guangzhou Gas from a config entry.
    
    Args:
        hass: Home Assistant instance.
        entry: Config entry.
        
    Returns:
        True if setup successful, False otherwise.
    """
    _LOGGER.info("Setting up Guangzhou Gas integration (entry_id=%s)", entry.entry_id)
    
    # 从配置条目中获取配置
    nickname = entry.data[CONF_NICKNAME]
    accept_key = entry.data[CONF_ACCEPT_KEY]
    unionid = entry.data[CONF_UNIONID]
    scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    
    # 创建 API 客户端
    session = async_get_clientsession(hass)
    from .api import GuangzhouGasAPI
    api = GuangzhouGasAPI(session, nickname, accept_key, unionid)
    
    # 创建数据协调器
    coordinator = GuangzhouGasDataUpdateCoordinator(
        hass,
        api,
        scan_interval,
    )
    
    # 首次更新数据
    await coordinator.async_config_entry_first_refresh()
    
    # 存储协调器到 hass.data
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    
    # 转发传感器平台（新版本 API）
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    
    # 监听配置条目的更新/卸载
    entry.async_on_unload(entry.add_update_listener(async_update_options))
    
    _LOGGER.info("Guangzhou Gas integration setup completed")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry.
    
    Args:
        hass: Home Assistant instance.
        entry: Config entry.
        
    Returns:
        True if unload successful, False otherwise.
    """
    _LOGGER.info("Unloading Guangzhou Gas integration (entry_id=%s)", entry.entry_id)
    
    # 卸载传感器平台（新版本 API）
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    
    # 从 hass.data 中移除协调器
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)
        _LOGGER.info("Guangzhou Gas integration unloaded successfully")
    
    return unload_ok


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options.
    
    Args:
        hass: Home Assistant instance.
        entry: Config entry.
    """
    _LOGGER.info("Updating Guangzhou Gas integration options (entry_id=%s)", entry.entry_id)
    await hass.config_entries.async_reload(entry.entry_id)


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate old entry data to new version.
    
    Args:
        hass: Home Assistant instance.
        entry: Config entry.
        
    Returns:
        True if migration successful, False otherwise.
    """
    _LOGGER.info("Migrating Guangzhou Gas integration from version %s to %s", 
                 entry.version, entry.minor_version)
    
    # 示例：从版本 1 迁移到版本 2
    # if entry.version == 1:
    #     new_data = {**entry.data}
    #     new_data["new_field"] = "default_value"
    #     entry.version = 2
    #     hass.config_entries.async_update_entry(entry, data=new_data)
    
    _LOGGER.info("Migration completed")
    return True
