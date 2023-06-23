#!/usr/bin/env python3

from lib.markdown_splitter import *

def test_single_paragraph():
    text = 'This is a paragraph.'
    assert markdown_splitter(text) == [text]

def test_two_paragraphs():
    text = '''
This is a paragraph.

This is another paragraph.
    '''
    assert markdown_splitter(text) == [
        'This is a paragraph.',
        'This is another paragraph.',
    ]

def test_include_previous_title():
    text = '''
# Title
This is a paragraph.

This is another paragraph.
    '''

    assert markdown_splitter(text) == [
        '# Title\nThis is a paragraph.',
        '# Title\nThis is another paragraph.',
    ]

def test_include_previous_title_and_subtitle():
    text = '''
# Title
This is a paragraph.

## Subtitle 1
This is another paragraph.

This is a third paragraph.

## Subtitle 2

This is a fourth paragraph.
    '''

    assert markdown_splitter(text) == [
        '# Title\nThis is a paragraph.',
        '# Title\n## Subtitle 1\nThis is another paragraph.',
        '# Title\n## Subtitle 1\nThis is a third paragraph.',
        '# Title\n## Subtitle 2\nThis is a fourth paragraph.',
    ]
