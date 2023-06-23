#!/usr/bin/env python3

"""
Utility functions for the chatbot
"""

import os
import re
import time
import sys
from toolz import curry
from typing import Any, NamedTuple
from collections.abc import Callable

import openai
from openai import ChatCompletion
openai.api_key = os.environ['OPENAI_API_KEY']

MODEL = 'gpt-3.5-turbo-0613'
TEMPERATURE = 0.0

Message = dict[str, str]
FunctionDescription = dict[str, Any]
Chat = list[Message]
Bot = NamedTuple('Bot', [('name', str), ('chat', Chat)])

@curry
def create_message(role: str, message: str) -> Message:
    """
    Create a message stripped of extra spaces.
    """
    return {'role': role, 'content': re.sub(r' +', ' ', message)}

def system_message(message: str) -> Message:
    """
    Create a system message.

    Convenience function for ``create_message('system', message)``.
    """
    return create_message('system', message)

def user_message(message: str) -> Message:
    """
    Create a user message.

    Convenience function for ``create_message('user', message)``.
    """
    return create_message('user', message)

def assistant_message(message: str) -> Message:
    """
    Create an assistant message.

    Convenience function for ``create_message('assistant', message)``.
    """
    return create_message('assistant', message)

def function_answer(function_name: str,answer: str) -> Message:
    """
    Create a function answer message.
    """
    return {'role': 'function', 'name': function_name, 'content': answer}

@curry
def add_message(bot: Bot, message: Message) -> Bot:
    """
    Add a message to a bot's chat history.
    """
    name, chat = bot
    return Bot(name=name, chat=chat + [message])

def with_retries(func, retries=3, exception_class=None, sleep_time=None):
    """
    Encapsulates a function call in a retry loop.

    Returns a function that can be called with the same arguments as the original function.
    """
    def wrapper(*args, **kwargs):
        last_exception = None
        for retry in range(retries):
            try:
                return func(*args, **kwargs)
            except exception_class as e:
                last_exception = e
                if sleep_time is None:
                    print(f'{exception_class}. Waiting {sleep_time} seconds before retrying. Retry {retry + 1}/{retries}', file=sys.stderr)
                    time.sleep(sleep_time)
                else:
                    print(f'{exception_class}. Retry {retry + 1}/{retries}', file=sys.stderr)
        raise last_exception
    return wrapper

def get_response(bot: Bot) -> str:
    """
    Ask the GPT-3 model to generate a response to the chat history of a bot.
    """
    response = ChatCompletion.create(
        model=MODEL,
        temperature=TEMPERATURE,
        messages=bot.chat,
    )
    return response.choices[0].message.content

def create_react_responder(functions: dict[str, Any]) -> Callable[[Bot], dict[str, str]]:
    """
    ReAct responder function factory.

    ReAct is a technique for LLMs to use knowledge beyound their training cuttof.
    See https://arxiv.org/abs/2106.05237 for more details.
    See https://www.promptingguide.ai/techniques/react for a straightforward explanation.

    The new ``functions`` parameter in the GPT API does most of the work for us.

    Parameters
    ----------
    functions : dict[str, Any]
        A dictionary of function descriptions that can be used by the ReACT model.

    Returns
    -------
    react_responder : Callable[[Bot], str]
        A function that takes a bot and its chat up to now and returns a response.
    """
    def react_responder(bot: Bot) -> str:
        response = openai.ChatCompletion.create(
            model=MODEL,
            temperature=TEMPERATURE,
            messages=bot.chat,
            functions=functions,
            function_call='auto',
        )
        return response.choices[0].message

    return react_responder


def get_response_with_retries(bot: Bot) -> str:
    """
    Convenience function for ``get_response`` that retries on rate limit errors.
    """
    get_resp = with_retries(get_response)
    return get_resp(bot)

def get_last_text(bot: Bot) -> str:
    """
    Get the text of the last message in a bot's chat history.
    """
    if len(bot.chat) == 0:
        throw('No message in history')
    return bot.chat[-1]['content']
