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
