# -*- coding: utf-8 -*-

import reflex as rx
from .utils import *
from chatapp.State import State


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
            style=input_style,
        ),
        rx.button(
            "Ask",
            on_click=State.answer,
            style=button_style,
        ),
    )

def leaning_wrap() -> rx.Component:
    return rx.hstack(
        rx.box(
            rx.foreach(State.leaning_messages, lambda message: rx.box(
                rx.text(message, style=answer_style)
            )), width="100%"
        ),
        rx.button("학습", on_click=State.leaning_handler, style=button_style),
        margin_top="50px;"
    )

def loading() -> rx.Component:
    return rx.cond(
        State.is_working,
        rx.box(rx.spinner(color="lightgreen", thickness=5, speed="1.5s", size="xl"), style=spinner_style)
    )

def index() -> rx.Component:
    return rx.container(
        leaning_wrap(),
        chat(),
        action_bar(),
    )


app = rx.App(state=State)
app.add_page(index)
app.compile()
