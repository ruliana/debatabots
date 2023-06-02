#!/usr/bin/env python3

"""
This is the Functional Prgrammin version of `debate_oop`.

It keeps a conversation between two chatbot using different instructions.
"""

import os
import re
import time
import sys
from toolz import curry, pipe
from typing import NamedTuple

import openai
from openai import ChatCompletion
openai.api_key = os.environ['OPENAI_API_KEY']

Message = dict[str, str]
Chat = list[Message]
Bot = NamedTuple('Bot', [('name', str), ('chat', Chat)])
Debate = tuple[Bot, Bot]

@curry
def create_message(role: str, message: str) -> Message:
    return {'role': role, 'content': re.sub(r' +', ' ', message)}

@curry
def add_message(bot: Bot, message: Message) -> Bot:
    name, chat = bot
    return Bot(name=name, chat=chat + [message])

def get_response(bot: Bot) -> str:
    response = ChatCompletion.create(
        model='gpt-3.5-turbo',
        temperature=0.9,
        messages=bot.chat,
    )
    return response.choices[0].message.content

def get_last_text(bot: Bot) -> str:
    if len(bot.chat) == 0:
        throw('No message in history')
    return bot.chat[-1]['content']

def turn(debate: Debate) -> Debate:
    answerer, questioner = debate
    answerer_with_question = pipe(
        questioner,
        get_last_text,
        create_message('user'),
        add_message(answerer),
    )
    answerer_with_answer = pipe(
        answerer_with_question,
        get_response,
        create_message('assistant'),
        add_message(answerer_with_question),
    )

    return (answerer_with_answer, questioner)

def print_turn(bot: Bot, turn_number: int) -> None:
    print()
    print(f'## Turn {turn_number}')
    print(f'{bot.name}:')
    print(bot.chat[turn_number]['content'])
    sys.stdout.flush()

def run_debate(debate: Debate, debate_length: int) -> None:
    answerer, questioner = debate

    for i in range(debate_length - 1):
        print_turn(questioner, i + 1)

        # Go for the next turn, unless we already have the next message
        if len(answerer.chat) > i + 1:
            questioner, answerer = answerer, questioner
        else:
            # Invert the roles of the debaters at each turn
            questioner, answerer = turn((answerer, questioner))

    print_turn(questioner, i + 2)

provoker = [
    create_message('system', '''
    You are a Functional Programming Evangelist.
    You are debating with a OOP evangelist about code reuse.
    Always use bullet points to enumerate your arguments. IMPORTANT: Do not summarize or conclude your arguments, just enumerate them.
    Some benefits, like "easy to understand", are personal and subjective, so you can't use them as arguments.
    IMPORTANT: Make sure to add examples to illustrate your points.
    '''),
    create_message('assistant', 'Functional Programming is better than OOP for code reuse.'),
    create_message('user', 'Can you elaborate on what you mean by "better"?'),
    create_message('assistant', '''
    Sure, here are some criteria I will use to compare the two paradigms when it comes to code reuse:
    1. Immutability
    2. Higher-Order Functions
    3. Composition
    4. Purity
    5. Separation of Concerns
    6. Modularity
    7. Domain-Specific Languages
    8. Type Inference
    Let's go through each of these points in turn and compare how functional programming is better suited for code reuse than OOP.
    '''),
]

contender = [
    create_message('system', '''
    You are a Socratic Philosopher.
    You are debating with a OOP Evangelist about code reuse and your goal is to estimulate their critical thinking by questioning their beliefs.
    You are not trying to win the debate, but to make them find the root point of each claim.
    Use the Socratic Questioning to do this. You can use the following questions:

    1. **Clarifying concepts:**
        - Can you elaborate on what you mean by that point?
        - How would you define this concept in your own words?
        - Can you provide a concrete example to explain this?

    2. **Probing assumptions:**
        - What are you assuming when you say that?
        - Why do you think that assumption holds true?
        - Can we think of a situation where that assumption may not be valid?

    3. **Probing reasons and evidence:**
        - What reasons do you have for believing that?
        - Can you provide evidence to support your point of view?
        - How do you reconcile this idea with [contrary evidence]?

    4. **Questioning viewpoints and perspectives:**
        - Have you considered any alternative viewpoints?
        - How might [different person or group] see this issue?
        - Why do you think others might disagree with you?

    5. **Probing implications and consequences:**
        - If we follow your argument to its logical conclusion, what would happen?
        - What are the potential implications of your viewpoint?
        - What might be the consequences if we ignore this issue?

    6. **Questioning the question:**
        - Why do you think I asked this question?
        - What does this question assume?
        - Is there another way to phrase the question that might provide a different perspective or answer?

    Never agree with the other person, even if they are right. Instead, ask them to elaborate on their point of view.
    '''),
    create_message('user', 'Functional Programming is better than OOP for code reuse.'),
    create_message('assistant', 'Can you elaborate on what you mean by "better"?'),
]

if __name__ == '__main__':
    run_debate(
        (
            Bot('Socratic Philosopher', contender),
            Bot('Functional Programming Evangelist', provoker)
        ),
        10
    )
