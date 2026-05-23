"""
基于 SQLite 的聊天消息历史存储
将每个会话的消息保存到 SQLite 数据库
"""
from typing import Sequence, List
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, message_to_dict, messages_from_dict
from .database import get_connection


class FileChatMessageHistory(BaseChatMessageHistory):
    """
    基于 SQLite 的聊天消息历史存储
    将每个会话的消息保存到 SQLite 数据库
    """

    def __init__(self, session_id: str, storage_path: str = None):
        """
        初始化聊天历史管理器

        Args:
            session_id: 会话id
            storage_path: 保留此参数以兼容旧接口，实际不再使用
        """
        self.session_id = session_id

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        """
        添加消息到历史记录

        Args:
            messages: 要添加的消息序列
        """
        conn = get_connection()
        try:
            for message in messages:
                msg_dict = message_to_dict(message)
                msg_type = msg_dict.get("type", "")
                msg_data = msg_dict.get("data", {})
                content = msg_data.get("content", "") if isinstance(msg_data, dict) else str(msg_data)

                conn.execute(
                    "INSERT INTO chat_history (session_id, type, content) VALUES (?, ?, ?)",
                    (self.session_id, msg_type, content),
                )
            conn.commit()
        finally:
            conn.close()

    @property
    def messages(self) -> List[BaseMessage]:
        """
        获取当前会话的所有消息
        @property装饰器将messages方法变成成员属性用
        """
        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT type, content FROM chat_history WHERE session_id = ? ORDER BY id ASC",
                (self.session_id,),
            ).fetchall()

            # 将数据库记录转换为 BaseMessage 对象
            from langchain_core.messages import HumanMessage, AIMessage

            result = []
            for row in rows:
                msg_type = row["type"]
                content = row["content"]
                if msg_type == "human":
                    result.append(HumanMessage(content=content))
                elif msg_type == "ai":
                    result.append(AIMessage(content=content))
                else:
                    # 兜底：尝试用 message_from_dict
                    msg_dict = {"type": msg_type, "data": {"content": content}}
                    result.extend(messages_from_dict([msg_dict]))
            return result
        finally:
            conn.close()

    def clear(self) -> None:
        """清空当前会话的所有消息"""
        conn = get_connection()
        try:
            conn.execute(
                "DELETE FROM chat_history WHERE session_id = ?", (self.session_id,)
            )
            conn.commit()
        finally:
            conn.close()


# 使用示例
if __name__ == '__main__':
    # 创建历史管理器
    history = FileChatMessageHistory(
        session_id="user_123",
    )

    # 添加消息示例
    from langchain_core.messages import HumanMessage, AIMessage

    history.add_messages([
        HumanMessage(content="我咳嗽（干咳无痰），推荐什么药？"),
        AIMessage(content="根据资料，推荐右美沙芬、可待因糖浆。如伴有咽痒，可使用氢溴酸右美沙芬片。")
    ])

    # 查看所有消息
    print("所有消息：")
    for msg in history.messages:
        print(f"{msg.type}: {msg.content}")

    # 清空历史
    # history.clear()
