import asyncio
import json
import os
import re
from typing import Any

from groq import Groq
from groq import GroqError
from pydantic import ValidationError

from app.models.schemas import (
    JdAnalysisResult,
    MatchResult,
    ResumeInfo,
)

SYSTEM_PROMPT = """你是一位专业的 HR 与 AI 产品经理求职顾问。用户会提供一段招聘 JD（职位描述），请仔细分析并提取结构化信息。

要求：
1. 仅基于 JD 原文进行分析，不要编造不存在的信息
2. 列表字段如果没有相关内容，返回空数组
3. job_title 如果未明确提及，根据 JD 内容推断最可能的岗位名称
4. 必须返回合法的 JSON，不要包含 markdown 代码块或其他多余文字

返回 JSON 字段说明：
- job_title: 岗位名称（字符串）
- responsibilities: 岗位职责列表
- ai_skills: AI 相关技能（如 LLM、Prompt Engineering、RAG、Agent、机器学习等）
- product_skills: 产品相关技能（如需求分析、用户研究、PRD、数据分析、Axure 等）
- soft_skills: 软技能（如沟通能力、跨部门协作、项目管理等）
- requirements: 硬性要求（学历、工作经验、行业背景等）"""

RESUME_EXTRACTION_PROMPT = """你是一名资深 HR，擅长从简历中提取关键信息。

请从以下简历文本中提取结构化信息，并返回合法 JSON。

返回 JSON 字段说明：
- name: 姓名（未提及则留空字符串）
- contact: 联系方式（电话、邮箱等，合并为一个字符串，未提及则留空）
- objective: 求职意向/目标岗位（未提及则留空）
- school: 学校（最高学历对应的学校，未提及则留空）
- major: 专业（可含学历，如"网络工程 本科"，未提及则留空）
- education: 教育经历列表（每条含学校、专业、学历、时间，一条一段；没有则空数组）
- skills: 技能列表（如 Python、SpringBoot、MySQL 等，不要超过 12 个）
- projects: 项目经历列表（每个项目一条完整描述，保留原文关键信息，不要删减事实）
- internships: 实习/实践经历列表（每条一段完整描述；没有则空数组）
- campusExperience: 校园经历列表（学生组织、社团、志愿活动等；没有则空数组）
- certificates: 证书/奖项列表（如英语六级、奖学金、竞赛获奖等；没有则空数组）
- selfEvaluation: 自我评价（原文内容，未提及则留空）
- other: 其他信息（无法归类但对求职有用的内容；没有则空数组）

要求：
1. 仅基于简历原文提取，不要编造，不要遗漏原文中已有的模块
2. 提取是"结构化整理"，不是"总结删减"，项目/实习描述应保留原文事实细节
3. 必须返回合法 JSON，不要包含 markdown 代码块或其他多余文字"""

MATCH_PROMPT = """你是一名资深互联网招聘专家和AI产品经理。
根据用户简历和岗位JD，分析匹配程度，并给出具体可执行修改建议。
输出严格JSON，不输出其他内容。

返回 JSON 字段说明：
- matchScore: 综合匹配度分数，整数 0-100
- position: 岗位名称（从 JD 推断）
- skillMatch: 技能匹配度，整数 0-100
- projectMatch: 项目经历匹配度，整数 0-100
- experienceMatch: 综合经历匹配度，整数 0-100
- requirementCoverage: 岗位要求覆盖度，整数 0-100
- advantages: 我的优势列表（基于简历与 JD 的匹配点）
- matchedSkills: 已匹配技能列表（简历中明确体现且 JD 要求的技能）
- partialSkills: 部分匹配技能列表，每项包含 skill（技能名称）和 reason（为什么只是部分匹配，如"项目中有使用但简历描述不够突出"）
- missingSkills: 岗位缺口/缺失技能列表（JD 要求但简历中未体现的技能）
- resumeProblems: 简历问题列表，每项包含 problem（问题）和 suggestion（修改建议）
- optimizationSuggestions: 具体优化建议列表，每条对应一个匹配失败或部分匹配的点，包含：
  - id（建议唯一标识，格式 sg-1、sg-2 递增）
  - type（建议类型：modify 修改 / enhance 强化 / add 新增 / delete 删除 / keep 保留，默认 modify）
  - field（所属简历模块，可选值：projects, skills, education, internships, campusExperience, certificates, selfEvaluation, basicInfo）
  - itemIndex（该建议对应模块内的条目索引，从 0 开始；新增类建议填 null）
  - problem（问题）
  - reason（为什么要这样修改）
  - before（修改前表述，从简历原文中摘录；新增类建议留空）
  - after（修改后表述，可直接替换到简历中）

评分参考：
- 90 分以上：简历与岗位高度匹配
- 70-89 分：基本匹配，有部分可优化空间
- 70 分以下：匹配度较低，需要较大调整

要求：
1. 基于真实信息分析，不虚构经历
2. 给出的建议必须具体可执行，针对 JD 要求与简历实际的差距
3. 优化建议的 before 必须来自简历原文，after 必须可直接替换
4. 优化是"改进表达"，不是"删除内容"，不要建议删除已有模块
5. 严格返回 JSON，不要 markdown"""


