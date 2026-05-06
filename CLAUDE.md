# demi-agent 工作環境

## MCP 伺服器

已安裝並連線（Local scope）：

| 名稱 | 指令 | 狀態 | API Key |
|------|------|------|---------|
| `playwright` | `npx -y @playwright/mcp` | ✅ Connected | 不需要 |
| `firecrawl` | `npx -y firecrawl-mcp` | ✅ Connected | 已設定於 env `FIRECRAWL_API_KEY` |
| `filesystem` | `npx -y @modelcontextprotocol/server-filesystem` | ✅ Connected | 不需要（存取 Desktop/Documents/Downloads）|

## 已安裝 Plugins（User scope）

| Plugin | 版本 | 功能 |
|--------|------|------|
| `skill-creator@claude-plugins-official` | — | 建立 / 優化自訂 Skill |
| `superpowers@claude-plugins-official` | v5.0.7 | Brainstorming 設計優先工作流 |
| `ui-ux-pro-max@ui-ux-pro-max-skill` | v2.5.0 | UI/UX 品牌設計系統生成 |

## 偏好設定

- 語言：繁體中文
- 預設模式：acceptEdits
- 模型：Claude Sonnet 4.6
