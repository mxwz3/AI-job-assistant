import logging
import re
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.models.schemas import ResumeInfo

logger = logging.getLogger(__name__)

# STSong-Light 是 ReportLab 内置的简体中文 CID 字体，无需字体文件，
# 完整支持中文、中文标点、英文、数字混排。
FONT_NAME = "STSong-Light"

MARGIN_LR = 17 * mm
MARGIN_TB = 16 * mm

# 极简商务配色：近黑正文、灰色辅助信息，单一低饱和度深蓝仅用于模块标题
COLOR_TEXT = HexColor("#1a1a1a")
COLOR_SUB = HexColor("#555555")
COLOR_ACCENT = HexColor("#334e68")
COLOR_HAIRLINE = HexColor("#d9d9d9")

_DATE_COL_WIDTH = 40 * mm
_TITLE_COL_WIDTH = A4[0] - MARGIN_LR * 2 - _DATE_COL_WIDTH

_NAME_STYLE = ParagraphStyle(
    "ResumeName",
    fontName=FONT_NAME,
    fontSize=22,
    leading=26,
    alignment=0,  # 左对齐
    textColor=COLOR_TEXT,
    spaceAfter=1 * mm,
)

_OBJECTIVE_STYLE = ParagraphStyle(
    "ResumeObjective",
    fontName=FONT_NAME,
    fontSize=11.5,
    leading=16,
    textColor=COLOR_SUB,
    spaceAfter=1 * mm,
    wordWrap="CJK",
)

_CONTACT_STYLE = ParagraphStyle(
    "ResumeContact",
    fontName=FONT_NAME,
    fontSize=9.5,
    leading=14,
    textColor=COLOR_SUB,
    wordWrap="CJK",
)

_SECTION_STYLE = ParagraphStyle(
    "SectionTitle",
    fontName=FONT_NAME,
    fontSize=12,
    leading=16,
    textColor=COLOR_ACCENT,
    spaceBefore=4.5 * mm,
    spaceAfter=1 * mm,
    keepWithNext=1,  # 标题不单独留在页底
    wordWrap="CJK",
)

_ENTRY_TITLE_STYLE = ParagraphStyle(
    "EntryTitle",
    fontName=FONT_NAME,
    fontSize=10.5,
    leading=15,
    textColor=COLOR_TEXT,
    wordWrap="CJK",
)

_DATE_STYLE = ParagraphStyle(
    "EntryDate",
    fontName=FONT_NAME,
    fontSize=9.5,
    leading=15,
    alignment=2,  # 右对齐
    textColor=COLOR_SUB,
)

_TECH_STYLE = ParagraphStyle(
    "TechStack",
    fontName=FONT_NAME,
    fontSize=9.5,
    leading=14,
    textColor=COLOR_SUB,
    spaceBefore=0.5 * mm,
    spaceAfter=0.5 * mm,
    wordWrap="CJK",
)

_BODY_STYLE = ParagraphStyle(
    "Body",
    fontName=FONT_NAME,
    fontSize=10,
    leading=15.5,
    textColor=COLOR_TEXT,
    spaceAfter=1 * mm,
    wordWrap="CJK",  # 中文/英文/长字符串都允许在任意字符处换行
)

_BULLET_STYLE = ParagraphStyle(
    "Bullet",
    parent=_BODY_STYLE,
    leftIndent=10,
    firstLineIndent=-10,
    spaceAfter=0.8 * mm,
)

_ENTRY_TABLE_STYLE = TableStyle(
    [
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]
)

# 日期或日期区间：2023.09 / 2023年9月 / 2023.09-2027.06 / 2023.09–至今 等
_DATE_RANGE_RE = re.compile(
    r"20\d{2}[./年]\s?\d{1,2}月?"
    r"(?:\s*[-–—~～至到]+\s*(?:20\d{2}[./年]\s?\d{1,2}月?|至今|今|现在))?"
)
# 描述开头的技术栈标签，如 "技术栈：Vue / Spring Boot。"
_TECH_LABEL_RE = re.compile(r"^(?:技术栈|使用技术|主要技术|开发技术|技术选型)\s*[:：]\s*")
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[。；;！？!?])\s*|\n+")
_TECH_SEP_RE = re.compile(r"[/、,，;；|]+")


def _register_fonts() -> None:
    if FONT_NAME not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(UnicodeCIDFont(FONT_NAME))


def _p(text: str, style: ParagraphStyle) -> Paragraph:
    """构建段落，转义 XML 特殊字符，换行转换为 <br/>。"""
    safe = escape(text or "").replace("\n", "<br/>")
    return Paragraph(safe, style)


def _extract_date(text: str) -> tuple[str, str]:
    """从文本中提取第一个日期/日期区间，返回 (剩余文本, 日期)。"""
    match = _DATE_RANGE_RE.search(text or "")
    if not match:
        return (text or "").strip(), ""
    date = match.group(0).strip()
    rest = (text[: match.start()] + text[match.end():]).strip(" ，,｜|·")
    return rest, date


def _split_sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_SPLIT_RE.split(text or "") if s and s.strip()]


def _parse_entry(raw: str):
    """将 "名称：描述" 形式的条目解析为 (标题, 日期, 技术栈, 描述句子列表)。

    仅做展示层拆分，不修改任何数据；无法识别标题时整段按描述处理。
    """
    text = (raw or "").strip()
    if not text:
        return None

    header = ""
    body = text
    for sep in ("：", ":"):
        left, found, right = text.partition(sep)
        if found and left.strip():
            header, body = left.strip(), right.strip()
            break

    header, date = _extract_date(header)

    tech = ""
    match = _TECH_LABEL_RE.match(body)
    if match:
        rest = body[match.end():]
        seg, found, remaining = rest.partition("。")
        if not found:
            seg, found, remaining = rest.partition("\n")
        tech = " · ".join(p.strip() for p in _TECH_SEP_RE.split(seg) if p.strip())
        body = remaining.strip() if found else ""

    return header, date, tech, _split_sentences(body)


