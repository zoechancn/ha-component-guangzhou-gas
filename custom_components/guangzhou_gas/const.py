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

# HTTP 请求头（模拟 Node-RED 微信小程序请求）
DEFAULT_HEADERS = {
    "Host": "wxxcx.gzgas.com",
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0xf254186b) XWEB/19481",
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "*/*",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://servicewechat.com/wx6a4fd0ebb4a12c11/366/page-frame.html",
    "Accept-Language": "zh-CN,zh;q=0.9",
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
    # 新增传感器（从 Node-RED 流程中提取的额外字段）
    "user_name": {
        "name": "用户名",
        "icon": "mdi:account",
        "device_class": None,
        "state_class": None,
        "unit": None,
        "value_key": "userName",
    },
    "user_no": {
        "name": "用户号",
        "icon": "mdi:identifier",
        "device_class": None,
        "state_class": None,
        "unit": None,
        "value_key": "userNo",
    },
    "address": {
        "name": "地址",
        "icon": "mdi:map-marker",
        "device_class": None,
        "state_class": None,
        "unit": None,
        "value_key": "userAddress",
    },
    "meter_no": {
        "name": "表号",
        "icon": "mdi:numeric",
        "device_class": None,
        "state_class": None,
        "unit": None,
        "value_key": "bm",
    },
    "meter_type": {
        "name": "表类型",
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": None,
        "unit": None,
        "value_key": "blx",
    },
    "last_watch_date": {
        "name": "上次抄表日期",
        "icon": "mdi:calendar-check",
        "device_class": None,
        "state_class": None,
        "unit": None,
        "value_key": "lastRecordWatchDate",
    },
    # 新增传感器（从真实 API 测试中提取的全部可用字段）
    "current_balance": {
        "name": "当期余额",
        "icon": "mdi:cash-check",
        "device_class": "monetary",
        "state_class": None,
        "unit": "元",
        "value_key": "dqye",
    },
    "fee_flag": {
        "name": "欠费标志",
        "icon": "mdi:alert-circle",
        "device_class": None,
        "state_class": None,
        "unit": None,
        "value_key": "feeFlag",
    },
    "fee_money": {
        "name": "欠费金额",
        "icon": "mdi:cash-remove",
        "device_class": "monetary",
        "state_class": None,
        "unit": "元",
        "value_key": "feeMoney",
    },
    "safety_inspection_date": {
        "name": "安检日期",
        "icon": "mdi:shield-check",
        "device_class": "date",
        "state_class": None,
        "unit": None,
        "value_key": "safeInspectDate",
    },
    "start_fire_date": {
        "name": "点火日期",
        "icon": "mdi:fire",
        "device_class": "timestamp",
        "state_class": None,
        "unit": None,
        "value_key": "startFireDate",
    },
    "company_name": {
        "name": "燃气公司",
        "icon": "mdi:domain",
        "device_class": None,
        "state_class": None,
        "unit": None,
        "value_key": "bmmc",
    },
    "payment_account": {
        "name": "扣费账号",
        "icon": "mdi:bank",
        "device_class": None,
        "state_class": None,
        "unit": None,
        "value_key": "backAccount",
    },
    "insurance_fee": {
        "name": "保险金额",
        "icon": "mdi:shield-plus",
        "device_class": "monetary",
        "state_class": None,
        "unit": "元",
        "value_key": "bxje",
    },
    "insurance_expire": {
        "name": "保险截止日期",
        "icon": "mdi:calendar-clock",
        "device_class": "date",
        "state_class": None,
        "unit": None,
        "value_key": "bxjzrq",
    },
    "billing_cycle_start": {
        "name": "阶梯周期开始",
        "icon": "mdi:calendar-start",
        "device_class": None,
        "state_class": None,
        "unit": None,
        "value_key": "jietiTimeBenci",
    },
    "user_type": {
        "name": "用户类型",
        "icon": "mdi:account-group",
        "device_class": None,
        "state_class": None,
        "unit": None,
        "value_key": "userType",
    },
    "insurance_type": {
        "name": "保险缴费类型",
        "icon": "mdi:shield-sync",
        "device_class": None,
        "state_class": None,
        "unit": None,
        "value_key": "bxjglx",
    },
    "insurance_invalid": {
        "name": "保险失效日期",
        "icon": "mdi:calendar-remove",
        "device_class": "date",
        "state_class": None,
        "unit": None,
        "value_key": "bxsxrq",
    },
    "gas_address_status": {
        "name": "用气地址状态",
        "icon": "mdi:home-check",
        "device_class": None,
        "state_class": None,
        "unit": None,
        "value_key": "yqdzztdes",
    },
    "customer_id": {
        "name": "客户ID",
        "icon": "mdi:identifier",
        "device_class": None,
        "state_class": None,
        "unit": None,
        "value_key": "khId",
    },
    "current_usage_detail": {
        "name": "本期用气量",
        "icon": "mdi:fire-circle",
        "device_class": "gas",
        "state_class": "total_increasing",
        "unit": "m³",
        "value_key": "bzqyyql",
    },
    "meter_location": {
        "name": "表具安装位置",
        "icon": "mdi:map-marker-question",
        "device_class": None,
        "state_class": None,
        "unit": None,
        "value_key": "rqbAzwz",
    },
    "meter_location_id": {
        "name": "表具位置ID",
        "icon": "mdi:map-marker-outline",
        "device_class": None,
        "state_class": None,
        "unit": None,
        "value_key": "rqbWzId",
    },
    "meter_id_detail": {
        "name": "表具ID",
        "icon": "mdi:numeric-1-circle",
        "device_class": None,
        "state_class": None,
        "unit": None,
        "value_key": "rqbId",
    },
    "meter_serial": {
        "name": "表具编号",
        "icon": "mdi:barcode",
        "device_class": None,
        "state_class": None,
        "unit": None,
        "value_key": "rqbbgh",
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
