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
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1", # 如果用本地部署的大模型服务，修改为对应的URL
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
            ], # type: ignore
            extra_body={'enable_thinking': False}
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"❌ 请求大模型分析时发生错误: {e}")
        raise


'''
如果使用本地部署的大模型服务，可直接使用下面代码，并注释掉上面的代码
'''

# 首先，要确保本地已经部署了一个兼容OpenAI API的大模型服务，并且该服务正在运行。
# 其次，确保在环境变量中设置了LOCAL_LLM_API_KEY（如果服务需要API密钥）。一般来说，本地服务可能不需要API密钥，可以将其留空或设置为任意值。
# 然后，可以使用下面的代码来初始化客户端并发送请求

# def get_llm_client() -> OpenAI:
#     """
#     初始化并返回一个配置好的OpenAI客户端，用于调用本地部署的大模型服务。
#
#     Raises:
#         ValueError: 如果环境变量未设置。
#         Exception: 客户端初始化失败。
#     """
#     try:
#         api_key = os.getenv("LOCAL_LLM_API_KEY")
#         if not api_key:
#             raise ValueError("环境变量 LOCAL_LLM_API_KEY 未设置或为空。")
#
#         client = OpenAI(
#             api_key=api_key,
#             base_url="http://localhost:8000/v1",  # 本地大模型服务的URL
#         )
#         return client
#     except Exception as e:
#         print(f"❌ LLM客户端初始化失败: {e}")
#         raise
#
# def request_llm_analysis(client: OpenAI, model: str, system_prompt: str, user_prompt: str) -> str:
#     """
#     向本地大语言模型发送分析请求并返回结果。
#     """
#     try:
#         completion = client.chat.completions.create(
#             model=model,
#             messages=[
#                 {'role': 'system', 'content': system_prompt},
#                 {'role': 'user', 'content': user_prompt}
#             ]
#         )
#         return completion.choices[0].message.content
#     except Exception as e:
#         print(f"❌ 请求本地大模型分析时发生错误: {e}")
#         raise