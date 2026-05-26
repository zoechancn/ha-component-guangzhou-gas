"""Constants for Guangzhou Gas integration."""
from __future__ import annotations

from datetime import timedelta

# 集成域名
DOMAIN = "guangzhou_gas"

# 配置键名
CONF_NICKNAME = "nickname"
CONF_ACCEPT_KEY = "accept_key"
CONF_UNIONID = "unionid"
CONF_SCAN_INTERVAL = "scan_interval"

# 默认配置
DEFAULT_SCAN_INTERVAL = 10800  # 3 小时（秒）

# API 端点 URL
API_BASE_URL = "https://wxxcx.gzgas.com/ydeq/min"
API_LOGIN_URL = f"{API_BASE_URL}/login/getToken.action"
API_USER_INFO_URL = f"{API_BASE_URL}/bind/getUserByShowIndex.action"
API_GAS_DETAIL_URL = f"{API_BASE_URL}/order/getBiaoDetail.action"

# HTTP 请求头
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
}

# 传感器类型定义
SENSOR_TYPES = {
    "balance": {
        "name": "燃气余额",
        "icon": "mdi:cash",
        "device_class": "monetary",
        "state_class": None,
        "unit": "元",
        "value_key": "money",
    },
    "gas_usage": {
        "name": "阶梯周期用气量",
        "icon": "mdi:fire",
        "device_class": "gas",
        "state_class": "total_increasing",
        "unit": "m³",
        "value_key": "jieti_amount_benci",
    },
    "meter_status": {
        "name": "燃气表状态",
        "icon": "mdi:gas-cylinder",
        "device_class": None,
        "state_class": None,
        "unit": None,
        "value_key": "rqbztdes",
    },
    "last_reading": {
        "name": "上次抄表读数",
        "icon": "mdi:counter",
        "device_class": None,
        "state_class": None,
        "unit": "m³",
        "value_key": "lastRecordWatchNum",
    },
    "last_recharge": {
        "name": "最近充值金额",
        "icon": "mdi:cash-plus",
        "device_class": "monetary",
        "state_class": None,
        "unit": "元",
        "value_key": "zhczje",
    },
    "total_recharge": {
        "name": "累计充值金额",
        "icon": "mdi:cash",
        "device_class": "monetary",
        "state_class": "total_increasing",
        "unit": "元",
        "value_key": "ljczye",
    },
    "billing_cycle": {
        "name": "阶梯周期",
        "icon": "mdi:calendar-range",
        "device_class": None,
        "state_class": None,
        "unit": None,
        "value_key": "jieti_interval",
    },
    "auto_payment": {
        "name": "自动扣费",
        "icon": "mdi:credit-card-check",
        "device_class": None,
        "state_class": None,
        "unit": None,
        "value_key": "feeWay",
    },
    "safety_inspection": {
        "name": "安检状态",
        "icon": "mdi:shield-check",
        "device_class": None,
        "state_class": None,
        "unit": None,
        "value_key": "safeInspectHas",
    },
    "last_recharge_time": {
        "name": "最近充值时间",
        "icon": "mdi:clock-outline",
        "device_class": "timestamp",
        "state_class": None,
        "unit": None,
        "value_key": "zhczsj",
    },
}

# 设备信息键名
DEVICE_INFO_KEYS = {
    "identifiers": "userNo",  # 用户号作为设备唯一标识
    "name": "userName",        # 用户名
    "model": "blx",           # 表类型
    "sw_version": None,       # 软件版本（API 未提供）
    "manufacturer": "广州燃气",  # 制造商
    "via_device": None,       # 通过哪个设备连接（无）
}

# 额外属性键名（从 API 数据中提取）
EXTRA_STATE_ATTRIBUTES = {
    "user_name": "userName",
    "user_no": "userNo",
    "address": "userAddress",
    "meter_no": "bm",
    "meter_status": "rqbztdes",
    "billing_cycle": "jieti_interval",
    "auto_payment": "feeWay",
    "safety_inspection": "safeInspectHas",
    "last_recharge_time": "zhczsj",
}
