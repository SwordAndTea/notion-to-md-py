import base64
import re

import httpx
from typing import Optional, Dict, List
from pytablewriter import MarkdownTableWriter
from pytablewriter.style import Style


def inline_code(text: str) -> str:
    return f'`{text}`'


def inline_equation(text: str) -> str:
    return f'${text}$'


def bold(text: str) -> str:
    return f'**{text}**'


def italic(text: str) -> str:
    return f'_{text}_'


def strikethrough(text: str) -> str:
    return f'~~{text}~~'


def underline(text: str) -> str:
    return f'<u>{text}</u>'


def link(text: str, href: str) -> str:
    return f'[{text}]({href})'


def code_block(text: str, language: Optional[str] = None) -> str:
    if language == "plain text":
        language = "text"
    return f'```{language or ""}\n{text}\n```'


def equation(text: str) -> str:
    return f'$$\n{text}\n$$'


def heading1(text: str) -> str:
    return f'# {text}'


def heading2(text: str) -> str:
    return f'## {text}'


def heading3(text: str) -> str:
    return f'### {text}'


def quote(text: str) -> str:
    no_newline = text.replace("\n", "\n> ")
    return f'> {no_newline}'


def callout(text: str, icon: Optional[Dict] = None) -> str:
    emoji = icon.get('emoji', '') if icon and icon.get('type') == 'emoji' else ''
    formatted_text = text.replace('\n', '\n> ')
    formatted_emoji = emoji + " " if emoji else ""
    heading_match = re.match(r'^(#{1,6})\s+(.+)', formatted_text)

    if heading_match:
        level, content = heading_match.groups()
        return f'> {"#" * len(level)} {formatted_emoji}{content}'
    return f'> {formatted_emoji}{formatted_text}'


def bullet(text: str, count: Optional[int] = None) -> str:
    text = text.strip()
    return f'{count}. {text}' if count else f'- {text}'


def todo(text: str, checked: bool) -> str:
    return f'- [{"x" if checked else " "}] {text}'


def _generate_image_markup(alt: str, href: str) -> str:
    if href.startswith('data:'):
        base64_data = href.split(',', 1)[1]
        return f'![{alt}](data:image/png;base64,{base64_data})'
    return f'![{alt}]({href})'


def image(alt: str, href: str, convert_to_base64: bool = False) -> str:
    if not convert_to_base64 or href.startswith('data:'):
        return _generate_image_markup(alt, href)

    with httpx.Client() as client:
        response = client.get(href)
    base64_data = base64.b64encode(response.content).decode()
    return f'![{alt}](data:image/png;base64,{base64_data})'


async def image_async(alt: str, href: str, convert_to_base64: bool = False) -> str:
    if not convert_to_base64 or href.startswith('data:'):
        return _generate_image_markup(alt, href)

    async with httpx.AsyncClient() as client:
        response = await client.get(href)
    base64_data = base64.b64encode(response.content).decode()
    return f'![{alt}](data:image/png;base64,{base64_data})'


def add_tab_space(text: str, n: int = 0) -> str:
    if n <= 0:
        return text

    tab = '\t'
    if '\n' in text:
        lines = text.split('\n')
        return '\n'.join(f'{tab * n}{line}' for line in lines)
    return f'{tab * n}{text}'


def divider() -> str:
    return '---'


def toggle(summary: Optional[str] = None, children: Optional[str] = None) -> str:
    if not summary:
        return children or ''
    result = f"- {summary}"
    if children:
        result += f"\n{add_tab_space(children, 1)}"
    return result


def table(cells: List[List[str]]) -> str:
    return MarkdownTableWriter(
        headers=cells[0],
        value_matrix=cells[1:],
        column_styles=[Style(align="left")],
        margin=1,
    ).dumps().strip('\n')
