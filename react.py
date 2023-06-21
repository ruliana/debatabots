#!/usr/bin/env python3

import os
import json
import openai
import requests
import sys

from pprint import pprint
from html2text import html2text

from lib.chat import *


def debug_display(stuff: Any) -> None:
    print("=" * 80)
    pprint(stuff)


def ask_assistant(bot: Bot) -> Bot:
    match responder(bot):
        case {'function': 'ask_google', 'arguments': arguments}:
            response = ask_google(arguments['search'])
            bot = add_message(bot, function_answer('ask_google', response))
            return ask_assistant(bot)
        case {'function': 'scrap_web_page', 'arguments': arguments}:
            response = scrap_web_page(arguments['url'])
            bot = add_message(bot, function_answer('scrap_web_page', response))
            return ask_assistant(bot)
        case {'content': content}:
            return add_message(bot, assistant_message(content))
            response = content


def ask_google(query: str) -> str:
    response = requests.get(
        "https://www.googleapis.com/customsearch/v1",
        params={
            'q': query,
            'key': os.environ['GOOGLE_SEARCH_KEY'],
            'cx': os.environ['GOOGLE_SEARCH_APP'],
            # 'excludeSites': 'twitter.com,youtube.com',
        },
    )
    response.raise_for_status()
    result = response.json()

    # Extract fields of interest. GPT can't handle too many tokens.
    entries_of_interest = [
        {'title': item['title'], 'snippet': item['snippet'], 'link': item['link']}
        for item in result['items']
    ]
    entries_of_interest.append({'query': query})
    return json.dumps(entries_of_interest)


def scrap_web_page(url: str) -> str:
    html = requests.get(url).text
    return html2text(html)


def create_responder_parser(responder: Callable[[Bot], dict[str, str]]) -> Callable[[Bot], dict[str, str]]:
    def wrapper(bot: Bot) -> dict[str, str]:
        match responder(bot):
            case {'function_call': {'name': function_name, 'arguments': arguments}}:
                return {
                    'function': function_name,
                    'arguments': json.loads(arguments),
                }
            case {'content': content}:
                return {'content': content}

    return wrapper

functions = [
    {
        'name': 'ask_google',
        'description': "Knowledge base lookup for things you don't know or are more recent than your cutoff training date",
        'parameters': {
            'type': 'object',
            'properties': {
                'search': {
                    'type': 'string',
                    'description': 'The search question to look up on Google',
                },
            },
            'required': ['search'],
        },
    },
    {
        'name': 'scrap_web_page',
        'description': "Scrap a web page for text. Use when you don't know the answer, but you know a website that has it. If the answer is not found, try another website." ,
        'parameters': {
            'type': 'object',
            'properties': {
                'url': {
                    'type': 'string',
                    'description': 'The URL of the web page to scrap',
                },
            },
            'required': ['url'],
        },
    }
]

# Create robust responder
responder = create_react_responder(functions)
responder = create_responder_parser(responder)
responder = with_retries(responder, exception_class=ValueError)
responder = with_retries(responder, exception_class=openai.error.RateLimitError, sleep_time=10)

# Main
bot = Bot(
    name='Assistant',
    chat=[
        user_message('What was the latest score for the Lakers game?'),
    ],
)
try:
    bot = ask_assistant(bot)
except Exception as e:
    print(e, file=sys.stderr)
finally:
    for entry in bot.chat:
        debug_display(f"{entry['role']}:\n{entry['content']}")
