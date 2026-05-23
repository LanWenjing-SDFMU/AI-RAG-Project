"""
RAG 检索增强生成服务
"""
import os

from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_core.runnables.history import RunnableWithMessageHistory
from app.rag.vector_stores import VectorStoreService
from app.rag.file_history_store import FileChatMessageHistory
from app.rag import config_data as config


def print_prompt(prompt):
    """打印提示词（调试用）"""
    try:
        print("=" * 20)
        print(prompt.to_string())
        print("=" * 20)
    except UnicodeEncodeError:
        pass
    return prompt


def get_history(session_id: str):
    """根据 session_id 获取聊天历史记录"""
    return FileChatMessageHistory(
        session_id=session_id,
        storage_path=config.chat_history_dir
    )


class RagService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self.vector_service = VectorStoreService(
            embedding=DashScopeEmbeddings(model=config.embedding_model_name)
        )

        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", "你是一个临床决策支持助手。严格基于以下参考资料回答用户问题。如果参考资料中没有相关信息，请明确告知。\n\n参考资料：{context}"),
            MessagesPlaceholder("history"),
            ("user", "{input}")
        ])

        self.chat_model = ChatTongyi(model=config.chat_model_name, streaming=True)
        self.chain = self._get_chain()

    def _get_chain(self):
        """获取最终的执行链"""

        def format_document(docs: list[Document]):
            if not docs:
                return "无相关参考资料"
            formatted_str = ""
            for doc in docs:
                formatted_str += f"文档片段：{doc.page_content}\n文档元数据：{doc.metadata}\n\n"
            return formatted_str

        def format_for_retriever(value: dict) -> str:
            return value["input"]

        def format_for_prompt_template(value):
            new_value = {}
            new_value["input"] = value["input"]["input"]
            new_value["context"] = value["context"]
            new_value["history"] = value["input"]["history"]
            return new_value

        retriever = self.vector_service.get_retriever()

        inner_chain = (
            {
                "input": RunnablePassthrough(),
                "context": RunnableLambda(format_for_retriever) | retriever | format_document
            }
            | RunnableLambda(format_for_prompt_template)
            | self.prompt_template
            | print_prompt
            | self.chat_model
            | StrOutputParser()
        )

        conversation_chain = RunnableWithMessageHistory(
            inner_chain,
            get_history,
            input_messages_key="input",
            history_messages_key="history",
        )

        return conversation_chain

    def chat(self, input_text: str, session_id: str = "default") -> str:
        """执行对话（非流式）"""
        session_config = {"configurable": {"session_id": session_id}}
        result = self.chain.invoke({"input": input_text}, session_config)
        return result

    async def chat_stream(self, input_text: str, session_id: str = "default"):
        """执行对话（流式输出）"""
        session_config = {"configurable": {"session_id": session_id}}
        async for chunk in self.chain.astream({"input": input_text}, session_config):
            yield chunk

    def diagnose(self, query: str, session_id: str = "differential_diag_001") -> str:
        """执行鉴别诊断"""
        session_config = {"configurable": {"session_id": session_id}}
        try:
            result = self.chain.invoke({"input": query}, session_config)
            return result
        except Exception as e:
            return f"生成鉴别诊断时出现错误：{str(e)}"

    def drug_safety_check(self, drug_name: str, age: int = 0, allergy: str = "", notes: str = "") -> str:
        """用药安全核查"""
        search_query = f"{drug_name.strip()} 可用性 不良反应 禁忌"
        try:
            all_docs = self.vector_service.vector_store.similarity_search(search_query, k=5)
            filtered_docs = [
                doc for doc in all_docs
                if "drug_safety_structured" in doc.metadata.get("source", "").lower()
            ]
        except Exception as e:
            filtered_docs = []

        if not filtered_docs:
            context = "未找到该药物的安全信息文档。"
        else:
            context = "\n\n".join([doc.page_content for doc in filtered_docs])

        prompt = f"""你是一个药物安全评估专家。严格基于以下药物安全知识库内容，根据患者信息判断该药物是否可以使用，并按指定格式输出。

患者信息：
- 药物名称：{drug_name.strip()}
- 年龄：{age if age > 0 else '未提供'} 岁
- 过敏史：{allergy.strip() if allergy.strip() else '无'}
- 备注（如怀孕、疾病等）：{notes.strip() if notes.strip() else '无'}

知识库内容：
{context}

请输出以下内容（严格遵守格式，不要添加额外解释）：

决策：[✅ 可以使用该药物] 或 [❌ 不可使用该药物]（二选一，并根据患者信息和知识库规则给出理由）

1. 主要不良反应：（列出知识库中提到的主要不良反应）

2. 用药禁忌：（列出知识库中提到的禁忌症，并结合患者信息说明是否存在）

3. 针对该患者的特别提醒：（结合年龄、过敏史、备注，给出个性化提醒）

如果知识库中没有相关信息，请明确说明"知识库中无此药物信息"。
"""
        try:
            response = self.chat_model.invoke(prompt)
            return response.content
        except Exception as e:
            return f"生成评估时出错：{str(e)}"
