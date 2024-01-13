# -*- coding: utf-8 -*-

from typing import List
import re
import json

import reflex as rx

# from DataLoader.DataLoader import DataLoader
from logParser.ChainLoader.ChainLoader import ChainLoader

from logParser.utils.utils import (
    load_conversation_history,
    log_bot_message,
    log_user_message,
    get_chat_history,
    encoding,
    decoding,
    validate_answer,
)
from logParser.utils.const import (
    DATA_PATH,
    MAPPING_LOG_TYPE_TABLE,
    MAPPING_LOG_TYPE_PARSING_SAMPLE,
    SUCCESS_MSG,
)


# db = DataLoader()
chainloader = ChainLoader()


class State(rx.State):
    """The app state."""
    chat_history: list[tuple[str, str]]
    user_message: str = ""
    data_path: str = DATA_PATH
    conversation_id: str = "dev"
    learning_messages: List[str] = []
    context: dict = {}

    def on_key_down(self, event):
        if event == "Enter":
            print(event)
            self.answer()

    def answer(self):

        answer = ""
        history_file = load_conversation_history(self.conversation_id)

        if (
                self.context.get("log_sample", None) is None and
                self.context.get("coding_key", None) is None
        ):

            self.context = dict(user_message=self.user_message)
            # 1. log_type
            self.context["log_type"] = chainloader.log_type.run(question=self.context["user_message"])
            with open(MAPPING_LOG_TYPE_TABLE[self.context["log_type"]]) as f:
                log_sample = f.read()
            with open(MAPPING_LOG_TYPE_PARSING_SAMPLE[self.context["log_type"]]) as f:
                parsing_sample = f.read()

            # 2. encoding sample
            coding_key, encoded_q, log_sample = encoding(log_sample, self.context["user_message"])
            self.context["input"] = encoded_q
            self.context["chat_history"] = get_chat_history(self.conversation_id)
            pattern = re.compile(r'\b(?:' + '|'.join(map(re.escape, coding_key.keys())) + r')(?![A-Za-z0-9_])')
            parsing_sample = pattern.sub(lambda x: coding_key.get(x.group(), x.group()), parsing_sample)

            self.context["log_sample"] = log_sample
            self.context["coding_key"] = coding_key
            self.context["parsing_sample"] = parsing_sample

            print("=======")
            print(parsing_sample)
            print("=======")

            # 3. identify keys to parse
            output = chainloader.identify_keys.run(question=encoded_q, log=log_sample, parsing_sample=parsing_sample)
            num_of_keys = output[
                          re.search("The number of keys to parse is ", output).end():
                          re.search("The number of keys to parse is ", output).end()+1
                          ]
            path_to_keys = output[re.search("The path to each key is the following:", output).end():]
            self.context["num_of_keys"] = num_of_keys
            self.context["path_to_keys"] = path_to_keys

            # 4. get answer from llm
            answer += chainloader.pyspark_parsing_code.run(
                question=self.context["input"],
                log=log_sample,
                num_of_keys=num_of_keys,
                path_to_keys=path_to_keys,
                parsing_sample=parsing_sample,
            )
            self.context["answer"] = answer
        else:
            self.context["user_message"] = self.user_message
            pattern = re.compile(
                r'\b(?:' + '|'.join(map(re.escape, self.context["coding_key"].keys())) + r')(?![A-Za-z0-9_])'
            )
            self.context["input"] = pattern.sub(
                lambda x: self.context["coding_key"].get(x.group(), x.group()), self.context["user_message"]
            )
            # 1. get answer after the first question
            answer += chainloader.answer_with_feedback.run(
                user_feedback=self.context["input"],
                log=self.context["log_sample"],
                path_to_keys=self.context["path_to_keys"],
                num_of_keys=self.context["num_of_keys"],
                parsing_sample=self.context["parsing_sample"],
                chat_history=self.context["chat_history"],
            )

        # 5. validate and correct the answer
        while True:
            error_message, code_lines = validate_answer(self.context["answer"])
            if error_message == SUCCESS_MSG:
                break
            # Todo: search for information about error_message in StackOverFlow through Chrome
            answer = chainloader.error_fix.run(
                error_message=error_message,
                log=self.context["log_sample"],
                path_to_keys=self.context["path_to_keys"],
                parsing_sample=self.context["parsing_sample"],
                num_of_keys=self.context["num_of_keys"],
                code=code_lines,
                question=self.context["input"],
            )

        # 6. decode the answer
        self.context["answer"] = answer
        decoded_a = decoding(self.context["coding_key"], self.context["path_to_keys"], self.context["answer"])

        log_user_message(history_file, self.context["user_message"])
        log_bot_message(history_file, decoded_a)
        self.context["chat_history"] = (self.context["input"], self.context["answer"])
        self.chat_history += [(self.user_message, decoded_a)]
        print(self.chat_history[-1])

        # Clear the question input.
        self.user_message = ""
        # Yield here to clear the frontend input before continuing.
        yield

    # @classmethod
    # def clear(cls):
    #     return cls()
    #

    # def learning_handler(self):
    #     db.create(self.leaning_messages)