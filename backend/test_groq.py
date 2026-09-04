from groq import Groq
from dotenv import load_dotenv
import os


load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


response = client.chat.completions.create(
    model="qwen/qwen3.8-27b",
    messages=[
        {
            "role": "user",
            "content": "你现在是AI产品经理，请分析AI产品经理岗位需要哪些能力"
        }
    ]
)


print(response.choices[0].message.content)
