from fastapi import APIRouter, HTTPException

from app.models.schemas import MatchRequest, MatchResult
from app.services.groq_service import (
    GroqAPIError,
    GroqConfigError,
    GroqParseError,
    GroqServiceError,
    groq_service,
)

router = APIRouter(prefix="/api", tags=["match"])


@router.post("/match", response_model=MatchResult)
async def match_resume_jd(request: MatchRequest) -> MatchResult:
    """根据简历和 JD 进行岗位匹配分析，返回结构化结果。"""
    try:
        return await groq_service.match_resume_jd(
            resume_text=request.resume,
            jd_text=request.jd,
        )
    except GroqConfigError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except (GroqAPIError, GroqParseError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except GroqServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {exc}") from exc
