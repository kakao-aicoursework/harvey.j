# -*- coding: utf-8 -*-

import os
file_path = os.path.dirname(__file__)

MAX_QUESTIONS = 10

# PROMPT
DEFAULT_RESPONSE_PROMPT_TEMPLATE = f"{file_path}/../prompt/default_response.txt"
ERROR_FIX_PROMPT_TEMPLATE = f"{file_path}/../prompt/error_fix.txt"
IDENTIFY_KEYS_PROMPT_TEMPLATE = f"{file_path}/../prompt/identify_keys.txt"
LOG_TYPE_PROMPT_TEMPLATE = f"{file_path}/../prompt/log_type.txt"
PYSPARK_PARSING_CODE_PROMPT_TEMPLATE = f"{file_path}/../prompt/pyspark_parsing_code2.txt"
SEARCH_COMPRESSION_PROMPT_TEMPLATE = f"{file_path}/../prompt/search_compress.txt"
ANSWER_WITH_FEEDBACK_PROMPT_TEMPLATE = f"{file_path}/../prompt/answer_with_feedback.txt"

# LLM MODEL
# ENCODING_MODEL = "gpt-3.5-turbo-16k"
OPENAI_DEFAULT_MODEL_ID = "gpt-4-0613"
HF_DEFAULT_MODEL_ID = "beomi/polyglot-ko-12.8b-safetensors"
DEFAULT_MODEL_ID = "lonby/polyglot-ko-12.8b-safetensors"

# LLM PARAMETER
DEFAULT_TEMPERATURE = 0.3
DEFAULT_TOP_P = 0.9
DEFAULT_MAX_TOKENS = 1024
MODEL_PATH = "./llm"
FINE_TUNINNING_DATA = f"{file_path}/../data/fine_tunning/theAgeOfAiHasBegun.csv"

# DB
FILE_EXTENSION = [".py", ".md", ".ipynb", ".txt"]
LOG_TYPES = ["request", "bid", "win", "click", "conversion"]
DATA_DIR = "/data/adrec_5/harvey/gptTest/log-parser/data"
DATA_PATH = os.path.join(DATA_DIR, "project_data_카카오싱크.txt")
# CODE_DIR = os.path.join(DATA_DIR, "codes", "python")
# SAMPLE_DIR = os.path.join(DATA_DIR, "codes", "python", "notebooks")
# DOC_DIR = os.path.join(DATA_DIR, "docs", "semantic-kernel")
CHROMA_PERSIST_DIR = os.path.join(DATA_DIR, "file-persist")
CHROMA_COLLECTION_NAME = "kakao-bot"

# CHAT HISTORY
HISTORY_DIR = f"{file_path}/../../chat_histories"

# SAMPLE
MAPPING_LOG_TYPE_TABLE = {
    "win": f"{file_path}/../data/sample/logs/win_sample.txt",
    "bid": f"{file_path}/../data/sample/logs/bid_sample.txt",
    "serving": f"{file_path}/../data/sample/logs/xmas_serving_sample.txt",
}

MAPPING_LOG_TYPE_PARSING_SAMPLE = {
    "win": f"{file_path}/../data/sample/parsing/win_log_parsing.txt",
    "bid": f"{file_path}/../data/sample/parsing/bid_log_parsing.txt",
    "serving": f"{file_path}/../data/sample/parsing/xmas_serving_log_parsing.txt",
}

# ETC
SUCCESS_MSG = "The answer may be successfully executed"
