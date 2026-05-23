"""
知识库
支持 TXT / PDF / DOCX / MD 多格式上传
"""
import os
import config_data as config
import hashlib
import io
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from datetime import datetime


# ==================== 多格式文本提取 ====================

def extract_text_from_uploaded_file(uploaded_file) -> tuple[str, str]:
    """
    从上传的文件对象中提取文本内容，支持 TXT / PDF / DOCX / MD

    Args:
        uploaded_file: Streamlit UploadedFile 对象

    Returns:
        (text_content, file_type) 元组
        file_type 为 "txt" / "pdf" / "docx" / "md" / "unknown"
    """
    file_name = uploaded_file.name.lower()
    file_bytes = uploaded_file.read()
    # 重置文件指针，以便后续可能再次读取
    uploaded_file.seek(0)

    if file_name.endswith(".txt"):
        return file_bytes.decode("utf-8", errors="replace"), "txt"
    elif file_name.endswith(".md"):
        return file_bytes.decode("utf-8", errors="replace"), "md"
    elif file_name.endswith(".pdf"):
        return _extract_text_from_pdf(file_bytes), "pdf"
    elif file_name.endswith(".docx"):
        return _extract_text_from_docx(file_bytes), "docx"
    else:
        # 兜底：按 UTF-8 文本处理
        return file_bytes.decode("utf-8", errors="replace"), "unknown"


def _extract_text_from_pdf(file_bytes: bytes) -> str:
    """从 PDF 字节数据中提取文本"""
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(io.BytesIO(file_bytes))
        texts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                texts.append(text)
        return "\n".join(texts)
    except Exception as e:
        return f"[PDF 文本提取失败: {e}]"


def _extract_text_from_docx(file_bytes: bytes) -> str:
    """从 DOCX 字节数据中提取文本"""
    try:
        from docx import Document
        doc = Document(io.BytesIO(file_bytes))
        texts = []
        for para in doc.paragraphs:
            if para.text.strip():
                texts.append(para.text)
        return "\n".join(texts)
    except Exception as e:
        return f"[DOCX 文本提取失败: {e}]"

def check_md5(md5_str: str):
    """检查传入的md5字符串是否已经被处理过了"""
    # 检查md5记录文件是否存在
    if not os.path.exists(config.md5_path):
        # 文件不存在，说明肯定没有处理过任何md5
        # 创建一个空的文件（写入模式，编码UTF-8）
        open(config.md5_path, 'w', encoding='utf-8').close()
        return False  # 返回False表示未处理过
    else:
        # 文件存在，逐行读取并检查
        for line in open(config.md5_path, 'r', encoding='utf-8').readlines():
            line = line.strip()  # 去除字符串前后的空格和换行符
            if line == md5_str:  # 如果找到匹配的md5
                return True  # 返回True表示已经处理过

        return False  # 遍历完所有行都没找到，表示未处理过



def save_md5(md5_str: str):
    """将传入的md5字符串，记录到文件内保存"""
    with open(config.md5_path, 'a', encoding="utf-8") as f:
        f.write(md5_str + '\n')  # 写入md5字符串并换行



def get_string_md5(input_str: str, encoding='utf-8'):
    """将传入的字符串转换为md5字符串"""
    # 将字符串转换为bytes字节数组
    # 因为hashlib需要处理字节数据，不能直接处理字符串
    str_bytes = input_str.encode(encoding=encoding)

    # 创建md5对象
    md5_obj = hashlib.md5()  # 得到md5对象（哈希对象）
    md5_obj.update(str_bytes)  # 更新内容（传入即将要转换的字节数组）
    md5_hex = md5_obj.hexdigest()  # 得到md5的十六进制字符串（32位）

    return md5_hex



class KnowledgeBaseService(object):
    def __init__(self):
        # 如果文件夹不存在则创建，如果存在则跳过
        os.makedirs(config.persist_directory, exist_ok=True)
        self.chroma = Chroma(
            collection_name=config.collection_name,  # 数据库的表名
            embedding_function=DashScopeEmbeddings(model="text-embedding-v4"),
            persist_directory=config.persist_directory,  # 数据库本地存储文件夹
        )  # 向量存储的实例 Chroma向量库对象

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,  # 分割后的文本段最大长度
            chunk_overlap=config.chunk_overlap,  # 连续文本段之间的字符重叠数量
            separators=config.separators,  # 自然段落划分的符号
            length_function=len,  # 使用Python自带的len函数做长度统计的依据
        )  # 文本分割器的对象



    def upload_by_str(self, data: str, filename):
        """将传入的字符串，进行向量化，存入向量数据库中"""
        # 先得到传入字符串的md5值
        md5_hex = get_string_md5(data)

        if check_md5(md5_hex):
            return "【跳过】内容已经存在知识库中"

        if len(data) > config.max_split_char_number:
            knowledge_chunks: list[str] = self.splitter.split_text(data)
        else:
            knowledge_chunks = [data]

        metadata = {
            "source": filename,
            # 2025-01-01 10:00:00
            "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operator": "蓝文静",
        }

        self.chroma.add_texts(  # 内容就加载到向量库中了
            # iterable -> list \ tuple
            knowledge_chunks,
            metadatas=[metadata for _ in knowledge_chunks]
        )

        save_md5(md5_hex)

        return "【成功】内容已经成功载入向量库"

    def get_all_documents(self) -> list[dict]:
        """
        获取知识库中所有文档的摘要信息（按源文件分组）
        Returns:
            list[dict]: [{source, chunk_count, create_time, operator, sample_content}, ...]
        """
        try:
            collection_data = self.chroma._collection.get(include=["metadatas", "documents"])
            ids = collection_data.get("ids", [])
            metadatas = collection_data.get("metadatas", [])
            documents = collection_data.get("documents", [])

            # 按 source 分组
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
                    # 过滤掉以 # 开头的注释行，取第一个非注释行作为预览
                    lines = content.split("\n")
                    preview_line = ""
                    for line in lines:
                        stripped = line.strip()
                        if stripped and not stripped.startswith("#"):
                            preview_line = stripped
                            break
                    if not preview_line:
                        # 如果全是注释行，取前100字符
                        preview_line = content[:100]
                    source_groups[source]["sample_content"] = preview_line[:100]

            return list(source_groups.values())
        except Exception as e:
            print(f"获取文档列表失败: {e}")
            return []

    def delete_document(self, source_name: str) -> str:
        """
        删除指定源文件的所有文档片段
        Args:
            source_name: 源文件名（metadata 中的 source 字段）
        Returns:
            操作结果字符串
        """
        try:
            # 查询所有 source 匹配的文档
            collection_data = self.chroma._collection.get(
                where={"source": source_name},
                include=["metadatas"]
            )
            ids = collection_data.get("ids", [])
            if not ids:
                return f"未找到来源为「{source_name}」的文档"

            # 删除这些文档
            self.chroma._collection.delete(ids=ids)
            return f"成功删除文档「{source_name}」（共 {len(ids)} 个片段）"
        except Exception as e:
            return f"删除文档失败: {str(e)}"


if __name__ == '__main__':  #简单测试是否能将文本转向量存如向量库
    service = KnowledgeBaseService()
    r = service.upload_by_str(data="阿司匹林", filename="testfile")
    print(r)