# -*- coding: utf-8 -*-

import openai

from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.tools import Tool
from langchain.utilities import GoogleSearchAPIWrapper
from langchain.schema import SystemMessage

from .const import *

with open("../.keys/openai_keys.txt", "r") as f:
    os.environ["OPENAI_API_KEY"] = f.read().strip()
    openai.api_key = os.environ["OPENAI_API_KEY"]

PROMPT = [
    {
        "role": "system",
        "content": "카카오싱크 데이터를 참조하여 질문에 대한 답을 하는 챗봇입니다."
    },
]

class ChainLoader:

    def __init__(self):
        self.llm = ChatOpenAI(temperature=0.8, max_tokens=200, model=GPT_MODEL)
        self.summarizer = self._build_summarizer()
        self.parse_subject_chain = self._create_chain(
            template_path=SUBJECT_PROMPT_TEMPLATE,
            output_key="subject",
        )
        self.q_step1_chain = self._create_chain(
            template_path=Q_STEP1_PROMPT_TEMPLATE,
            output_key="output"
        )
        self.default_chain = self._create_chain(
            template_path=DEFAULT_RESPONSE_PROMPT_TEMPLATE,
            output_key="output"
        )
        self.search_value_check_chain = self._create_chain(
            template_path=SEARCH_VALUE_CHECK_PROMPT_TEMPLATE,
            output_key="output",
        )
        self.search_compression_chain = self._create_chain(
            template_path=SEARCH_COMPRESSION_PROMPT_TEMPLATE,
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

    def _query_web_search(self, user_message: str) -> str:

        search = GoogleSearchAPIWrapper(
            google_api_key=os.getenv("GOOGLE_API_KEY", GOOGLE_API_KEY),
            google_cse_id=os.getenv("GOOGLE_CSE_ID", GOOGLE_CSE_ID)
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
