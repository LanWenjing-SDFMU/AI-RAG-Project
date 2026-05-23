from .vector_stores import VectorStoreService
from langchain_community.embeddings import DashScopeEmbeddings
from . import config_data as config
from .file_history_store import FileChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_core.runnables.history import RunnableWithMessageHistory


def print_prompt(prompt):
    """打印提示词（调试用）"""
    try:
        print("=" * 20)
        print(prompt.to_string())
        print("=" * 20)
    except UnicodeEncodeError:
        # Windows 终端 GBK 编码无法处理某些 Unicode 字符时忽略
        pass
    return prompt


def get_history(session_id: str):
    """根据 session_id 获取聊天历史记录"""
    return FileChatMessageHistory(
        session_id=session_id,
        storage_path=config.chat_history_dir
    )


class RagService(object):

    def __init__(self):
        self.vector_service = VectorStoreService(
            embedding=DashScopeEmbeddings(model=config.embedding_model_name)
        )

        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", "你是一个临床决策支持助手。严格基于以下参考资料回答用户问题。如果参考资料中没有相关信息，请明确告知。\n\n参考资料：{context}"),
            MessagesPlaceholder("history"),
            ("user", "{input}")
        ])

        self.chat_model = ChatTongyi(model=config.chat_model_name, streaming=True)

        self.chain = self.__get_chain()

    def __get_chain(self):
        """获取最终的执行链"""

        def format_document(docs: list[Document]):
            """将检索到的文档列表格式化为字符串"""
            if not docs:
                return "无相关参考资料"

            formatted_str = ""
            for doc in docs:
                formatted_str += f"文档片段：{doc.page_content}\n文档元数据：{doc.metadata}\n\n"
            return formatted_str

        def format_for_retriever(value: dict) -> str:
            """从输入字典中提取用于检索的查询字符串"""
            return value["input"]

        def format_for_prompt_template(value):
            """
            重组数据格式，为提示词模板准备正确的输入结构
            将嵌套的 {"input": {"input": "...", "history": [...]}, "context": "..."}
            转换为平铺的 {"input": "...", "context": "...", "history": [...]}
            """
            new_value = {}
            new_value["input"] = value["input"]["input"]
            new_value["context"] = value["context"]
            new_value["history"] = value["input"]["history"]
            return new_value

        retriever = self.vector_service.get_retriever()

        # 构建内部链（不使用 RunnableWithMessageHistory 的版本）
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

        # 包装历史消息支持
        conversation_chain = RunnableWithMessageHistory(
            inner_chain,
            get_history,
            input_messages_key="input",
            history_messages_key="history",
        )

        return conversation_chain


if __name__ == '__main__':
    # session id 配置
    session_config = {
        "configurable": {
            "session_id": "user_001",
        }
    }
    res = RagService().chain.invoke({"input": "是干咳无痰的"}, session_config)
    print(res)