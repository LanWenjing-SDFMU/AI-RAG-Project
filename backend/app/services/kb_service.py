"""
知识库服务
"""
import os
import hashlib
from datetime import datetime

from langchain_community.embeddings import DashScopeEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.rag import config_data as config


def get_string_md5(input_str: str, encoding='utf-8') -> str:
    """计算字符串的 MD5"""
    str_bytes = input_str.encode(encoding=encoding)
    md5_obj = hashlib.md5()
    md5_obj.update(str_bytes)
    return md5_obj.hexdigest()


def check_md5(md5_str: str) -> bool:
    """检查 MD5 是否已存在"""
    if not os.path.exists(config.md5_path):
        open(config.md5_path, 'w', encoding='utf-8').close()
        return False
    for line in open(config.md5_path, 'r', encoding='utf-8').readlines():
        if line.strip() == md5_str:
            return True
    return False


def save_md5(md5_str: str):
    """保存 MD5 到文件"""
    with open(config.md5_path, 'a', encoding="utf-8") as f:
        f.write(md5_str + '\n')


class KnowledgeBaseService:
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

        os.makedirs(config.persist_directory, exist_ok=True)
        self.chroma = Chroma(
            collection_name=config.collection_name,
            embedding_function=DashScopeEmbeddings(model="text-embedding-v4"),
            persist_directory=config.persist_directory,
        )

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            separators=config.separators,
            length_function=len,
        )

    def upload_by_str(self, data: str, filename: str, operator: str = "") -> str:
        """将字符串内容向量化存入知识库"""
        md5_hex = get_string_md5(data)

        if check_md5(md5_hex):
            return "【跳过】内容已经存在知识库中"

        if len(data) > config.max_split_char_number:
            knowledge_chunks = self.splitter.split_text(data)
        else:
            knowledge_chunks = [data]

        metadata = {
            "source": filename,
            "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operator": operator,
        }

        self.chroma.add_texts(
            knowledge_chunks,
            metadatas=[metadata for _ in knowledge_chunks]
        )

        save_md5(md5_hex)
        return "【成功】内容已经成功载入向量库"

    def get_all_documents(self) -> list[dict]:
        """获取知识库中所有文档的摘要信息"""
        try:
            collection_data = self.chroma._collection.get(include=["metadatas", "documents"])
            ids = collection_data.get("ids", [])
            metadatas = collection_data.get("metadatas", [])
            documents = collection_data.get("documents", [])

            from collections import OrderedDict
            source_groups = OrderedDict()
            for i, meta in enumerate(metadatas):
                source = meta.get("source", "未知")
                if source not in source_groups:
                    source_groups[source] = {
                        "source": source,
                        "chunk_count": 0,
                        "create_time": meta.get("create_time", ""),
                        "operator": meta.get("operator", ""),
                        "sample_content": "",
                        "doc_ids": [],
                    }
                source_groups[source]["chunk_count"] += 1
                source_groups[source]["doc_ids"].append(ids[i])
                if not source_groups[source]["sample_content"] and i < len(documents):
                    content = documents[i] or ""
                    lines = content.split("\n")
                    preview_line = ""
                    for line in lines:
                        stripped = line.strip()
                        if stripped and not stripped.startswith("#"):
                            preview_line = stripped
                            break
                    if not preview_line:
                        preview_line = content[:100]
                    source_groups[source]["sample_content"] = preview_line[:100]

            return list(source_groups.values())
        except Exception as e:
            print(f"获取文档列表失败: {e}")
            return []

    def delete_document(self, source_name: str) -> str:
        """删除指定源文件的所有文档片段"""
        try:
            collection_data = self.chroma._collection.get(
                where={"source": source_name},
                include=["metadatas"]
            )
            ids = collection_data.get("ids", [])
            if not ids:
                return f"未找到来源为「{source_name}」的文档"

            self.chroma._collection.delete(ids=ids)
            return f"成功删除文档「{source_name}」（共 {len(ids)} 个片段）"
        except Exception as e:
            return f"删除文档失败: {str(e)}"

    def get_vector_store(self):
        """获取向量存储对象"""
        return self.chroma
