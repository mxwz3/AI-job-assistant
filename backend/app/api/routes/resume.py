import logging
import traceback
from urllib.parse import quote

from fastapi import APIRouter, File, HTTPException, Response, UploadFile

from app.models.schemas import ResumeInfo, ResumeUploadResponse
from app.services.groq_service import (
    GroqAPIError,
    GroqConfigError,
    GroqParseError,
    groq_service,
)
from app.services.pdf_service import generate_resume_pdf
from app.services.resume_service import ResumeParseError, parse_pdf_resume

router = APIRouter(prefix="/api", tags=["resume"])

logger = logging.getLogger(__name__)


@router.post("/upload_resume", response_model=ResumeUploadResponse)
async def upload_resume(file: UploadFile = File(...)) -> ResumeUploadResponse:
    """接收用户上传的 PDF 简历，解析并返回结构化信息。"""
    try:
        resume_text = await parse_pdf_resume(file)
        resume_info = groq_service.extract_resume_info(resume_text)
        return ResumeUploadResponse(
            success=True,
            resume_text=resume_text,
            resume_info=resume_info,
        )
    except ResumeParseError as exc:
        return ResumeUploadResponse(success=False, error=str(exc))
    except GroqConfigError as exc:
        return ResumeUploadResponse(success=False, error=str(exc))
    except (GroqAPIError, GroqParseError) as exc:
        return ResumeUploadResponse(
            success=False,
            error=f"简历信息提取失败: {exc}",
        )
    except Exception as exc:
        return ResumeUploadResponse(success=False, error=f"服务器内部错误: {exc}")


@router.post("/resume/pdf")
async def generate_resume_pdf_endpoint(resume_info: ResumeInfo) -> Response:
    """根据优化后的结构化简历数据生成 PDF 简历（不调用 AI）。"""
    try:
        pdf_bytes = generate_resume_pdf(resume_info)
        # HTTP header 只支持 latin-1，中文文件名必须按 RFC 5987 编码，
        # 同时提供 ASCII fallback，避免 'latin-1' codec 编码错误。
        filename = f"{resume_info.name or '简历'}_优化后简历.pdf"
        content_disposition = (
            f"attachment; filename=\"resume.pdf\"; "
            f"filename*=UTF-8''{quote(filename)}"
        )
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": content_disposition},
        )
    except Exception as exc:
        logger.error("PDF 生成失败:\n%s", traceback.format_exc())
        raise HTTPException(
            status_code=500, detail="PDF 生成失败，请稍后重试"
        ) from exc
