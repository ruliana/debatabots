#!/usr/bin/env python3

import re

def append_paragraph(paragraphs: list[str], paragraph: str) -> list[str]:
    if paragraph.strip() == '':
        return paragraphs
    else:
        return paragraphs + [paragraph]

def markdown_splitter(text: str) -> list[str]:
    """
    Split a markdown text in a list of paragraphs. Keep all the titles before each paragraph and add them to the paragraph for context.
    """
    paragraphs = []
    current_paragraph = ''
    title_breadcrumb = []
    for line in text.splitlines():
        if re.match(r'^\s*$', line):
            paragraphs = append_paragraph(paragraphs, current_paragraph)
            current_paragraph = ''
        if re.match(r'^#+ ', line):
            # Count number of # to determine title level
            title_level = len(re.match(r'^(#+) ', line).group(1))

            # Remove all breadcrumbs above the current title level
            title_breadcrumb = title_breadcrumb[:title_level - 1]
            title_breadcrumb.append(line)
        else:
            if line.strip() != '':
                if current_paragraph == '' and len(title_breadcrumb) > 0:
                    current_paragraph = '\n'.join(title_breadcrumb) + '\n'
                current_paragraph += line.strip()
    paragraphs = append_paragraph(paragraphs, current_paragraph)
    return paragraphs
