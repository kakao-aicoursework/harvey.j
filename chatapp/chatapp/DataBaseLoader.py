import os
from typing import List
import openai
import tiktoken

from langchain.document_loaders import (
    NotebookLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)

from dotenv import load_dotenv
from langchain.docstore.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma

from .const import (
    CHROMA_COLLECTION_NAME,
    CHROMA_PERSIST_DIR,
    FILE_EXTENSION,
    DATA_PATH,
    GPT_MODEL
)

LOADER_DICT = {
    "py": TextLoader,
    "ipynb": NotebookLoader,
    "md": UnstructuredMarkdownLoader,
    "txt": UnstructuredMarkdownLoader,
}

# load_dotenv()
with open("../.keys/openai_keys.txt", "r") as f:
    os.environ["OPENAI_API_KEY"] = f.read().strip()
    openai.api_key = os.environ["OPENAI_API_KEY"]



class DataBaseLoader:
    manual_file_path = DATA_PATH
    collection_name = "dev"
    collection_persist_directory = CHROMA_PERSIST_DIR
    collection = CHROMA_COLLECTION_NAME
    chunk_size = 500
    chunk_overlap = 100
    db = Chroma(
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=OpenAIEmbeddings(),
        collection_name=collection_name,
    )
    search_url = [
        "https://developers.kakao.com/docs/latest/ko/kakaologin/rest-api"
    ]
    subject_list = ["시작하기", "기능 소개", "과정 예시", "도입 안내", "설정 안내", "기타"]

    def create(self, learning_messages: List[str]):
        input_text_list = self._load_data()
        # search_text_list = [search.query(url) for url in self.search_url]

        self.add_embeddings(input_text_list)
        # self.add_embeddings(search_text_list)

        learning_messages.append("Croma Collection 생성이 완료 되었습니다.")
        learning_messages.append("Manual File 데이터의 Document 등록이 완료 되었습니다.")
        learning_messages.append("Search 데이터의 Document 등록이 완료 되었습니다.")
    def _load_data(self):

        enc = tiktoken.encoding_for_model(GPT_MODEL)
        with open(self.manual_file_path, "r") as f:
            data = f.read()
        temp = data.split("#")

        # DB 저장
        data = []
        for d in temp:
            data.append(self._preprocess(d, enc))
        return data

    def _preprocess(self, datum, enc):

        def _truncate_text(text, max_tokens=3000):
            tokens = enc.encode(text)
            if len(tokens) <= max_tokens:  # 토큰 수가 이미 3000 이하라면 전체 텍스트 반환
                return text
            return enc.decode(tokens[:max_tokens])

        subject = datum[:datum.find("\n")]
        content = datum[datum.find("\n")+1:].replace("\n", "")
        self.subject_list.append(subject)

        full_content = f"주제: {subject}\n내용: {content}"
        full_content_truncated = _truncate_text(full_content, max_tokens=3000)
        # summary = self.summarizer.run(text=full_content_truncated)

        result = {
            "subject": subject,
            "content": full_content_truncated,
            # "summary": summary
        }
        return result

    def add_embeddings(self, text_list: List[str]):
        print(text_list)
        text_splitter = CharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
        for page_content in text_list:
            if page_content["content"] is None:
                continue
            documents = text_splitter.split_documents(
                [Document(page_content=text["content"]) for text in text_list]
            )

        # Chroma DB에 Document 저장
        self.db.from_documents(
            documents,
            # 어떤 Embedding 기법을 사용할지 지정하는 코드 (OpenAIEmbeddings을 사용하겠다.)
            OpenAIEmbeddings(),
            collection_name=self.collection_name,
            persist_directory=self.collection_persist_directory,
        )

        print("Success adding embedding documents")

    def query(self, query: str, max_document_size: int = 3):
        docs = self.db.similarity_search(query=query, k=max_document_size)

        return [doc.page_content for doc in docs]