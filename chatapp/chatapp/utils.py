# -*- coding: utf-8 -*-

import os

from langchain.memory import ConversationBufferMemory, FileChatMessageHistory

import reflex as rx
from .style import *

from .const import (
    HISTORY_DIR,
)


def qa(question, answer) -> rx.Component:
    return rx.box(
        rx.box(
            rx.text(question, text_align="right"),
            style=question_style,
        ),
        rx.box(
            rx.text(answer, text_align="left"),
            style=answer_style,
        ),
        margin_y="1em",
    )


class Data(rx.Model, table=True):
    """Data for KAKAO SYNC"""
    subject: str
    content: str
    summary: str


def load_conversation_history(conversation_id: str):
    file_path = os.path.join(HISTORY_DIR, f"{conversation_id}.json")
    return FileChatMessageHistory(file_path)


def log_user_message(history: FileChatMessageHistory, user_message: str):
    history.add_user_message(user_message)


def log_bot_message(history: FileChatMessageHistory, bot_message: str):
    history.add_ai_message(bot_message)


def get_chat_history(conversation_id: str):
    history = load_conversation_history(conversation_id)
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        input_key="user_message",
        chat_memory=history,
    )

    return memory.buffer
