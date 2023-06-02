#!/usr/bin/env python3

from debate_fp import *
from pytest_mock import mocker


def test_create_message():
    assert create_message('user', 'hello') == {'role': 'user', 'content': 'hello'}

def test_add_message():
    bot = Bot(name='Joe', chat=[{'role': 'assistant', 'content': 'whazzup'}])
    message = {'role': 'user', 'content': 'hello'}
    assert add_message(bot, message) == Bot(
        name='Joe',
        chat=[
            {'role': 'assistant', 'content': 'whazzup'},
            {'role': 'user', 'content': 'hello'},
        ]
    )

def test_get_last_text():
    bot = Bot(
        name='Joe',
        chat=[
            {'role': 'assistant', 'content': 'hello'},
            {'role': 'user', 'content': 'hello there'},
        ]
    )
    assert get_last_text(bot) == 'hello there'

def test_turn(mocker):
    mocker.patch(
        'debate_fp.get_response',
        return_value='Hey there!'
    )
    debate = (
        Bot(name='Joe', chat=[]),
        Bot(name='Zoe', chat=[{'role': 'assistant', 'content': 'Hello!'}])
    )
    assert turn(debate) == (
        Bot(name='Joe', chat=[{'role': 'user', 'content': 'Hello!'}, {'role': 'assistant', 'content': 'Hey there!'}]),
        Bot(name='Zoe', chat=[{'role': 'assistant', 'content': 'Hello!'}])
    )
