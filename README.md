# 广州燃气 Home Assistant 集成插件

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/custom-components/integration_blueprint)
[![GitHub Release](https://img.shields.io/github/release/zoechancn/ha-component-guangzhou-gas.svg?style=for-the-badge)](https://github.com/zoechancn/ha-component-guangzhou-gas/releases)
[![License](https://img.shields.io/github/license/zoechancn/ha-component-guangzhou-gas?style=for-the-badge)](LICENSE)

English | [简体中文](README.zh-Hans.md)

## 📖 目录

- [简介](#简介)
- [功能特性](#功能特性)
- [安装方法](#安装方法)
  - [方法一：通过 HACS 安装（推荐）](#方法一通过-hacs-安装推荐)
  - [方法二：手动安装](#方法二手动安装)
- [配置方法](#配置方法)
  - [获取认证参数](#获取认证参数)
  - [在 Home Assistant 中配置](#在-home-assistant-中配置)
- [传感器说明](#传感器说明)
- [自动化示例](#自动化示例)
- [常见问题（FAQ）](#常见问题faq)
- [调试与日志](#调试与日志)
- [贡献指南](#贡献指南)
- [许可证](#许可证)
- [致谢](#致谢)

## 简介

本集成插件用于接入广州燃气的官方 API，实现在 Home Assistant 中实时监控和展示燃气信息，包括燃气余额、用气量、充值记录、安检状态等。

**⚠️ 注意**: 本集成插件是非官方的，仅用于个人学习和研究目的。请合理使用，避免对广州燃气服务器造成过大压力。

## 功能特性

✅ **实时监控**: 自动获取燃气余额、用气量等信息  
✅ **10 个传感器**: 全面展示燃气信息  
✅ **HACS 支持**: 一键安装和更新  
✅ **多账户支持**: 支持配置多个燃气账户  
✅ **自动化友好**: 可基于传感器状态触发自动化  
✅ **安全可靠**: 认证信息安全存储，HTTPS 加密传输

## 安装方法

### 方法一：通过 HACS 安装（推荐）

1. 确保已安装 [HACS](https://hacs.xyz/)
2. 在 HACS 中搜索 "广州燃气" 或 "Guangzhou Gas"
3. 点击 "下载" 安装
4. 重启 Home Assistant
5. 配置集成（见下方[配置方法](#配置方法)）

### 方法二：手动安装

1. 下载本仓库的 [最新 Release](https://github.com/zoechancn/ha-component-guangzhou-gas/releases)
2. 解压文件
3. 将 `custom_components/guangzhou_gas` 目录复制到 Home Assistant 的 `custom_components` 目录
   - 完整路径应为：`/config/custom_components/guangzhou_gas/`
4. 重启 Home Assistant
5. 配置集成（见下方[配置方法](#配置方法)）

## 配置方法

### 获取认证参数

本集成插件需要 3 个认证参数：`nickName`、`acceptKey`、`unionid`。这些参数需要从广州燃气微信小程序中抓取。

#### 方法：使用抓包工具（如 Charles 或 Fiddler）

1. **安装抓包工具**:
   - Charles: https://www.charlesproxy.com/
   - Fiddler: https://www.telerik.com/fiddler

2. **配置手机代理**:
   - 将手机连接到与电脑相同的 Wi-Fi
   - 在手机 Wi-Fi 设置中配置代理，输入电脑的 IP 地址和抓包工具的端口（Charles 默认 8888）

3. **抓取认证参数**:
   - 打开广州燃气微信小程序
   - 登录并进入首页
   - 在抓包工具中查找以下 API 请求：
     - `POST https://wxxcx.gzgas.com/ydeq/min/login/getToken.action`
   - 查看该请求的 **Request Body**，包含：
     - `nickName`: 用户昵称
     - `acceptKey`: 密钥
     - `unionid`: 用户 ID

4. **记录认证参数**:
   - 将这 3 个参数记录下来，稍后在 Home Assistant 中配置时使用

**⚠️ 注意**: 认证参数是个人敏感信息，请妥善保管，不要泄露给他人。

### 在 Home Assistant 中配置

1. 进入 **设置** → **设备与服务** → **添加集成**
2. 搜索 "广州燃气" 或 "Guangzhou Gas"
3. 点击 "广州燃气"
4. 输入认证参数：
   - **Nick Name** (`nickName`): 用户昵称（从抓包获取）
   - **Accept Key** (`acceptKey`): 密钥（从抓包获取）
   - **Union ID** (`unionid`): 用户 ID（从抓包获取）
   - **更新间隔（秒）**: 默认 10800 秒（3 小时），可根据需要调整
5. 点击 "提交"
6. 如果配置正确，将显示 "配置成功"，并自动创建 10 个传感器实体

## 传感器说明

本集成插件会创建以下 10 个传感器实体：

| 传感器名称 | 实体 ID | 单位 | 图标 | 说明 |
|-----------|---------|------|------|------|
| 燃气余额 | `sensor.guangzhou_gas_balance` | 元 | 💰 | 当前燃气账户余额 |
| 阶梯周期用气量 | `sensor.guangzhou_gas_gas_usage` | m³ | 🔥 | 当前阶梯周期内的用气量 |
| 燃气表状态 | `sensor.guangzhou_gas_meter_status` | - | 🎯 | 燃气表的当前状态 |
| 上次抄表读数 | `sensor.guangzhou_gas_last_reading` | m³ | 📊 | 上次抄表时的读数 |
| 最近充值金额 | `sensor.guangzhou_gas_last_recharge` | 元 | ➕ | 最近一次充值的金额 |
| 累计充值金额 | `sensor.guangzhou_gas_total_recharge` | 元 | 💵 | 历史累计充值金额 |
| 阶梯周期 | `sensor.guangzhou_gas_billing_cycle` | - | 📅 | 当前阶梯周期的时间范围 |
| 自动扣费 | `sensor.guangzhou_gas_auto_payment` | - | 💳 | 自动扣费功能的状态 |
| 安检状态 | `sensor.guangzhou_gas_safety_inspection` | - | 🛡️ | 最近一次安检的状态 |
| 最近充值时间 | `sensor.guangzhou_gas_last_recharge_time` | - | 🕐 | 最近一次充值的时间 |

### 额外属性

每个传感器实体还包含以下额外属性（`extra_state_attributes`）：

- **用户名** (`userName`)
- **用户号** (`userNo`)
- **地址** (`userAddress`)
- **表号** (`bm`)
- **表类型** (`blx`)

## 自动化示例

### 示例 1：燃气余额低时发送通知

```yaml
automation:
  - alias: "燃气余额低提醒"
    trigger:
      - platform: numeric_state
        entity_id: sensor.guangzhou_gas_balance
        below: 50
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "燃气余额不足"
          message: "当前燃气余额为 {{ states('sensor.guangzhou_gas_balance') }} 元，请及时充值。"
    mode: single
```

### 示例 2：阶梯周期用气量接近上限时提醒

```yaml
automation:
  - alias: "阶梯用气量提醒"
    trigger:
      - platform: numeric_state
        entity_id: sensor.guangzhou_gas_gas_usage
        above: 300
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "阶梯用气量提醒"
          message: "当前阶梯周期用气量已达 {{ states('sensor.guangzhou_gas_gas_usage') }} m³，注意用气节税。"
    mode: single
```

## 常见问题（FAQ）

### Q1: 配置时提示 "认证失败，请检查认证信息" 怎么办？

**A**: 请检查以下几点：
1. `nickName`、`acceptKey`、`unionid` 是否正确（从抓包工具中获取）
2. 手机时间是否正确（错误的时间可能导致认证失败）
3. 网络是否正常（能否访问 `https://wxxcx.gzgas.com`）

如果问题仍然存在，请查看 Home Assistant 日志获取详细错误信息。

### Q2: 传感器显示 "不可用" 怎么办？

**A**: 可能的原因：
1. 网络故障：检查 Home Assistant 是否能访问外网
2. API 失败：广州燃气服务器可能暂时不可用，等待下次更新周期重试
3. 认证失败：认证参数可能已过期，请重新抓包获取最新的认证参数，然后在集成配置页面点击 "重新配置"

### Q3: 更新间隔可以设置为多短？

**A**: 理论上可以设置为任意值，但建议：
- **最短不要低于 300 秒（5 分钟）**，避免对广州燃气服务器造成过大压力
- **推荐设置为 10800 秒（3 小时）**，平衡实时性和服务器负载

### Q4: 支持配置多个燃气账户吗？

**A**: 支持。在集成配置页面，点击 "添加集成"，再次添加 "广州燃气"，输入另一个账户的认证参数即可。每个配置条目对应一个燃气账户。

### Q5: 如何查看 Home Assistant 日志？

**A**: 
1. 进入 **设置** → **系统** → **日志**
2. 在页面右上角搜索 "guangzhou_gas" 过滤相关日志

或者，如果你有 SSH 访问权限，可以直接查看日志文件：
```bash
tail -f /config/home-assistant.log | grep guangzhou_gas
```

## 调试与日志

如果需要调试，可以在 `configuration.yaml` 中增加日志级别：

```yaml
logger:
  logs:
    custom_components.guangzhou_gas: debug
```

重启 Home Assistant 后，可以在日志中看到详细的调试信息（API 请求、响应、错误处理等）。

**⚠️ 注意**: 调试模式下，日志可能包含敏感信息（如 API 请求和响应）。请不要在公共场合分享调试日志。

## 贡献指南

欢迎贡献代码、报告问题或改进文档！

### 报告问题

请在 [GitHub Issues](https://github.com/zoechancn/ha-component-guangzhou-gas/issues) 中报告问题，并包含以下信息：

- Home Assistant 版本
- 集成版本
- 错误日志
- 复现步骤

### 贡献代码

1. Fork 本仓库
2. 创建分支 (`git checkout -b feature/your-feature`)
3. 提交更改 (`git commit -m 'Add some feature'`)
4. 推送到分支 (`git push origin feature/your-feature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 致谢

- [Home Assistant](https://www.home-assistant.io/) - 开源智能家居平台
- [HACS](https://hacs.xyz/) - Home Assistant 社区商店
- [广州燃气](https://www.gzgas.com/) - 提供燃气服务（本集成插件为非官方，与广州燃气无关）

---

**⚠️ 免责声明**: 本集成插件为个人开源项目，与广州燃气集团有限公司无关。使用本插件所产生的任何后果，包括但不限于API调用失败、账号异常、法律责任等，由使用者自行承担，开发者不承担任何责任。请合理使用，遵守相关法律法规。
