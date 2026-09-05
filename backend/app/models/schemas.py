from pydantic import BaseModel, Field, field_validator


def _flatten_education_entry(item) -> str:
    """LLM 偶尔会把 education 条目返回为 {school, major, date...} 对象，
    按"时间 学校 专业 学历"顺序拼成一段文字，保持 list[str] 契约。"""
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        parts = [
            item.get("date") or item.get("time") or item.get("period") or "",
            item.get("school") or item.get("university") or "",
            item.get("major") or "",
            item.get("degree") or item.get("education") or item.get("学历") or "",
        ]
        return " ".join(p for p in parts if str(p).strip())
    return str(item) if item is not None else ""


class AnalyzeRequest(BaseModel):
    jd_text: str = Field(..., min_length=10, description="招聘 JD 原文")


class JdAnalysisResult(BaseModel):
    job_title: str = Field(description="岗位名称")
    responsibilities: list[str] = Field(default_factory=list, description="岗位职责")
    ai_skills: list[str] = Field(default_factory=list, description="AI 相关技能")
    product_skills: list[str] = Field(default_factory=list, description="产品相关技能")
    soft_skills: list[str] = Field(default_factory=list, description="软技能")
    requirements: list[str] = Field(default_factory=list, description="硬性要求（学历、经验等）")


class ResumeInfo(BaseModel):
    name: str = Field(default="", description="姓名")
    contact: str = Field(default="", description="联系方式（电话/邮箱等）")
    objective: str = Field(default="", description="求职意向")
    school: str = Field(default="", description="学校")
    major: str = Field(default="", description="专业")
    education: list[str] = Field(default_factory=list, description="教育经历列表")
    skills: list[str] = Field(default_factory=list, description="技能列表")
    projects: list[str] = Field(default_factory=list, description="项目经验列表")
    internships: list[str] = Field(default_factory=list, description="实习/实践经历列表")
    campusExperience: list[str] = Field(default_factory=list, description="校园经历列表")
    certificates: list[str] = Field(default_factory=list, description="证书/奖项列表")
    selfEvaluation: str = Field(default="", description="自我评价")
    other: list[str] = Field(default_factory=list, description="其他信息")

    @field_validator("education", mode="before")
    @classmethod
    def _coerce_education_to_strings(cls, value):
        """兼容 LLM 返回结构化教育经历对象的情况，统一转为字符串列表。"""
        if not isinstance(value, list):
            return value
        return [_flatten_education_entry(item) for item in value]


class ResumeUploadResponse(BaseModel):
    success: bool = Field(description="是否解析成功")
    resume_text: str = Field(default="", description="解析出的简历原始文本，失败时为空")
    resume_info: ResumeInfo = Field(default_factory=ResumeInfo, description="结构化简历信息")
    error: str = Field(default="", description="错误信息，成功时为空")


class MatchRequest(BaseModel):
    resume: str = Field(..., min_length=1, description="简历文本")
    jd: str = Field(..., min_length=1, description="岗位 JD 文本")


class ResumeProblem(BaseModel):
    problem: str = Field(description="简历存在的问题")
    suggestion: str = Field(description="修改建议")


class OptimizationSuggestion(BaseModel):
    id: str = Field(default="", description="建议唯一标识")
    type: str = Field(default="modify", description="建议类型：add 新增 / modify 修改 / delete 删除 / enhance 强化 / keep 保留")
    field: str = Field(default="projects", description="所属简历模块，如 projects/skills/education/internships/campusExperience/certificates/selfEvaluation/basicInfo")
    itemIndex: int | None = Field(default=None, description="对应模块内的条目索引（从 0 开始），新增建议为 null")
    problem: str = Field(default="", description="对应问题")
    reason: str = Field(default="", description="为什么要这样修改")
    before: str = Field(default="", description="修改前表述（简历原文）")
    after: str = Field(default="", description="修改后表述（AI 建议内容）")


class SkillMatchDetail(BaseModel):
    skill: str = Field(description="技能名称")
    reason: str = Field(default="", description="匹配状态说明")


class MatchResult(BaseModel):
    matchScore: int = Field(ge=0, le=100, description="匹配度分数 0-100")
    position: str = Field(description="岗位名称")
    skillMatch: int = Field(default=0, ge=0, le=100, description="技能匹配度 0-100")
    projectMatch: int = Field(default=0, ge=0, le=100, description="项目匹配度 0-100")
    experienceMatch: int = Field(default=0, ge=0, le=100, description="经历匹配度 0-100")
    requirementCoverage: int = Field(default=0, ge=0, le=100, description="岗位要求覆盖度 0-100")
    advantages: list[str] = Field(default_factory=list, description="优势列表")
    matchedSkills: list[str] = Field(default_factory=list, description="已匹配技能")
    partialSkills: list[SkillMatchDetail] = Field(default_factory=list, description="部分匹配技能及原因")
    missingSkills: list[str] = Field(default_factory=list, description="岗位缺口/缺失技能")
    resumeProblems: list[ResumeProblem] = Field(default_factory=list, description="简历问题及建议")
    optimizationSuggestions: list[OptimizationSuggestion] = Field(default_factory=list, description="具体优化建议")


class ChatMessage(BaseModel):
    role: str = Field(..., description="消息角色：user 或 assistant")
    content: str = Field(..., description="消息内容")


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="用户当前问题")
    resume: str = Field(default="", description="当前使用的简历文本（通常为优化后版本）")
    original_resume: str = Field(default="", description="原始简历文本")
    optimized_resume: str = Field(default="", description="优化后简历文本")
    jd: str = Field(default="", description="目标岗位 JD")
    match_result: MatchResult | None = Field(default=None, description="岗位匹配分析结果")
    optimized_match_result: MatchResult | None = Field(default=None, description="优化后岗位匹配分析结果")
    original_match_score: int | None = Field(default=None, ge=0, le=100, description="原始匹配度")
    optimized_match_score: int | None = Field(default=None, ge=0, le=100, description="优化后匹配度")
    history: list[ChatMessage] = Field(default_factory=list, description="历史对话记录")


class ChatResponse(BaseModel):
    answer: str = Field(description="AI 回复内容")
