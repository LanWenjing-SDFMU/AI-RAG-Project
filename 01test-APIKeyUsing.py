from openai import OpenAI
import os

client = OpenAI(
    # 如果没有配置环境变量，请用阿里云百炼API Key替换：api_key="sk-xxx"
    api_key="sk-40358142538b45c781708e76986fa19e",# 配置环境变量后apiKEY可以不在代码中显式声明
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",# API接入地址
)

messages=[ #设定模型回答风格
    {"role": "system", "content": "你是一个Python编程专家，并且不说废话简单回答"},#设定模型的行为和规则
    {"role": "assistant", "content": "好的，我是编程专家，并且话不多，你要问什么？"},#设定模型的回答，由用户设定
    {"role": "user", "content": "输出1-10的数字，使用python代码"}#用户提问
]

completion = client.chat.completions.create(
    model="qwen3.6-plus",  # 深度思考模型。可更换，比如deepseek-v3
    messages=messages,
    extra_body={"enable_thinking": True},
    stream=True #流式输出
)
is_answering = False  # 是否进入回复阶段
print("\n" + "=" * 20 + "思考过程" + "=" * 20)
for chunk in completion:
    delta = chunk.choices[0].delta
    if hasattr(delta, "reasoning_content") and delta.reasoning_content is not None:
        if not is_answering:
            print(delta.reasoning_content, end="", flush=True)
    if hasattr(delta, "content") and delta.content:
        if not is_answering:
            print("\n" + "=" * 20 + "完整回复" + "=" * 20)
            is_answering = True
        print(delta.content, end="", flush=True)