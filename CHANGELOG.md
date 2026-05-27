# Changelog

本文档记录广州燃气 Home Assistant 集成插件的所有版本更新。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [Unreleased]

### Added
- （待添加的功能）

### Changed
- （待变更的改进）

### Fixed
- （待修复的问题）

---

## [1.1.8] - 2026-05-27

### Added
- 🎉 **新增 20 个传感器（共 36 个）**
  - ✅ 根据真实 API 测试，添加全部可用字段
  - ✅ 优先使用用户信息 API（59 个字段）
  - ✅ 补充使用燃气详情 API（10 个独有字段）
  - ✅ 自动选择更准确的数据源（如 `rqbAzwz` 从燃气详情 API 获取）
  
- **新增传感器列表**：
  1. 当期余额（`dqye`）
  2. 欠费标志（`feeFlag`）
  3. 欠费金额（`feeMoney`）
  4. 安检日期（`safeInspectDate`）
  5. 点火日期（`startFireDate`）
  6. 燃气公司（`bmmc`）
  7. 扣费账号（`backAccount`）
  8. 保险金额（`bxje`）
  9. 保险截止日期（`bxjzrq`）
  10. 阶梯周期开始（`jietiTimeBenci`）
  11. 用户类型（`userType`）
  12. 保险缴费类型（`bxjglx`）
  13. 保险失效日期（`bxsxrq`）
  14. 用气地址状态（`yqdzztDes`）
  15. 客户ID（`khId`）
  16. 本期用气量（`bzqyyql` - 从燃气详情 API）
  17. 表具安装位置（`rqbAzwz` - 从燃气详情 API，更准确）
  18. 表具位置ID（`rqbWzId`）
  19. 表具ID（`rqbId`）
  20. 表具编号（`rqbbgh`）

### Changed
- 📊 **数据源优化**
  - 主要使用用户信息 API（59 字段）
  - 补充使用燃气详情 API（10 字段）
  - 重复字段自动选择更准确的数据源

---

## [1.1.7] - 2026-05-27

### Fixed
- 🐛 **修复 `entity.py` 第67行和第81行 `DOMAIN` 未定义错误**
  - ❌ v1.1.6 在加载传感器时崩溃
  - ✅ 添加 `from .const import DOMAIN` 导入
  - ✅ 修复 `unique_id` 属性（第67行）
  - ✅ 修复 `_get_device_info()` 方法（第81行）
  - ✅ 错误信息：`name 'DOMAIN' is not defined`

---

## [1.1.6] - 2026-05-27

### Fixed
- 🐛 **修复 `entity.py` 第9行 DeviceInfo 导入错误**
  - ❌ v1.1.5 在 Home Assistant 2024.x+ 中导入失败
  - ✅ 使用 try/except 兼容新旧版本：
    - 新版本：`from homeassistant.helpers.device_registry import DeviceInfo`
    - 旧版本：`from homeassistant.helpers.typing import DeviceInfo`
  - ✅ 错误信息：`No module named 'homeassistant.helpers.typing'.DeviceInfo`
  - ✅ 代码审查通过：所有文件语法检查通过
  - ✅ 版本号一致性检查通过

---

## [1.1.5] - 2026-05-27

### Fixed
- 🐛 **修复 Home Assistant 新版本 API 兼容性**
  - ❌ v1.1.4 使用已弃用的 `async_forward_entry_setup()` 方法
  - ✅ 新版本 Home Assistant (2024.x+) 使用 `async_forward_entry_setups()` (带 's')
  - ✅ 修复 `__init__.py`: 平台加载使用新 API `async_forward_entry_setups(entry, ["sensor"])`
  - ✅ 修复 `__init__.py`: 平台卸载使用新 API `async_unload_platforms(entry, ["sensor"])`
  - ✅ 错误信息：`'ConfigEntries' object has no attribute 'async_forward_entry_setup'`

---

## [1.1.4] - 2026-05-27

### Fixed
- 🐛 **修复用户信息解析（根据真实 API 测试）**
  - ❌ 之前版本（v1.1.3）假设 `wtVo` 是数组（list）
  - ✅ 真实 API 返回 `wtVo` 是对象（dict）
  - ✅ 修复 `api.py`: `async_get_user_info()` 现在兼容处理 dict 和 list 两种情况
  - ✅ 修复 `api.py`: `async_get_gas_detail()` 现在兼容处理 dict 和 list 两种情况（提高健壮性）
  - ✅ 更新测试夹具（fixtures）以匹配真实 API 响应格式
  - ✅ 更新 `config_flow.py` 注释，更准确描述代码行为
  - ✅ 使用用户提供的认证信息直接测试真实 API，确保代码正确性

---

## [1.1.3] - 2026-05-27

