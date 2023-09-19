"""Welcome to Pynecone! This file outlines the steps to create a basic app."""

import openai

from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import SystemMessage
import tiktoken

import pynecone as pc
from .style import *

import os
with open("../.keys/openai_keys.txt", "r") as f:
    os.environ["OPENAI_API_KEY"] = f.read().strip()
    openai.api_key = os.environ["OPENAI_API_KEY"]


MAX_QUESTIONS = 10

enc = tiktoken.encoding_for_model("gpt-3.5-turbo-16k")
def build_summarizer(llm):
    system_message = "assistant는 user의 내용을 bullet point 3줄로 요약하라. 영어인 경우 한국어로 번역해서 요약하라."
    system_message_prompt = SystemMessage(content=system_message)

    human_template = "{text}\n---\n위 내용을 bullet point로 3줄로 한국어로 요약해"
    human_message_prompt = HumanMessagePromptTemplate.from_template(
        human_template)

    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt,
                                                    human_message_prompt])

    chain = LLMChain(llm=llm, prompt=chat_prompt)
    return chain
llm = ChatOpenAI(temperature=0.8)
summarizer = build_summarizer(llm)


def read_prompt_template(file_path: str) -> str:
    with open(file_path, "r") as f:
        prompt_template = f.read()

    return prompt_template


def create_chain(llm, template_path, output_key):
    return LLMChain(
        llm=llm,
        prompt=ChatPromptTemplate.from_template(
            template=read_prompt_template(template_path),
        ),
        output_key=output_key,
        verbose=True,
    )


PROMPT = [
    {
        "role": "system",
        "content": "카카오싱크 데이터를 참조하여 질문에 대한 답을 하는 챗봇입니다."
    },
]


class Data(pc.Model, table=True):
    """Data for KAKAO SYNC"""
    subject: str
    content: str
    summary: str

class State(pc.State):
    """The app state."""
    chat_history: list[tuple[str, str]]
    question: str = ""
    data_path: str = "./data/project_data_카카오싱크.txt"
    prompt: list = PROMPT

    async def handle_submit(self):
        self.is_working = True
        yield
        # 데이터 조회
        temp = self._data_preprocess()
        # DB 저장
        data = []
        for d in temp:
            data.append(self._preprocess(d))

        self.prompt.append(
            {
                "role": "assistant",
                "content": self.data
            }
        )

    def _preprocess(self, datum):

        def truncate_text(text, max_tokens=3000):
            tokens = enc.encode(text)
            if len(tokens) <= max_tokens:  # 토큰 수가 이미 3000 이하라면 전체 텍스트 반환
                return text
            return enc.decode(tokens[:max_tokens])

        subject = datum[:datum.find("\n")]
        content = datum[datum.find("\n")+1:]

        full_content = f"주제: {subject}\n내용: {content}"
        full_content_truncated = truncate_text(full_content, max_tokens=3000)
        summary = summarizer.run(text=full_content_truncated)

        result = {
            "subject": subject,
            "content": content,
            "summary": summary
        }
        return result
    def _data_preprocess(self):
        with open(self.data_path, "r") as f:
            data = f.read()
        data = data.split("#")
        return data


    def answer(self):
        # Our chatbot has some brains now!

        self.prompt.append(
            {
                "role": "user",
                "content": self.question
            }
        )

        session = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=self.prompt,
            stop=None,
            temperature=0.7,
            stream=True,
        )

        answer = ""
        self.chat_history += [(self.question, answer)]
        print(self.chat_history)

        # Clear the question input.
        self.question = ""
        # Yield here to clear the frontend input before continuing.
        yield

        for item in session:
            if hasattr(item.choices[0].delta, "content"):
                answer += item.choices[0].delta.content
                self.chat_history[-1] = (
                    self.chat_history[-1][0],
                    answer,
                )
                yield



# Define views.
def qa(question, answer) -> pc.Component:
    return pc.box(
        pc.box(
            pc.text(question, text_align="right"),
            style=question_style,
        ),
        pc.box(
            pc.text(answer, text_align="left"),
            style=answer_style,
        ),
        margin_y="1em",
    )


def chat() -> pc.Component:
    return pc.box(
        pc.foreach(
            State.chat_history,
            lambda q, a: qa(q, a),
        )
    )


def action_bar() -> pc.Component:
    return pc.hstack(
        pc.input(
            # value=State.question,
            placeholder="질문을 입력하세요",
            on_change=State.set_question,
            style=input_style,
        ),
        pc.button(
            "Ask",
            on_click=State.answer,
            style=button_style,
        ),
    )


def index() -> pc.Component:
    return pc.container(
        chat(),
        action_bar(),
    )


app = pc.App(state=State)
app.add_page(index)
app.compile()