class GroqServiceError(Exception):
    """Groq 服务调用异常基类。"""


class GroqConfigError(GroqServiceError):
    """配置缺失或无效。"""


class GroqAPIError(GroqServiceError):
    """Groq API 返回错误。"""


class GroqParseError(GroqServiceError):
    """响应解析或校验失败。"""


class GroqService:
    def __init__(self) -> None:
        self.api_key = os.getenv("GROQ_API_KEY", "").strip()
        self.base_url = os.getenv("LLM_BASE_URL", "").strip() or None
        self.model = os.getenv("LLM_MODEL", "qwen/qwen3.8-27b").strip()

    def _create_client(self) -> Groq:
        if not self.api_key:
            raise GroqConfigError("未配置 GROQ_API_KEY，请在 backend/.env 中设置")

        client_kwargs: dict[str, Any] = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url
        return Groq(**client_kwargs)

    def _call_json(
        self,
        system_prompt: str,
        user_content: str,
        temperature: float = 0.3,
    ) -> dict[str, Any]:
        client = self._create_client()

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
            )
        except GroqError as exc:
            raise GroqAPIError(f"Groq API 调用失败: {exc}") from exc
        except Exception as exc:
            raise GroqAPIError(f"调用 Groq 服务时发生错误: {exc}") from exc

        content = response.choices[0].message.content
        if not content:
            raise GroqParseError("Groq 返回内容为空")

        return self._parse_json(content)

    def _parse_json(self, content: str) -> dict[str, Any]:
        content = content.strip()
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError as exc:
                    raise GroqParseError("Groq 返回的内容不是合法 JSON") from exc
            raise GroqParseError("Groq 返回的内容不是合法 JSON")

    async def analyze_jd(self, jd_text: str) -> JdAnalysisResult:
        parsed = await asyncio.to_thread(
            self._call_json, SYSTEM_PROMPT, f"请分析以下招聘 JD：\n\n{jd_text}"
        )
        try:
            return JdAnalysisResult.model_validate(parsed)
        except ValidationError as exc:
            raise GroqParseError(f"Groq 返回数据格式不符合预期: {exc}") from exc

    def extract_resume_info(self, resume_text: str) -> ResumeInfo:
        parsed = self._call_json(
            RESUME_EXTRACTION_PROMPT,
            f"请分析以下简历：\n\n{resume_text}",
            temperature=0.3,
        )
        try:
            return ResumeInfo.model_validate(parsed)
        except ValidationError as exc:
            raise GroqParseError(f"简历信息提取失败: {exc}") from exc

    async def match_resume_jd(self, resume_text: str, jd_text: str) -> MatchResult:
        user_content = f"【简历】\n{resume_text}\n\n【岗位JD】\n{jd_text}"
        parsed = await asyncio.to_thread(
            self._call_json, MATCH_PROMPT, user_content, 0.3
        )
        try:
            return MatchResult.model_validate(parsed)
        except ValidationError as exc:
            raise GroqParseError(f"匹配结果格式不符合预期: {exc}") from exc


groq_service = GroqService()