### Fixed
- 🐛 **完全修复数据解析逻辑**（根据 Node-RED 流程分析）
  - ✅ 修复 `api.py`: `async_get_user_info()` 现在返回 `wtVo[0]`（不是完整的 API 响应）
  - ✅ 修复 `api.py`: `async_get_gas_detail()` 现在返回 `rqbList[0]`（不是完整的 API 响应）
  - ✅ 修复 `config_flow.py`: 正确从 `wtVo[0]["userName"]` 提取用户名
  - ✅ 修复 `coordinator.py`: 正确调用 API 并合并数据（扁平结构）
  - ✅ 修复 `coordinator.py`: 从 `user_info` 中提取 `userNo`，用于查询燃气详情
- ✅ `sensor.py` 无需修改（已在使用正确的中文键名）

---

## [1.1.2] - 2026-05-27

### Fixed
- 🐛 **完全重构 API 请求逻辑**（根据 Node-RED 流程分析）
  - ✅ 修复登录请求格式：`unionid` 放在 **header** 里（不是 body）
  - ✅ `nickName` 和 `acceptKey` 使用 **表单格式** (`x-www-form-urlencoded`)
  - ✅ 添加 `xweb_xhr: 1` header（微信小程序必需）
- 🐛 **修复 Token 解析**
  - ✅ 从 `response["data"]` 获取 token（**字符串**，不是对象）
  - Node-RED 流程：`let token = res.data;` （data 直接是 token）
- 🐛 **修复后续请求认证方式**
  - ✅ 使用 `accessToken` header（不是 `Authorization: Bearer`）
  - ✅ 每个请求都带 `unionid` 和 `xweb_xhr: 1`
- 🐛 **更新请求头**
  - ✅ `User-Agent` 完全匹配 Node-RED 配置
  - ✅ `Referer` 完全匹配 Node-RED 配置
  - ✅ `Content-Type: application/x-www-form-urlencoded`

### Changed
- 🔧 简化登录逻辑，直接使用表单格式（不再尝试 JSON）

---

## [1.1.1] - 2026-05-27

### Fixed
- ✅ 修复了配置时无法连接服务器的问题
- ✅ 添加详细的请求/响应日志，便于调试
- ✅ 忽略 Content-Type 检查，兼容 `text/html` 响应
- ✅ 支持表单格式 (`x-www-form-urlencoded`) 和 JSON 格式
- ✅ 更新请求头，模拟微信小程序真实请求
- ✅ 登录时自动尝试两种格式（JSON 优先，失败后尝试表单）
- ✅ 指数退避重试机制（1秒、2秒、4秒）

---

## [1.1.0] - 2026-05-26

### Added
- ✨ 新增 6 个传感器实体：
  - 用户名 (`sensor.guangzhou_gas_user_name`)
  - 用户号 (`sensor.guangzhou_gas_user_no`)
  - 地址 (`sensor.guangzhou_gas_address`)
  - 表号 (`sensor.guangzhou_gas_meter_no`)
  - 表类型 (`sensor.guangzhou_gas_meter_type`)
  - 上次抄表日期 (`sensor.guangzhou_gas_last_watch_date`)
- ✨ 现在共支持 16 个传感器实体

### Changed
- （无）

### Fixed
- （无）

---

## [1.0.0] - 2026-05-26

### Added
- ✨ 初始版本发布
- ✨ 支持 10 个传感器实体：
  - 燃气余额 (`sensor.guangzhou_gas_balance`)
  - 阶梯周期用气量 (`sensor.guangzhou_gas_gas_usage`)
  - 燃气表状态 (`sensor.guangzhou_gas_meter_status`)
  - 上次抄表读数 (`sensor.guangzhou_gas_last_reading`)
  - 最近充值金额 (`sensor.guangzhou_gas_last_recharge`)
  - 累计充值金额 (`sensor.guangzhou_gas_total_recharge`)
  - 阶梯周期 (`sensor.guangzhou_gas_billing_cycle`)
  - 自动扣费 (`sensor.guangzhou_gas_auto_payment`)
  - 安检状态 (`sensor.guangzhou_gas_safety_inspection`)
  - 最近充值时间 (`sensor.guangzhou_gas_last_recharge_time`)
- ✨ HACS 支持，一键安装
- ✨ 多账户支持
- ✨ 配置流（Config Flow）支持，无需手动编辑配置文件
- ✨ 完整的中英文翻译
- ✨ 自动化示例（余额低提醒、阶梯用气量提醒）
- ✨ 完整的调试日志支持

### Changed
- （无）

### Fixed
- （无）

### Security
- （无）

---

## 版本说明

### 版本号格式：主版本.次版本.修订号 (MAJOR.MINOR.PATCH)

- **主版本 (MAJOR)**: 不兼容的 API 修改
- **次版本 (MINOR)**: 向后兼容的功能性新增
- **修订号 (PATCH)**: 向后兼容的问题修正

### 分类说明

- **Added**: 新功能
- **Changed**: 对现有功能的变更
- **Deprecated**: 即将移除的功能
- **Removed**: 已移除的功能
- **Fixed**: 错误修复
- **Security**: 安全问题修复

---

**发布日期格式**: YYYY-MM-DD
