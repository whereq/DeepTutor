import os

from openai import OpenAI


# 阿里云 DashScope 兼容 OpenAI 接口地址
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MODEL = "MiniMax/MiniMax-M2.5"

# 优先读取环境变量；未设置时使用你提供的 key（建议后续改为纯环境变量）
API_KEY = os.getenv("DASHSCOPE_API_KEY", "sk-6a8bef38384749e485f2be7909ce0bee")


def main() -> int:
    if not API_KEY:
        print("未检测到 API Key，请设置 DASHSCOPE_API_KEY")
        return 1

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "你是一个简洁的助手。"},
                {"role": "user", "content": "请用一句话介绍你自己。"},
            ],
            temperature=0.7,
            max_tokens=256,
        )
    except Exception as exc:
        print(f"调用失败: {exc}")
        return 1

    content = response.choices[0].message.content if response.choices else ""
    print("调用成功，模型回复：")
    print(content or "<空回复>")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
