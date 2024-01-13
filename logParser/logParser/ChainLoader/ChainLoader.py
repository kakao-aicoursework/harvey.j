# -*- coding: utf-8 -*-

import os

from langchain.chains import LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.tools import Tool
from langchain.utilities import GoogleSearchAPIWrapper
from langchain.schema import SystemMessage

from logParser.utils.const import (
    LOG_TYPE_PROMPT_TEMPLATE,
    IDENTIFY_KEYS_PROMPT_TEMPLATE,
    ERROR_FIX_PROMPT_TEMPLATE,
    PYSPARK_PARSING_CODE_PROMPT_TEMPLATE,
    OPENAI_DEFAULT_MODEL_ID,
    HF_DEFAULT_MODEL_ID,
    DEFAULT_MODEL_ID,
    ANSWER_WITH_FEEDBACK_PROMPT_TEMPLATE
)
from logParser.LargeLangModel.LargeLangModel import LargeLangModel
import openai
import subprocess

AUTH_TOKEN_READ = "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"
AUTH_TOKEN_WRITE = "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"
huggingface_bin_path = "/home/bc-user/.pyenv/versions/log-parser/bin"
os.environ["PATH"] = f"{huggingface_bin_path}:{os.environ['PATH']}"
os.environ["HUGGINGFACEHUB_API_TOKEN"] = "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"

openai.api_key = "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"
os.environ["OPENAI_API_KEY"] = "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"
openai.api_key = os.environ["OPENAI_API_KEY"]

subprocess.run(["huggingface-cli", "login", "--token", AUTH_TOKEN_READ])



class ChainLoader:

    def __init__(self, model_id:str = "", model_from:str = "openai"):

        if not model_id:
            model_id = (
                OPENAI_DEFAULT_MODEL_ID if model_from == "openai"
                else HF_DEFAULT_MODEL_ID if model_from == "huggingface"
                else DEFAULT_MODEL_ID
            )

        llm = LargeLangModel(model_id, model_from)
        self.llm = llm.llm
        # self.summarizer = self._build_summarizer()
        self.log_type = self._create_chain(
            template_path=LOG_TYPE_PROMPT_TEMPLATE,
            output_key="output",
        )
        self.identify_keys = self._create_chain(
            template_path=IDENTIFY_KEYS_PROMPT_TEMPLATE,
            output_key="output",
        )
        self.pyspark_parsing_code = self._create_chain(
            template_path=PYSPARK_PARSING_CODE_PROMPT_TEMPLATE,
            output_key="output",
        )
        self.error_fix = self._create_chain(
            template_path=ERROR_FIX_PROMPT_TEMPLATE,
            output_key="output",
        )
        self.answer_with_feedback = self._create_chain(
            template_path=ANSWER_WITH_FEEDBACK_PROMPT_TEMPLATE,
            output_key="output",
        )

    @staticmethod
    def _read_prompt_template(file_path: str) -> str:
        with open(file_path, "r") as f:
            prompt_template = f.read()

        return prompt_template

    def _create_chain(self, template_path, output_key):
        return LLMChain(
            llm=self.llm,
            prompt=ChatPromptTemplate.from_template(
                template=self._read_prompt_template(template_path)
            ),
            output_key=output_key,
            verbose=True,
        )

    def _query_web_search(self, user_message: str, google_api_key:str, google_cse_id:str) -> str:

        search = GoogleSearchAPIWrapper(
            google_api_key=os.getenv("GOOGLE_API_KEY", google_api_key),
            google_cse_id=os.getenv("GOOGLE_CSE_ID", google_cse_id)
        )

        search_tool = Tool(
            name="Google Search",
            description="Search Google for recent results.",
            func=search.run,
        )

        context = {"user_message": user_message}
        context["related_web_search_results"] = search_tool.run(user_message)

        has_value = self.search_value_check_chain.run(context)

        print(has_value)
        if has_value == "Y":
            return self.search_compression_chain.run(context)
        else:
            return ""

    def _build_summarizer(self):
        system_message = "assistant는 user의 내용을 bullet point 3줄로 요약하라. 영어인 경우 한국어로 번역해서 요약하라."
        system_message_prompt = SystemMessage(content=system_message)

        human_template = "{text}\n---\n위 내용을 bullet point로 3줄로 한국어로 요약해"
        human_message_prompt = HumanMessagePromptTemplate.from_template(
            human_template)

        chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt,
                                                        human_message_prompt])

        chain = LLMChain(llm=self.llm, prompt=chat_prompt)
        return chain
