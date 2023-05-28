#!/usr/bin/env python3

import os
import re
import sys
import time
from functools import cache

import openai
from openai import ChatCompletion
openai.api_key = os.environ['OPENAI_API_KEY']


class Chat(object):
    """Tiny wrapper around OpenAI Chat API"""

    def __init__(self, system_message, name=None, history=[]):
        """Create a new chat session.

        system_message: The prompt directive for the chat bot
        history: A list of previous messages in the chat, used to seed the chat.
        """
        self.system_message = system_message
        self.name = name or 'chatbot'
        self.history = [
            {'role': 'system', 'content': re.sub('\s+', ' ', self.system_message)},
        ]
        self.history.extend(history)

    def get_response(self, message):
        """Get a response from the chat bot and update the chat history."""
        self.history.append({'role': 'user', 'content': message})
        response = ChatCompletion.create(
            model='gpt-3.5-turbo',
            temperature=0.9,
            messages=self.history,
        )
        answer = response.choices[0].message.content
        self.history.append({'role': 'assistant', 'content': answer})
        return answer

    def last_message(self):
        """Get the last message in the chat history or throw an error if there is no message."""
        if len(self.history) == 0:
            throw('No message in history')
        return self.history[-1]['content']


class Debate(object):
    def __init__(self, turn_limit=20):
        """Create a new debate session.

        turn_limit: The number of turns before the debate ends.
        """
        self.turn_count = turn_limit
        self.chat_index = 0
        # We create two chats, one for each side of the debate.
        # If you customize this, you can make them debate about a different topic.
        self.chats = [
            Chat('''
            You are a OOP Evangelist.
            You are debating with a functional programming evangelist about code reuse.
            Your goal is to find which situations are better for OOP for code reuse.
            Think step by step and dismatle the functional programming evangelist's arguments using your knowledge of programming and their challenges.
            Always use bullet points to enumerate your arguments. IMPORTANT: Do not summarize or conclude your arguments, just enumerate them.
            Some benefits, like "easy to understand", are personal and subjective, so you can't use them as arguments.
            Provide examples to illustrate your counter-arguments.
            ''',
                 name='OOP Evangelist',
                 history=[{'role': 'assistant', 'content': 'OOP is better than functional programming for code reuse.'}],
            ),
            Chat('''
            You are a Functional Programming Evangelist.
            You are debating with a OOP evangelist about code reuse.
            Your goal is to find which situations are better for functional programming for code reuse.
            Think step by step and dismatle the OOP evangelist's arguments using your knowledge of programming and their challenges.
            Always use bullet points to enumerate your arguments. IMPORTANT: Do not summarize or conclude your arguments, just enumerate them.
            Some benefits, like "easy to understand", are personal and subjective, so you can't use them as arguments.
            Provide examples to illustrate your counter-arguments.
            ''',
                 name='Functional Programming Evangelist',
            ),
        ]
        # We count the number of "Thank you", "You're welcome", and such to determine when the debate is over.
        self.thank_you_count = 4

    def print_last_message(self):
        """Print the last message of the current chat.

        This is used to show the current state of the debate.
        """
        print(f'{self.current_chat().name}:\n{self.current_chat().last_message()}')

    def current_chat(self):
        return self.chats[self.chat_index]

    def next_chat(self):
        """Switch to the next chatbot"""
        self.chat_index = (self.chat_index + 1) % len(self.chats)

    def turn(self):
        """Perform a single turn of the debate."""

        argument = self.current_chat().last_message()
        self.next_chat()
        self.current_chat().get_response(argument)
        last_message = self.current_chat().last_message()

        # Check if the debate is over
        # Yes, in every instance of the debate, it ended with them thanking each other.
        if re.search(r'\b(thank you|you\'re welcome|great day)\b', last_message, re.IGNORECASE):
            self.thank_you_count -= 1

        if self.thank_you_count == 0:
            self.end_debate()
            sys.exit(0)

        self.print_last_message()

    def end_debate(self):
        """End the debate with a summary of the discussion."""
        print(f'=== End of debate! ===')
        print(self.current_chat().get_response('''
        The debate is over. Summarize it, enumarating the pros and cons of each side.
        '''))
        sys.exit(0)

    def loop(self):
        """Loop over the turns of the debate.

        This is the main loop of the program.
        """
        print('=== Provocation ===')
        self.print_last_message()
        for turn in range(self.turn_count, 0, -1):
            print()
            print(f'=== Turn {turn:02} ===')
            self.turn()
            time.sleep(3)

        end_debate()

if __name__ == '__main__':
    Debate().loop()
