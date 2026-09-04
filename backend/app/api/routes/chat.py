from fastapi import APIRouter, HTTPException

from app.models.schemas import ChatRequest, ChatResponse
from app.services.chat_service import (
    ChatAPIError,
    ChatConfigError,
    ChatServiceError,
    chat_service,
)

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """AI 求职顾问聊天接口。"""
    try:
        answer = chat_service.get_advice(
            message=request.message,
            resume=request.resume,
            original_resume=request.original_resume,
            optimized_resume=request.optimized_resume,
            jd=request.jd,
            match_result=(
                request.match_result.model_dump()
                if request.match_result
                else None
            ),
            optimized_match_result=(
                request.optimized_match_result.model_dump()
                if request.optimized_match_result
                else None
            ),
            original_match_score=request.original_match_score,
            optimized_match_score=request.optimized_match_score,
            history=[item.model_dump() for item in request.history],
        )
        return ChatResponse(answer=answer)
    except ChatConfigError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except ChatAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except ChatServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {exc}") from exc
