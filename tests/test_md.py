import pytest
from notion_to_md.utils import md


def test_callout_without_emoji():
    text = "Call out text content."
    assert md.callout(text) == f"> {text}"


def test_callout_with_emoji():
    text = "Call out text content."
    assert md.callout(
        text,
        {
            "type": "emoji",
            "emoji": "😍",
        },
    ) == f"> 😍 {text}"


def test_markdown_table():
    mock_table = [
        ["number", "char"],
        ["1", "a"],
        ["2", "b"],
    ]
    expected_output = """
| number | char |
| ------ | ---- |
| 1      | a    |
| 2      | b    |
""".strip()
    assert md.table(mock_table) == expected_output


def test_inline_code():
    assert md.inline_code("simple text") == "`simple text`"


def test_code_block():
    expected_output = """
```javascript
simple text
```
""".strip()
    assert md.code_block("simple text", "javascript") == expected_output


def test_inline_equation():
    assert md.inline_equation("E = mc^2") == "$E = mc^2$"


def test_equation_block():
    expected_output = """
$$
E = mc^2
$$
""".strip()
    assert md.equation("E = mc^2") == expected_output


def test_bold():
    assert md.bold("simple text") == "**simple text**"


def test_italic():
    assert md.italic("simple text") == "_simple text_"


def test_strikethrough():
    assert md.strikethrough("simple text") == "~~simple text~~"


def test_underline():
    assert md.underline("simple text") == "<u>simple text</u>"


def test_heading1():
    assert md.heading1("simple text") == "# simple text"


def test_heading2():
    assert md.heading2("simple text") == "## simple text"


def test_heading3():
    assert md.heading3("simple text") == "### simple text"


def test_bullet():
    assert md.bullet("simple text") == "- simple text"


def test_checked_todo():
    assert md.todo("simple text", True) == "- [x] simple text"


def test_unchecked_todo():
    assert md.todo("simple text", False) == "- [ ] simple text"


@pytest.mark.asyncio
async def test_image_with_alt_text_async():
    result = await md.image_async("simple text", "https://example.com/image", False)
    assert result == "![simple text](https://example.com/image)"


def test_image_with_alt_text():
    result = md.image("simple text", "https://example.com/image", False)
    assert result == "![simple text](https://example.com/image)"


@pytest.mark.asyncio
async def test_image_to_base64_async():
    result = await md.image_async(
        "simple text", "https://w.wallhaven.cc/full/ex/wallhaven-ex9gwo.png", True
    )
    assert result.startswith(
        "![simple text](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAB4AAAAQ4CAY"
    )

def test_image_to_base64():
    result = md.image(
        "simple text", "https://w.wallhaven.cc/full/ex/wallhaven-ex9gwo.png", True
    )
    assert result.startswith(
        "![simple text](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAB4AAAAQ4CAY"
    )


def test_toggle_without_title():
    assert md.toggle(None, "content").replace(" ", "") == "content"


def test_toggle_empty_title_and_content():
    assert md.toggle(None, None).replace(" ", "") == ""


def test_toggle_with_title_and_content():
    result = md.toggle("title", "content")
    expected_output = "- title\n\tcontent"
    assert result == expected_output