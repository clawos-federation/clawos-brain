# trustedProxies 条件配置模板（仅在反向代理场景启用）

## 何时需要配置
仅当你把 OpenClaw Control UI / Gateway 放在反向代理后面（Nginx/Caddy/Traefik/Cloudflare Tunnel）时需要配置。

如果保持本机 loopback（127.0.0.1）且不经反向代理，可保持为空。

## 示例（说明性）
在 `~/.openclaw/openclaw.json` 中：

```json
{
  "gateway": {
    "trustedProxies": [
      "127.0.0.1",
      "::1",
      "192.168.1.10"
    ]
  }
}
```

## 建议
1. 只写你自己的代理出口 IP，不要写过宽网段。
2. 上线前执行：`openclaw security audit --deep`
3. 修改后观察 24 小时日志再扩大暴露面。
