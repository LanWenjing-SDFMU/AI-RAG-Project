from langchain_community.llms.tongyi import Tongyi

# 使用 qwen-max 模型
model = Tongyi(model="qwen-max")

# 调用invoke向模型提问
res = model.invoke(input="你是谁呀能做什么?")

for chunk in res:
    print(chunk, end="", flush=True)
