#!/usr/bin/env python3

from debate_oop import *
import pytest
from pytest_mock import mocker


def test_create_chat():
    new_chat = Chat("Hello there!")
    assert new_chat.name == "chatbot"
    assert new_chat.history == [{"role": "system", "content": "Hello there!"}]

def test_last_message():
    new_chat = Chat("Hello there!")
    assert new_chat.last_message() == "Hello there!"
