# MCP 伺服器設定參考

> 設定位置：`/Users/demi/.claude.json` → `projects["/Users/demi/Desktop/demi-agent"].mcpServers`

## 已安裝的 MCP 伺服器

| 名稱 | 類型 | 說明 |
|------|------|------|
| `notion` | stdio / npm | Notion 工作區讀寫 |
| `firecrawl` | stdio / npm | 網頁爬取與搜尋 |
| `filesystem` | stdio / npm | 本機檔案系統（Desktop / Documents / Downloads）|
| `playwright` | stdio / npm | 瀏覽器自動化 |
| `cloudflare` | stdio / remote | Cloudflare Workers 觀測 |

---

## Notion MCP

**正確設定方式**（`@notionhq/notion-mcp-server`，不是 HTTP 方式）：

```json
"notion": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@notionhq/notion-mcp-server"],
  "env": {
    "NOTION_API_KEY": "ntn_你的token（從 Notion 開發人員頁面複製）"
  }
}
```

**注意**：`mcp.notion.com/mcp`（HTTP 方式）需要 OAuth，**不接受** integration token。  
**一定要用 stdio + npm 套件** 才能搭配 `ntn_` 開頭的 integration token。

### Token 來源
- Notion → 開發人員 → 連接 → 淑瑜的生活日誌 → 存取權杖（格式：`ntn_xxxxxxxxxx`）
- Workspace：淑瑜的生活空間
- 實際 token 存在 `~/.claude.json` 的 `mcpServers.notion.env.NOTION_API_KEY`

---

## 踩坑記錄

- **2026-06-17**：HTTP 方式設 `mcp.notion.com/mcp` + Authorization header → 401，因為該端點只接受 OAuth。改用 stdio npm 套件後解決。
