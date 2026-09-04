import os

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.analyze import router as analyze_router
from app.api.routes.chat import router as chat_router
from app.api.routes.match import router as match_router
from app.api.routes.resume import router as resume_router

app = FastAPI(
    title="AI 求职助手 API",
    description="简历解析、JD 分析、岗位匹配、AI 助手服务",
    version="1.0.0",
)

# 本地开发默认源；生产环境通过 CORS_EXTRA_ORIGINS 追加（逗号分隔）
_default_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]
_extra = os.getenv("CORS_EXTRA_ORIGINS", "").strip()
_allow_origins = _default_origins + [
    o.strip() for o in _extra.split(",") if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router)
app.include_router(resume_router)
app.include_router(match_router)
app.include_router(chat_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