def _title_date_row(title: str, date: str) -> Table:
    """左侧标题 + 右侧日期的同行布局（无边框表格，仅作排版用途）。"""
    table = Table(
        [[Paragraph(escape(title), _ENTRY_TITLE_STYLE), Paragraph(escape(date), _DATE_STYLE)]],
        colWidths=[_TITLE_COL_WIDTH, _DATE_COL_WIDTH],
    )
    table.setStyle(_ENTRY_TABLE_STYLE)
    return table


def _entry_block(raw: str) -> list:
    """项目/实习条目：名称与日期同行，技术栈紧随其后，描述为 bullet list。

    返回 flowable 列表（不在此处包 KeepTogether，避免嵌套 KeepTogether
    导致 Platypus 分页误判）。
    """
    parsed = _parse_entry(raw)
    if not parsed:
        return []
    header, date, tech, sentences = parsed

    flow: list = []
    if header:
        flow.append(_title_date_row(header, date))
    if tech:
        flow.append(_p(tech, _TECH_STYLE))
    for sentence in sentences:
        flow.append(_p(f"• {sentence}", _BULLET_STYLE))
    if not flow:
        return []

    flow.append(Spacer(1, 1.6 * mm))
    return flow


def _education_block(raw: str) -> list:
    """教育经历：学校｜专业｜学历 紧凑一行，日期右对齐。"""
    text = (raw or "").strip()
    if not text:
        return []
    rest, date = _extract_date(text)
    parts = [p for p in re.split(r"[\s｜|]+", rest) if p]
    title = " ｜ ".join(parts) if parts else rest
    return [_title_date_row(title, date), Spacer(1, 1.6 * mm)]


def _bullets_block(items: list[str]) -> list:
    """证书/其他等简单条目的紧凑 bullet 列表。"""
    return [
        _p(f"• {item.strip()}", _BULLET_STYLE)
        for item in items
        if item and item.strip()
    ]


def _section(story: list, title: str, blocks: list) -> None:
    """输出一个模块：标题 + 细分隔线 + 内容块。

    标题与首个内容块包在同一个 KeepTogether 中（标题不孤行在页底），
    其余每个条目各自 KeepTogether（一个项目/实习尽量不被分页拆散）。
    """
    blocks = [b for b in blocks if b]
    if not blocks:
        return
    head = [
        Paragraph(escape(title), _SECTION_STYLE),
        HRFlowable(
            width="100%",
            thickness=0.5,
            color=COLOR_HAIRLINE,
            spaceBefore=0,
            spaceAfter=1.5 * mm,
        ),
    ]
    story.append(KeepTogether(head + blocks[0]))
    for block in blocks[1:]:
        story.append(KeepTogether(block))


def generate_resume_pdf(resume_info: ResumeInfo) -> bytes:
    """根据优化后的结构化简历数据生成 PDF 字节流，不调用任何 AI。

    只读取 optimizedResume 数据，空模块自动隐藏，
    内容超过一页时由 Platypus 自然分页，条目级 KeepTogether 避免拆散。
    """
    _register_fonts()

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=MARGIN_LR,
        rightMargin=MARGIN_LR,
        topMargin=MARGIN_TB,
        bottomMargin=MARGIN_TB,
        title=f"{resume_info.name or '简历'}_优化后简历",
        author="AI 求职助手",
    )

    story: list = []

    # 个人信息区域：姓名左对齐，求职意向紧随姓名，联系方式单独一行
    header_flow: list = []
    if resume_info.name:
        header_flow.append(_p(resume_info.name, _NAME_STYLE))
    if resume_info.objective:
        header_flow.append(_p(resume_info.objective, _OBJECTIVE_STYLE))
    if resume_info.contact:
        header_flow.append(_p(resume_info.contact, _CONTACT_STYLE))
    if header_flow:
        story.append(KeepTogether(header_flow))
        story.append(Spacer(1, 1 * mm))

    # 教育经历：优先使用 education 列表，否则回退 school + major
    education_items = [e for e in (resume_info.education or []) if e.strip()]
    if not education_items:
        fallback = " ".join(
            part for part in [resume_info.school, resume_info.major] if part
        ).strip()
        if fallback:
            education_items = [fallback]
    _section(story, "教育经历", [_education_block(e) for e in education_items])

    # 实习/实践经历
    _section(story, "实习/实践经历", [_entry_block(t) for t in (resume_info.internships or [])])

    # 项目经历
    _section(story, "项目经历", [_entry_block(p) for p in (resume_info.projects or [])])

    # 专业技能：紧凑单行，顿号分隔，不使用评分/星级/进度条
    skills = [s.strip() for s in (resume_info.skills or []) if s and s.strip()]
    if skills:
        _section(story, "专业技能", [[_p("、".join(skills), _BODY_STYLE)]])

    # 校园经历
    _section(story, "校园经历", [_entry_block(c) for c in (resume_info.campusExperience or [])])

    # 证书与奖项：紧凑 bullet
    _section(story, "证书与奖项", [_bullets_block(resume_info.certificates or [])])

    # 自我评价：普通段落
    if resume_info.selfEvaluation and resume_info.selfEvaluation.strip():
        _section(story, "自我评价", [[_p(resume_info.selfEvaluation.strip(), _BODY_STYLE)]])

    # 其他信息
    _section(story, "其他信息", [_bullets_block(resume_info.other or [])])

    if not story:
        story.append(_p("暂无简历内容", _BODY_STYLE))

    doc.build(story)
    return buffer.getvalue()
