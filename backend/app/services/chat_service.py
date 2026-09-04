import json
import os
from typing import Any

from groq import Groq
from groq import GroqError

CHAT_SYSTEM_PROMPT = """你是一名专业的AI求职助手，擅长招聘分析、简历优化、岗位匹配和面试辅导。

你已经获得用户的原始简历、优化后简历（如果有）、目标岗位JD以及岗位匹配分析结果（如果有的话）。

回答时必须优先基于用户真实简历和当前岗位JD，不要虚构用户没有的经历、技能或项目。

状态判断：
- 如果用户询问简历相关问题，但未提供简历，请回答："目前还没有检测到你的简历，请先上传简历。"
- 如果用户询问岗位匹配相关问题，但只提供了简历未提供JD，请分析简历后提醒："如果你再提供目标岗位JD，我可以进一步分析岗位匹配度。"
- 如果用户询问技术知识、面试技巧等一般性问题，可以正常回答，不必强行联系简历。

如果用户问"刚才修改了什么""为什么这样修改""这段是否夸张"等关于优化的问题，请基于原始简历和优化后简历的对比进行回答，指出具体改动点和原因。

回答应该：
1. 简洁
2. 具体
3. 可执行
4. 尽量使用列表、标题、加粗
5. 避免没有意义的大段总结

请用中文回答。"""


class ChatServiceError(Exception):
    """聊天服务异常基类。"""


class ChatConfigError(ChatServiceError):
    """配置缺失或无效。"""


class ChatAPIError(ChatServiceError):
    """Groq API 返回错误。"""


class ChatService:
    def __init__(self) -> None:
        self.api_key = os.getenv("GROQ_API_KEY", "").strip()
        self.base_url = os.getenv("LLM_BASE_URL", "").strip() or None
        self.model = os.getenv("LLM_MODEL", "qwen/qwen3.8-27b").strip()

    def get_advice(
        self,
        message: str,
        resume: str,
        original_resume: str,
        optimized_resume: str,
        jd: str,
        match_result: dict[str, Any] | None,
        optimized_match_result: dict[str, Any] | None,
        original_match_score: int | None,
        optimized_match_score: int | None,
        history: list[dict[str, str]],
    ) -> str:
        if not self.api_key:
            raise ChatConfigError("未配置 GROQ_API_KEY，请在 backend/.env 中设置")

        client_kwargs: dict[str, Any] = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url

        client = Groq(**client_kwargs)

        context_parts = []
        if resume.strip():
            context_parts.append(f"【当前简历】\n{resume.strip()}")
        if original_resume.strip():
            context_parts.append(f"【原始简历】\n{original_resume.strip()}")
        if optimized_resume.strip() and optimized_resume != original_resume:
            context_parts.append(f"【优化后简历】\n{optimized_resume.strip()}")
        if jd.strip():
            context_parts.append(f"【目标岗位JD】\n{jd.strip()}")
        if match_result:
            context_parts.append(f"【原始岗位匹配分析结果】\n{json.dumps(match_result, ensure_ascii=False, indent=2)}")
        if optimized_match_result:
            context_parts.append(f"【优化后岗位匹配分析结果】\n{json.dumps(optimized_match_result, ensure_ascii=False, indent=2)}")
        if original_match_score is not None and optimized_match_score is not None:
            diff = optimized_match_score - original_match_score
            context_parts.append(
                f"【匹配度对比】原始匹配度：{original_match_score}%，优化后匹配度：{optimized_match_score}%，变化：{diff:+.0f}%"
            )

        user_content = message.strip()
        if context_parts:
            user_content = "\n\n".join(context_parts) + f"\n\n【用户当前问题】\n{user_content}"

        messages = [{"role": "system", "content": CHAT_SYSTEM_PROMPT}]
        for item in history:
            role = item.get("role")
            content = item.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": user_content})

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
            )
        except GroqError as exc:
            raise ChatAPIError(f"Groq API 调用失败: {exc}") from exc
        except Exception as exc:
            raise ChatAPIError(f"调用 Groq 服务时发生错误: {exc}") from exc

        content = response.choices[0].message.content
        if not content:
            raise ChatAPIError("Groq 返回内容为空")

        return content.strip()


chat_service = ChatService()
