# -*- coding: utf-8 -*-

import json
import os
import string
import random
import re
import copy

from langchain.memory import ConversationBufferMemory, FileChatMessageHistory

import reflex as rx
from logParser.utils.style import (
    input_style,
    button_style,
    answer_style,
    spinner_style,
    question_style,
)
from logParser.utils.const import (
    HISTORY_DIR,
    SUCCESS_MSG,
)



def decoding(coding_key, path_to_keys, answer):
    inversed = {v: k for k, v in coding_key.items()}
    for v in re.sub('[^A-Za-z0-9_]+', ' ', answer).split(" "):
        if v in inversed.keys():
            answer = answer.replace(v, inversed[v])
    return answer


def encoding(obj_for_parsing, question=None, coding_key=None):

    if coding_key is None:
        coding_key, coding_val = coding_key_val(obj_for_parsing)

    if question is not None:
        pattern = re.compile(r'\b(?:' + '|'.join(map(re.escape, coding_key.keys())) + r')(?![A-Za-z0-9_])')
        question = pattern.sub(lambda x: coding_key.get(x.group(), x.group()), question)
        for k in re.sub('[^A-Za-z0-9_]+', ' ', question).split(" "):
            if (k not in coding_key.keys()) and (k not in coding_key.values()) and len(k) > 0:
                coding_key[k] = random_generate_key()
                question = re.sub(fr'\b{k}', coding_key[k], question)

    for k_from, k_to in coding_key.items():
        obj_for_parsing = obj_for_parsing.replace(f"'{k_from}':", f"'{k_to}':")
        obj_for_parsing = obj_for_parsing.replace(f'"{k_from}":', f'"{k_to}":')
        obj_for_parsing = obj_for_parsing.replace(f'\\"{k_from}\\":', f'\\"{k_to}\\":')
    return coding_key, question, obj_for_parsing


def random_generate_key():
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(10))


def coding_key_val(log_sample):
    log_data = json.loads(log_sample)
    coding_key, coding_value = {}, {}
    for k, v in _recursive_items(log_data):
        random_str = random_generate_key()
        while random_str in coding_key.keys():
            random_str = random_generate_key()
        if k not in coding_key.keys():
            coding_key[k] = random_str
        if (type(v) not in [dict, list]):
            if type(v) is str:
                coding_value[v] = _encoding_value(v)

    return coding_key, coding_value


def _recursive_items(dictionary):
    for key, value in dictionary.items():
        if type(value) is list:
            for sub_v in value:
                try:
                    sub_v = json.loads(sub_v)
                except:
                    yield (key, value)
                finally:
                    if (type(sub_v) is dict):
                        yield (key, ' ')
                        yield from _recursive_items(sub_v)
                    else:
                        yield (key, value)
        else:
            try:
                value = json.loads(value)
            except:
                yield (key, value)
            finally:
                if (type(value) is dict):
                    yield (key, ' ')
                    yield from _recursive_items(value)
                else:
                    yield (key, value)


def _encoding_value(values):
    if type(values) is str:
        return values
    elif type(values) is int:
        return int
    elif type(values) is float:
        return float
    elif type(values) is bool:
        return True
    elif type(values) is list:
        return [_encoding_value(v) for v in values]
    elif type(values) is type(None):
        return values
    else:
        raise TypeError(f"Unsupported types for encoding values: {type(values)}")


def validate_answer(answer):
    error_message = SUCCESS_MSG
    print(answer)
    try:
        answer = answer[re.search(r"\ndef\b|def\b", answer).start():re.search(r"\ndf = ", answer).start()+1]
    except Exception as e:
        error_message = f"(Format Error: {e}) Please check the answer format, following the instruction."
        return error_message, answer

    try:
        _mapper = exec(answer)
    except Exception as e:
        error_message = e
    return error_message, answer


def qa(question, answer) -> rx.Component:
    return rx.box(
        rx.box(
            rx.text(question, text_align="right"),
            style=question_style,
        ),
        # rx.box(
        #     rx.text(answer, text_align="left"),
        #     style=answer_style,
        # ),
        rx.code_block(
            answer,
            language="python",
            show_line_numbers=True,
        ),
        margin_y="1em",
        margin_top="50px;"
    )


class Data(rx.Model, table=True):
    """Data for KAKAO SYNC"""
    subject: str
    content: str
    summary: str


def load_conversation_history(conversation_id: str):
    file_path = os.path.join(HISTORY_DIR, f"{conversation_id}.json")
    try:
        return FileChatMessageHistory(file_path)
    except FileNotFoundError:
        with open(file_path, 'w') as f:
            json.dump({}, f)
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
