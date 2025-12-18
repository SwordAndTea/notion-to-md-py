import pytest
from unittest.mock import MagicMock, AsyncMock
from notion_to_md import NotionToMarkdown, NotionToMarkdownAsync


def test_block_to_markdown_calls_custom_transformer():
    custom_transformer_mock = MagicMock()
    n2m = NotionToMarkdown(notion_client={})
    n2m.set_custom_transformer("test", custom_transformer_mock)

    n2m.block_to_markdown({
        "id": "test",
        "name": "test",
        "type": "test",
        "test": {"foo": "bar"},
    })

    custom_transformer_mock.assert_called_once_with({
        "id": "test",
        "name": "test",
        "type": "test",
        "test": {"foo": "bar"}
    })


def test_supports_only_one_custom_transformer_per_type():
    custom_transformer_mock1 = MagicMock()
    custom_transformer_mock2 = MagicMock()
    n2m = NotionToMarkdown(notion_client={})

    # Set two transformers for the same type
    n2m.set_custom_transformer("test", custom_transformer_mock1)
    n2m.set_custom_transformer("test", custom_transformer_mock2)

    n2m.block_to_markdown({
        "id": "test",
        "name": "test",
        "type": "test",
        "test": {"foo": "bar"},
    })

    custom_transformer_mock1.assert_not_called()
    custom_transformer_mock2.assert_called_once()


def test_custom_transformer_implementation_works():
    custom_transformer_mock = MagicMock()
    custom_transformer_mock.return_value = "hello"
    n2m = NotionToMarkdown(notion_client={})
    n2m.set_custom_transformer("divider", custom_transformer_mock)

    md = n2m.block_to_markdown({
        "id": "test",
        "type": "divider",
        "divider": {},
        "object": "block",
    })

    assert md == "hello"


def test_custom_transformer_default_implementation_works():
    custom_transformer_mock = MagicMock()
    custom_transformer_mock.return_value = False
    n2m = NotionToMarkdown(notion_client={})
    n2m.set_custom_transformer("divider", custom_transformer_mock)

    md = n2m.block_to_markdown({
        "id": "test",
        "type": "divider",
        "divider": {},
        "object": "block",
    })

    assert md == "---"


@pytest.mark.asyncio
async def test_block_to_markdown_calls_custom_transformer_async():
    custom_transformer_mock = AsyncMock()
    n2m = NotionToMarkdownAsync(notion_client={})
    n2m.set_custom_transformer("test", custom_transformer_mock)

    await n2m.block_to_markdown({
        "id": "test",
        "name": "test",
        "type": "test",
        "test": {"foo": "bar"},
    })

    custom_transformer_mock.assert_called_once_with({
        "id": "test",
        "name": "test",
        "type": "test",
        "test": {"foo": "bar"}
    })


@pytest.mark.asyncio
async def test_supports_only_one_custom_transformer_per_type_async():
    custom_transformer_mock1 = AsyncMock()
    custom_transformer_mock2 = AsyncMock()
    n2m = NotionToMarkdownAsync(notion_client={})

    # Set two transformers for the same type
    n2m.set_custom_transformer("test", custom_transformer_mock1)
    n2m.set_custom_transformer("test", custom_transformer_mock2)

    await n2m.block_to_markdown({
        "id": "test",
        "name": "test",
        "type": "test",
        "test": {"foo": "bar"},
    })

    custom_transformer_mock1.assert_not_called()
    custom_transformer_mock2.assert_called_once()


@pytest.mark.asyncio
async def test_custom_transformer_implementation_works_async():
    custom_transformer_mock = AsyncMock()
    custom_transformer_mock.return_value = "hello"
    n2m = NotionToMarkdownAsync(notion_client={})
    n2m.set_custom_transformer("divider", custom_transformer_mock)

    md = await n2m.block_to_markdown({
        "id": "test",
        "type": "divider",
        "divider": {},
        "object": "block",
    })

    assert md == "hello"


@pytest.mark.asyncio
async def test_custom_transformer_default_implementation_works_async():
    custom_transformer_mock = AsyncMock()
    custom_transformer_mock.return_value = False
    n2m = NotionToMarkdownAsync(notion_client={})
    n2m.set_custom_transformer("divider", custom_transformer_mock)

    md = await n2m.block_to_markdown({
        "id": "test",
        "type": "divider",
        "divider": {},
        "object": "block",
    })

    assert md == "---"


@pytest.mark.asyncio
async def test_comment_to_markdown_with_simple_text():
    n2m = NotionToMarkdownAsync(notion_client={})

    comment = {
        "rich_text": [
            {
                "plain_text": "This is a simple comment",
                "annotations": {}
            }
        ],
        "display_name": {
            "resolved_name": "John Doe"
        }
    }

    result = await n2m.comment_to_markdown(comment)
    assert result == "**John Doe**: This is a simple comment\n"


