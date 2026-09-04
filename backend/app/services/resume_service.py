from io import BytesIO

from fastapi import UploadFile
from pypdf import PdfReader


class ResumeParseError(Exception):
    """简历解析异常。"""


async def parse_pdf_resume(file: UploadFile) -> str:
    """解析 PDF 简历文件，返回完整文本内容。"""
    if file.content_type != "application/pdf":
        raise ResumeParseError("仅支持上传 PDF 格式的简历")

    try:
        content = await file.read()
        if not content:
            raise ResumeParseError("上传的文件为空")

        pdf_file = BytesIO(content)
        reader = PdfReader(pdf_file)

        if not reader.pages:
            raise ResumeParseError("PDF 文件没有可解析的页面")

        text_parts: list[str] = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

        resume_text = "\n".join(text_parts).strip()
        if not resume_text:
            raise ResumeParseError("无法从 PDF 中提取到文本，可能是扫描件或图片 PDF")

        return resume_text

    except ResumeParseError:
        raise
    except Exception as exc:
        raise ResumeParseError(f"PDF 解析失败: {exc}") from exc
    finally:
        await file.close()
