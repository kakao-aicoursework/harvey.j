# -*- coding: utf-8 -*-

from typing import List
import reflex as rx

from .DataBaseLoader import DataBaseLoader
from .ChainLoader import ChainLoader

from .utils import *
from .const import *

db = DataBaseLoader()
chainloader = ChainLoader()


class State(rx.State):
    """The app state."""
    chat_history: list[tuple[str, str]]
    user_message: str = ""
    data_path: str = DATA_PATH
    conversation_id: str = "dev"
    leaning_messages: List[str] = []

    def answer(self):

        answer = ""
        history_file = load_conversation_history(self.conversation_id)
        context = dict(user_message=self.user_message)
        context["input"] = context["user_message"]
        context["chat_history"] = get_chat_history(self.conversation_id)

        subject = chainloader.parse_subject_chain.run(context)

        # if subject in db.subject_list:
        #     context["related_documents"] = db.query(context["user_message"])
        #     for step in [chainloader.q_step1_chain]:
        #         context = step(context)
        #         answer += context[step.output_key]
        #         answer += "\n\n"
        # else:
        print(f"DB has no information about the subject: {subject}")
        context["related_documents"] = db.query(context["user_message"])
        context["compressed_web_search_results"] = chainloader._query_web_search(
            context["user_message"]
        )
        answer = chainloader.default_chain.run(context)
        answer = chainloader.summarizer(answer)

        log_user_message(history_file, self.user_message)
        log_bot_message(history_file, answer)


        self.chat_history += [(self.user_message, answer)]
        print(self.chat_history)

        # Clear the question input.
        self.user_message = ""
        # Yield here to clear the frontend input before continuing.
        yield
    def leaning_handler(self):
        db.create(self.leaning_messages)