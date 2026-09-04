from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from app.models.schemas import AnalyzeRequest, JdAnalysisResult
from app.services.groq_service import (
    GroqAPIError,
    GroqConfigError,
    GroqParseError,
    groq_service,
)

router = APIRouter(prefix="/api", tags=["analyze"])


@router.post("/analyze", response_model=JdAnalysisResult)
async def analyze_jd(request: AnalyzeRequest) -> JdAnalysisResult:
    try:
        return await groq_service.analyze_jd(request.jd_text)
    except GroqConfigError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except (GroqAPIError, GroqParseError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(status_code=502, detail=f"数据校验失败: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {exc}") from exc
