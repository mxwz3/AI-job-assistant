"""PDF 服务本地冒烟测试：不调用 AI，验证 generate_resume_pdf 排版与中文输出。"""

from app.models.schemas import ResumeInfo
from app.services.pdf_service import generate_resume_pdf


def test_pdf() -> None:
    resume = ResumeInfo(
        name="王小明",
        contact="电话：12345678910 | 邮箱：test@example.com",
        objective="软件测试工程师（实习）",
        school="武汉科技大学",
        major="网络工程 本科",
        education=["2023.09 至今 武汉科技大学 网络工程 本科"],
        skills=["功能测试", "SQL", "Postman", "Git", "Linux", "Java", "Spring Boot"],
        projects=[
            "差旅报销系统 2026.05-2026.06 技术：Vue, Spring Boot, MySQL, Redis；"
            "负责报销申请、审批流等模块开发与功能验证，累计编写测试用例 50+；"
            "使用 MySQL 进行数据一致性校验，确保前后端数据同步准确。",
            "Web 安全测试实验 2026.04；SQL 注入实验，了解漏洞原理及常见防御方案，完成实验报告撰写。",
        ],
        certificates=["CET-4", "CET-6"],
        selfEvaluation="测试基础扎实，熟悉用例设计方法，能清晰表达并规范输出测试记录。",
    )

    pdf_bytes = generate_resume_pdf(resume)

    assert pdf_bytes.startswith(b"%PDF"), "输出不是合法 PDF"
    assert len(pdf_bytes) > 1000, f"PDF 过小: {len(pdf_bytes)} 字节"

    with open("test_pdf_output.pdf", "wb") as f:
        f.write(pdf_bytes)

    print(f"OK: 生成 {len(pdf_bytes)} 字节合法 PDF -> test_pdf_output.pdf")


if __name__ == "__main__":
    test_pdf()
