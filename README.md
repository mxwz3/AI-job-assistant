# AI 求职助手

上传简历 + 目标岗位 JD → AI 匹配分析 → 逐项优化建议（用户确认）→ 生成优化后简历 PDF。

## 技术栈

- 前端：Vue 3 + Vite
- 后端：FastAPI (Python)
- AI：Groq API（OpenAI 兼容协议）
- PDF：ReportLab（A4 中文字体排版）

## 本地启动

### 后端（端口 8001）

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env        # 填入 GROQ_API_KEY
uvicorn app.main:app --host 127.0.0.1 --port 8001
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

浏览器访问终端输出的地址（默认 http://localhost:5173）

## 环境变量（backend/.env）

| 变量 | 说明 |
|------|------|
| `GROQ_API_KEY` | Groq API 密钥（必需） |
| `LLM_BASE_URL` | 默认 `https://api.groq.com` |
| `LLM_MODEL` | 默认 `qwen/qwen3.8-27b` |
| `CORS_EXTRA_ORIGINS` | 生产环境追加的前端域名（逗号分隔，可选） |

## 部署（Render + Vercel）

1. **后端 → Render**（Web Service，根目录 `backend`）：
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - 环境变量：`GROQ_API_KEY`、`LLM_BASE_URL`、`LLM_MODEL`
2. **前端 → Vercel**（根目录 `frontend`，框架自动识别 Vite）：
   - Build: `npm run build`，Output: `dist`
   - 在 Vercel 项目设置中添加 Rewrite：`/api/(.*)` → `https://<你的Render域名>/api/$1`
   - 或在项目根目录放 `vercel.json`：
     ```json
     { "rewrites": [{ "source": "/api/(.*)", "destination": "https://<你的Render域名>/api/$1" }] }
     ```
3. 后端 Render 环境变量 `CORS_EXTRA_ORIGINS` 填前端 Vercel 域名。