@pytest.mark.asyncio
async def test_comment_to_markdown_with_bold_text():
    n2m = NotionToMarkdownAsync(notion_client={})

    comment = {
        "rich_text": [
            {
                "plain_text": "bold text",
                "annotations": {"bold": True}
            }
        ],
        "display_name": {
            "resolved_name": "Jane Smith"
        }
    }

    result = await n2m.comment_to_markdown(comment)
    assert result == "**Jane Smith**: **bold text**\n"


@pytest.mark.asyncio
async def test_comment_to_markdown_with_italic_text():
    n2m = NotionToMarkdownAsync(notion_client={})

    comment = {
        "rich_text": [
            {
                "plain_text": "italic text",
                "annotations": {"italic": True}
            }
        ],
        "display_name": {
            "resolved_name": "Bob Johnson"
        }
    }

    result = await n2m.comment_to_markdown(comment)
    assert result == "**Bob Johnson**: _italic text_\n"


@pytest.mark.asyncio
async def test_comment_to_markdown_with_code():
    n2m = NotionToMarkdownAsync(notion_client={})

    comment = {
        "rich_text": [
            {
                "plain_text": "console.log('hello')",
                "annotations": {"code": True}
            }
        ],
        "display_name": {
            "resolved_name": "Alice Cooper"
        }
    }

    result = await n2m.comment_to_markdown(comment)
    assert result == "**Alice Cooper**: `console.log('hello')`\n"


@pytest.mark.asyncio
async def test_comment_to_markdown_with_link():
    n2m = NotionToMarkdownAsync(notion_client={})

    comment = {
        "rich_text": [
            {
                "plain_text": "Click here",
                "annotations": {},
                "href": "https://example.com"
            }
        ],
        "display_name": {
            "resolved_name": "David Lee"
        }
    }

    result = await n2m.comment_to_markdown(comment)
    assert result == "**David Lee**: [Click here](https://example.com)\n"


@pytest.mark.asyncio
async def test_comment_to_markdown_with_multiple_parts():
    n2m = NotionToMarkdownAsync(notion_client={})

    comment = {
        "rich_text": [
            {
                "plain_text": "This is ",
                "annotations": {}
            },
            {
                "plain_text": "bold",
                "annotations": {"bold": True}
            },
            {
                "plain_text": " and ",
                "annotations": {}
            },
            {
                "plain_text": "italic",
                "annotations": {"italic": True}
            }
        ],
        "display_name": {
            "resolved_name": "Emma Wilson"
        }
    }

    result = await n2m.comment_to_markdown(comment)
    assert result == "**Emma Wilson**: This is **bold** and _italic_\n"


@pytest.mark.asyncio
async def test_comment_to_markdown_with_anonymous_user():
    n2m = NotionToMarkdownAsync(notion_client={})

    comment = {
        "rich_text": [
            {
                "plain_text": "Anonymous comment",
                "annotations": {}
            }
        ],
        "display_name": {}
    }

    result = await n2m.comment_to_markdown(comment)
    assert result == "**Anonymous**: Anonymous comment\n"


@pytest.mark.asyncio
async def test_comment_to_markdown_with_empty_rich_text():
    n2m = NotionToMarkdownAsync(notion_client={})

    comment = {
        "rich_text": [],
        "display_name": {
            "resolved_name": "Test User"
        }
    }

    result = await n2m.comment_to_markdown(comment)
    assert result == "**Test User**: \n"


@pytest.mark.asyncio
async def test_comment_to_markdown_with_invalid_input():
    n2m = NotionToMarkdownAsync(notion_client={})

    # Test with non-dict input
    result = await n2m.comment_to_markdown("invalid")
    assert result == ""

    # Test with dict missing rich_text
    result = await n2m.comment_to_markdown({"display_name": {"resolved_name": "Test"}})
    assert result == ""


@pytest.mark.asyncio
async def test_comment_to_markdown_with_strikethrough():
    n2m = NotionToMarkdownAsync(notion_client={})

    comment = {
        "rich_text": [
            {
                "plain_text": "strikethrough text",
                "annotations": {"strikethrough": True}
            }
        ],
        "display_name": {
            "resolved_name": "Mike Brown"
        }
    }

    result = await n2m.comment_to_markdown(comment)
    assert result == "**Mike Brown**: ~~strikethrough text~~\n"


@pytest.mark.asyncio
async def test_comment_to_markdown_with_underline():
    n2m = NotionToMarkdownAsync(notion_client={})

    comment = {
        "rich_text": [
            {
                "plain_text": "underlined text",
                "annotations": {"underline": True}
            }
        ],
        "display_name": {
            "resolved_name": "Sarah Davis"
        }
    }

    result = await n2m.comment_to_markdown(comment)
    assert result == "**Sarah Davis**: <u>underlined text</u>\n"


@pytest.mark.asyncio
async def test_comment_to_markdown_with_mixed_annotations():
    n2m = NotionToMarkdownAsync(notion_client={})

    comment = {
        "rich_text": [
            {
                "plain_text": "bold and italic",
                "annotations": {"bold": True, "italic": True}
            }
        ],
        "display_name": {
            "resolved_name": "Chris Evans"
        }
    }

    result = await n2m.comment_to_markdown(comment)
    assert result == "**Chris Evans**: _**bold and italic**_\n"

