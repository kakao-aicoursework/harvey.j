# -*- coding: utf-8 -*-

import os

MAX_QUESTIONS = 10

# PROMPT
Q_STEP1_PROMPT_TEMPLATE = "./chatapp/prompt/q_step1.txt"
DEFAULT_RESPONSE_PROMPT_TEMPLATE = "./chatapp/prompt/default_response.txt"
SEARCH_VALUE_CHECK_PROMPT_TEMPLATE = "./chatapp/prompt/search_value_check.txt"
SEARCH_COMPRESSION_PROMPT_TEMPLATE = "./chatapp/prompt/search_compress.txt"
SUBJECT_PROMPT_TEMPLATE = "./chatapp/prompt/parse_subject.txt"
# SUBJECT_LIST = "./chatapp/prompt/subject_list.txt"

# KEYS
# todo: .keys 폴더로 옮기기
GOOGLE_API_KEY = "AIzaSyA-xeF0kdhD2OvLNgwLUKb_UAIES1WT3as"
GOOGLE_CSE_ID = "3189ea666cf68445e"

# LLM MODEL
GPT_MODEL = "gpt-3.5-turbo-16k"

# DB
FILE_EXTENSION = [".py", ".md", ".ipynb", ".txt"]
DATA_DIR = "./chatapp/data"
DATA_PATH = os.path.join(DATA_DIR, "project_data_카카오싱크.txt")
# CODE_DIR = os.path.join(DATA_DIR, "codes", "python")
# SAMPLE_DIR = os.path.join(DATA_DIR, "codes", "python", "notebooks")
# DOC_DIR = os.path.join(DATA_DIR, "docs", "semantic-kernel")
CHROMA_PERSIST_DIR = os.path.join(DATA_DIR, "file-persist")
CHROMA_COLLECTION_NAME = "kakao-bot"

# CHAT HISTORY
HISTORY_DIR = "./chatapp/chat_histories"