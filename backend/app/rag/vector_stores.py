from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from . import config_data as config
import re


class VectorStoreService(object):

    def __init__(self, embedding):
        self.embedding = embedding
        self.vector_store = Chroma(
            collection_name=config.collection_name,
            embedding_function=self.embedding,
            persist_directory=config.persist_directory,
        )

    def get_retriever(self):
        return self.vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={'k': config.similarity_threshold, 'fetch_k': 10}
        )


def extract_relevant_line(query: str, full_text: str) -> str:
    """
    根据用户查询中的症状关键词，从完整文本中提取最相关的行。
    """
    # 从查询中提取关键症状描述（例如 "咳嗽（干咳无痰）"）
    # 简单策略：匹配 "症状（具体描述）" 或 "症状" 开头的行
    lines = full_text.split('\n')

    # 提取查询中可能存在的症状关键词（取括号前的部分，如 "咳嗽"）
    symptom_match = re.search(r'([^（(]+)[（(]', query)
    if symptom_match:
        symptom_key = symptom_match.group(1).strip()
    else:
        # 如果没有括号，直接用整个查询作为关键词（去掉"推荐药物"等）
        symptom_key = query.replace("推荐药物", "").strip()

    # 寻找包含该关键词的行
    for line in lines:
        if symptom_key in line:
            return line.strip()

    # 如果没有精确匹配，返回第一行（兜底）
    return lines[0].strip() if lines else full_text


if __name__ == '__main__':
    embeddings = DashScopeEmbeddings(model="text-embedding-v4")
    retriever = VectorStoreService(embeddings).get_retriever()

    query = "我咳嗽（干咳无痰），推荐药物"
    res = retriever.invoke(query)

    print("=" * 60)
    print(f"🔍 检索结果：共找到 {len(res)} 条相关内容")
    print("=" * 60)

    for i, doc in enumerate(res, 1):
        print(f"\n📄 【结果 {i}】")
        print(f"📁 来源文件：{doc.metadata.get('source', '未知')}")
        print(f"👤 上传者：{doc.metadata.get('operator', '未知')}")
        print(f"⏰ 上传时间：{doc.metadata.get('create_time', '未知')}")
        print(f"📝 推荐内容：")
        print("-" * 40)
        # 【关键修改】只输出与症状匹配的那一行
        relevant_line = extract_relevant_line(query, doc.page_content)
        print(relevant_line)
        print("-" * 40)

    print("\n" + "=" * 60)