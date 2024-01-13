# -*- coding: utf-8 -*-

import reflex as rx

from logParser.utils.utils import qa
from logParser.utils.style import (
    input_style,
    button_style,
    answer_style,
    spinner_style,
)
from logParser.State import State

import os
import subprocess

import openai


AUTH_TOKEN_READ = "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"
AUTH_TOKEN_WRITE = "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"
huggingface_bin_path = "/home/bc-user/.pyenv/versions/log-parser/bin"
os.environ["PATH"] = f"{huggingface_bin_path}:{os.environ['PATH']}"
os.environ["HUGGINGFACEHUB_API_TOKEN"] = "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"

openai.api_key = "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"
os.environ["OPENAI_API_KEY"] = "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"
openai.api_key = os.environ["OPENAI_API_KEY"]

subprocess.run(["huggingface-cli", "login", "--token", AUTH_TOKEN_READ])



def chat() -> rx.Component:
    return rx.box(
        rx.foreach(
            State.chat_history,
            lambda messages: qa(messages[0], messages[1]),
        )
    )


def action_bar() -> rx.Component:
    return rx.hstack(
        rx.input(
            value=State.user_message,
            placeholder="질문을 입력하세요",
            on_change=State.set_user_message,
            on_key_down=State.on_key_down,
            style=input_style,
        ),
        rx.button(
            "Ask",
            on_click=State.answer,
            style=button_style,
        ),
    )

# def learning_wrap() -> rx.Component:
#     return rx.hstack(
#         rx.box(
#             rx.foreach(State.learning_messages, lambda message: rx.box(
#                 rx.text(message, style=answer_style)
#             )), width="100%"
#         ),
#         rx.button("학습(미지원)", on_click=State.learning_handler, style=button_style),
#         margin_top="50px;"
#     )


def loading() -> rx.Component:
    return rx.cond(
        State.is_working,
        rx.box(rx.spinner(color="lightgreen", thickness=5, speed="1.5s", size="xl"), style=spinner_style)
    )

def index() -> rx.Component:
    return rx.container(
        # learning_wrap(),
        chat(),
        action_bar(),
    )


app = rx.App(state=State)
app.add_page(index)
app.compile()
