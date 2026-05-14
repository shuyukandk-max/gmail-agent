---
name: social-post
description: Write social media posts in the user's personal style. Use this skill whenever the user mentions writing a post, social content, IG文, 貼文, Threads, Facebook post, LinkedIn post, social media copy, or wants to share an idea on social platforms — even if they don't say "write a post" explicitly. If the user says things like "幫我寫一篇關於X" or "把這個想法變成貼文" or "這個可以發嗎", treat it as a social-post task. Outputs three platform-tuned versions at once: Threads/IG (short, conversational), Facebook (medium, story-wrapped), and LinkedIn (structured, professional).
---

# Social Post Generator

你的任務是把用戶給的主題或素材，轉化成三個平台版本的貼文。核心邏輯：**先學語氣，再寫內容**。

## 步驟

### Step 1：讀語氣範例（如果有的話）

先檢查 `200_Reference/writing-samples/social/` 這個資料夾是否有 `.md` 或 `.txt` 檔案。

- **如果有**：讀 2-3 篇，抓住以下特徵：
  - 開頭方式（問句 / 短句 / 數字開場）
  - 常用句式和停頓節奏
  - 結尾習慣（反問 / 呼籲行動 / 留白）
  - 避開的詞彙或風格
- **如果沒有**：跳過，用通用的知識型 KOL 語氣（清晰、有溫度、給洞見）

### Step 2：理解輸入

用戶給你的可能是：
- 一個主題句（「我想寫靈性療癒的力量」）
- 一段草稿（「這是我的想法...」）
- 一個問題（「AI 會取代創作者嗎？」）
- 一篇長文要改短（附上文章）

如果輸入模糊（少於 20 字且沒有具體角度），**問一個問題**：「這篇貼文你最想讓讀者帶走什麼感受或行動？」只問這一個，不要問多。

### Step 3：輸出三版本

根據主題和語氣，同時產出以下三個版本，**每個版本獨立成段**，格式如下：

---

**📱 Threads / IG 版**（目標 80–200 字）
- 風格：輕、快、有呼吸感，像和朋友說話
- 第一句要讓人停下來（懸念、反常識、問句、短到讓人想往下看）
- 可用 emoji，但不超過 3 個
- 結尾：留問句或空間，讓人有話說

---

**📘 Facebook 版**（目標 200–400 字）
- 風格：有故事感或數據包裝，帶出觀點
- 結構：一個開場鉤子 → 展開故事或數據 → 核心觀點 → 結尾收攏
- Emoji 可用可不用
- 結尾：可加「你有類似經驗嗎？」或行動呼籲

---

**💼 LinkedIn 版**（目標 200–350 字）
- 風格：專業但不冷硬，有個人觀點
- 結構：問題陳述或洞見開場 → 展開論點（1-2 個具體支撐）→ 給讀者的啟示或建議
- 不用 emoji 或少用
- 結尾：引導留言（「你在這方面的做法是什麼？」）

---

### Step 4：存檔（可選）

如果用戶說要存起來或未來想找回，把三個版本存進：
`100_Todo/drafts/social-posts/YYYY-MM-DD_主題簡述.md`

格式：
```
# [主題]（YYYY-MM-DD）

## Threads / IG 版
（內容）

## Facebook 版
（內容）

## LinkedIn 版
（內容）
```

## 迭代邏輯

用戶看完三版之後可能說：
- 「Threads 版太長了」→ 縮到 80 字以內，只留最強的一句
- 「Facebook 版改更有故事感」→ 加一個具體情境或案例
- 「LinkedIn 版不夠有力」→ 開場換成更有爭議性的切入點
- 「語氣不像我」→ 問「哪裡不像？我來調整」，或問他提供一篇最像他自己的貼文讓你學

每次修改只改指定版本，其他版本不動。

## 注意事項

- 不要主動寫 hashtag，除非用戶要求
- 三個版本都要有自己的核心論點，不是同一段話換長短
- 如果主題涉及靈性、能量、水晶等，維持知識型語氣，不要過度感性或過度「商業化」
- 字數只是參考，內容完整比字數精確更重要
