"""Constants for the Guangzhou Gas integration."""

DOMAIN = "guangzhou_gas"

CONF_NICKNAME = "nickname"
CONF_ACCEPT_KEY = "accept_key"
CONF_UNIONID = "unionid"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_SCAN_INTERVAL = 10_800
MIN_SCAN_INTERVAL = 300

API_BASE_URL = "https://wxxcx.gzgas.com/ydeq/min"
API_LOGIN_URL = f"{API_BASE_URL}/login/getToken.action"
API_USER_INFO_URL = f"{API_BASE_URL}/bind/getUserByShowIndex.action"
API_GAS_DETAIL_URL = f"{API_BASE_URL}/order/getBiaoDetail.action"

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 "
        "Safari/537.36 MicroMessenger/7.0.20.1781 MiniProgramEnv/Windows"
    ),
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": "https://servicewechat.com/wx6a4fd0ebb4a12c11/366/page-frame.html",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "xweb_xhr": "1",
}
