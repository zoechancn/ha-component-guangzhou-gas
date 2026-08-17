# 广州燃气 Home Assistant 集成

通过广州燃气微信小程序使用的接口，将燃气表余额、用气量、表具状态、充值和安检信息接入 Home Assistant。

> 这是非官方集成，与广州燃气集团有限公司无关。认证参数属于敏感信息，请勿公开分享。

## 2.0 界面设计

设备主页默认只显示 8 个日常需要关注的实体：

- 燃气表余额
- 阶梯周期用气量
- 燃气表状态
- 上次抄表读数
- 最近充值金额
- 阶梯周期
- 安检状态
- 欠费金额

其余 28 个账户、保险和表具字段归入“诊断”分类，并在新安装中默认禁用。需要时可在设备的实体列表中单独启用。

从 1.x 升级不会更改旧实体的唯一 ID，因此历史数据和自动化可继续使用。此前已经启用的诊断实体不会被强制关闭。

## 安装

### HACS

1. 在 HACS 中添加本仓库为自定义集成仓库。
2. 搜索“广州燃气”并下载。
3. 重启 Home Assistant。
4. 前往“设置 → 设备与服务 → 添加集成”，搜索“广州燃气”。

### 手动安装

将 `custom_components/guangzhou_gas` 复制到 Home Assistant 的 `/config/custom_components/`，重启 Home Assistant 后添加集成。

## 配置

需要从广州燃气微信小程序的登录请求中取得：

- `nickName`
- `acceptKey`
- `unionid`

登录接口为：

```text
POST https://wxxcx.gzgas.com/ydeq/min/login/getToken.action
```

可通过 Charles 或 Fiddler 等网络调试工具查看该请求。请勿把请求内容、Home Assistant 配置条目或调试日志上传到公开位置。

默认更新间隔为 3 小时，最短允许 5 分钟。燃气数据变化频率较低，不建议设置得更短。

## 自动化示例

实体 ID 由 Home Assistant 根据名称生成，请在开发者工具中确认自己的实际实体 ID。

```yaml
automation:
  - alias: 燃气余额不足提醒
    triggers:
      - trigger: numeric_state
        entity_id: sensor.ran_qi_biao_yu_e
        below: 50
    actions:
      - action: notify.mobile_app_your_phone
        data:
          title: 燃气余额不足
          message: >-
            当前余额 {{ states('sensor.ran_qi_biao_yu_e') }} 元，请及时充值。
```

## 故障排查

- 实体不可用：先确认 Home Assistant 可以访问 `wxxcx.gzgas.com`，再尝试重新加载集成。
- 认证失败：在集成菜单中选择“重新配置”，填入最新认证参数。
- 查看日志：前往“设置 → 系统 → 日志”，搜索 `guangzhou_gas`。

集成不会在日志中输出认证参数、完整账户响应或地址信息。

## 开发

```bash
python -m pytest -q
ruff check .
ruff format --check .
```

许可证见 [LICENSE](LICENSE)。
