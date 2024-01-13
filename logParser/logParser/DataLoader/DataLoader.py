# import os
# from typing import List
# import tiktoken
#
# from langchain.document_loaders import (
#     NotebookLoader,
#     TextLoader,
#     UnstructuredMarkdownLoader,
# )
#
# from langchain.docstore.document import Document
# from langchain.embeddings import HuggingFaceEmbeddings
# from langchain.text_splitter import CharacterTextSplitter
# from langchain.vectorstores import Chroma
#
# from utils.const import (
#     CHROMA_COLLECTION_NAME,
#     CHROMA_PERSIST_DIR,
#     DATA_PATH,
#     LOG_TYPES,
# )
#
# LOADER_DICT = {
#     "py": TextLoader,
#     "ipynb": NotebookLoader,
#     "md": UnstructuredMarkdownLoader,
#     "txt": UnstructuredMarkdownLoader,
# }
#
# # # load_dotenv()
# # with open("../.keys/keys.txt", "r") as f:
# #     os.environ["OPENAI_API_KEY"] = f.read().strip()
# #     openai.api_key = os.environ["OPENAI_API_KEY"]
#
#
# class DataBaseLoader:
#     local_file_path = DATA_PATH
#     collection_name = "dev"
#     collection_persist_directory = CHROMA_PERSIST_DIR
#     collection = CHROMA_COLLECTION_NAME
#     chunk_size = 500
#     chunk_overlap = 100
#     db = Chroma(
#         persist_directory=CHROMA_PERSIST_DIR,
#         embedding_function=HuggingFaceEmbeddings(),
#         collection_name=collection_name,
#     )
#     #ToDo: 검색 url은 위키 페이지로?
#     search_url = [
#         "https://developers.kakao.com/docs/latest/ko/kakaologin/rest-api"
#     ]
#
#     def create(self, learning_messages: List[str]):
#
#         input_text_list = self._load_data()
#         self.add_embeddings(input_text_list)
#         # search_text_list = [search.query(url) for url in self.search_url]
#         # self.add_embeddings(search_text_list)
#
#         learning_messages.append("Chroma Collection 생성이 완료 되었습니다.")
#         learning_messages.append("Manual File 데이터의 Document 등록이 완료 되었습니다.")
#         learning_messages.append("Search 데이터의 Document 등록이 완료 되었습니다.")
#
#     def _get_data_files(self):
#         files = []
#         for root, subfolders, filenames in os.walk(self.local_file_path):
#             for filename in filenames:
#                 if ".py" in filename:
#                     files.append(root + "/" + filename)
#         return files
#
#     def _load_data(self):
#
#         enc = tiktoken.encoding_for_model(ENCODING_MODEL)
#         files = self._get_data_files()
#         data = []
#         for file in files:
#             with open(file, "r") as f:
#                 content = f.read()
#             data.append(self._preprocess(file, content, enc))
#
#         return data
#
#     def _preprocess(self, file, datum, enc):
#
#         def _truncate_text(text, max_tokens=3000):
#             tokens = enc.encode(text)
#             if len(tokens) <= max_tokens:  # 토큰 수가 이미 3000 이하라면 전체 텍스트 반환
#                 return text
#             return enc.decode(tokens[:max_tokens])
#
#         filename = file.split("/")[-1].split(".")[0]
#         full_content = f"job: {datum}"
#         full_content_truncated = _truncate_text(full_content, max_tokens=3000)
#         # summary = self.summarizer.run(text=full_content_truncated)
#
#         result = {
#             "log_type": log_type
#             "job_name": filename,
#             "job": full_content_truncated,
#             # "summary": summary
#         }
#         return result
#
#     def add_embeddings(self, text_list: List[str]):
#         text_splitter = CharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
#         for page_content in text_list:
#             if page_content["job"] is None:
#                 continue
#             documents = text_splitter.split_documents(
#                 [Document(page_content=text["job"]) for text in text_list]
#             )
#
#         # Chroma DB에 Document 저장
#         self.db.from_documents(
#             documents,
#             # 어떤 Embedding 기법을 사용할지 지정하는 코드 (OpenAIEmbeddings을 사용하겠다.)
#             HuggingFaceEmbeddings(),
#             collection_name=self.collection_name,
#             persist_directory=self.collection_persist_directory,
#         )
#
#         print("Success adding embedding documents")
#
#     def query(self, query: str, max_document_size: int = 3):
#         docs = self.db.similarity_search(query=query, k=max_document_size)
#
#         return [doc.page_content for doc in docs]