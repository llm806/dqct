# -*- coding: utf-8 -*-

import os
from openai import OpenAI
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

def get_llm_client() -> OpenAI:
    """
    初始化并返回一个配置好的OpenAI客户端，用于调用兼容服务（如DashScope）。

    Raises:
        ValueError: 如果环境变量未设置。
        Exception: 客户端初始化失败。
    """
    try:
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            raise ValueError("环境变量 DASHSCOPE_API_KEY 未设置或为空。")

        client = OpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        return client
    except Exception as e:
        print(f"❌ LLM客户端初始化失败: {e}")
        raise

def request_llm_analysis(client: OpenAI, model: str, system_prompt: str, user_prompt: str) -> str:
    """
    向大语言模型发送分析请求并返回结果。
    """
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            extra_body={'enable_thinking': False}
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"❌ 请求大模型分析时发生错误: {e}")
        raise