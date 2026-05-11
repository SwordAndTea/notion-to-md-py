import pytest
from unittest.mock import MagicMock, AsyncMock
from notion_to_md import NotionToMarkdown, NotionToMarkdownAsync


def _make_paragraph_block(block_id: str, text: str, has_children: bool = False) -> dict:
    return {
        "id": block_id,
        "type": "paragraph",
        "has_children": has_children,
        "paragraph": {
            "rich_text": [{
                "type": "text",
                "plain_text": text,
                "annotations": {},
            }],
        },
    }


def _make_callout_block(block_id: str, text: str, has_children: bool = True) -> dict:
    return {
        "id": block_id,
        "type": "callout",
        "has_children": has_children,
        "callout": {
            "icon": None,
            "rich_text": [{
                "type": "text",
                "plain_text": text,
                "annotations": {},
            }],
        },
    }


def _make_synced_block(block_id: str, synced_from_id: str, has_children: bool = True) -> dict:
    return {
        "id": block_id,
        "type": "synced_block",
        "has_children": has_children,
        "synced_block": {
            "synced_from": {"block_id": synced_from_id} if synced_from_id else None,
        },
    }


def _children_response(blocks):
    return {"results": blocks, "next_cursor": None}


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


@pytest.mark.asyncio
async def test_block_list_to_markdown_with_parse_comments_enabled():
    mock_client = AsyncMock()
    mock_client.comments.list = AsyncMock()

    # Mock the comments list response
    mock_client.comments.list.return_value = {
        "results": [
            {
                "rich_text": [
                    {
                        "plain_text": "Great point!",
                        "annotations": {}
                    }
                ],
                "display_name": {
                    "resolved_name": "John Doe"
                }
            }
        ]
    }

    n2m = NotionToMarkdownAsync(notion_client=mock_client, config={"parse_comments": True})

    blocks = [
        {
            "id": "block-1",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "plain_text": "This is a paragraph",
                        "annotations": {}
                    }
                ]
            },
            "has_children": False
        }
    ]

    result = await n2m.block_list_to_markdown(blocks)

    # Verify comments.list was called with the block id
    mock_client.comments.list.assert_called_once_with(block_id="block-1")

    # Verify the result includes both the block content and comments
    assert "This is a paragraph" in result[0]["parent"]
    assert "Comments:" in result[0]["parent"]
    assert "**John Doe**: Great point!" in result[0]["parent"]


@pytest.mark.asyncio
async def test_block_list_to_markdown_with_parse_comments_disabled():
    mock_client = AsyncMock()
    mock_client.comments.list = AsyncMock()

    n2m = NotionToMarkdownAsync(notion_client=mock_client, config={"parse_comments": False})

    blocks = [
        {
            "id": "block-1",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "plain_text": "This is a paragraph",
                        "annotations": {}
                    }
                ]
            },
            "has_children": False
        }
    ]

    result = await n2m.block_list_to_markdown(blocks)

    # Verify comments.list was NOT called when parse_comments is False
    mock_client.comments.list.assert_not_called()

    # Verify the result includes only the block content, no comments
    assert "This is a paragraph" in result[0]["parent"]
    assert "Comments:" not in result[0]["parent"]


@pytest.mark.asyncio
async def test_block_list_to_markdown_with_multiple_comments():
    mock_client = AsyncMock()
    mock_client.comments.list = AsyncMock()

    # Mock multiple comments
    mock_client.comments.list.return_value = {
        "results": [
            {
                "rich_text": [
                    {
                        "plain_text": "First comment",
                        "annotations": {}
                    }
                ],
                "display_name": {
                    "resolved_name": "Alice"
                }
            },
            {
                "rich_text": [
                    {
                        "plain_text": "Second comment",
                        "annotations": {}
                    }
                ],
                "display_name": {
                    "resolved_name": "Bob"
                }
            }
        ]
    }

    n2m = NotionToMarkdownAsync(notion_client=mock_client, config={"parse_comments": True})

    blocks = [
        {
            "id": "block-1",
            "type": "heading_1",
            "heading_1": {
                "rich_text": [
                    {
                        "plain_text": "Important Heading",
                        "annotations": {}
                    }
                ]
            },
            "has_children": False
        }
    ]

    result = await n2m.block_list_to_markdown(blocks)

    # Verify both comments are included
    assert "Comments:" in result[0]["parent"]
    assert "**Alice**: First comment" in result[0]["parent"]
    assert "**Bob**: Second comment" in result[0]["parent"]


@pytest.mark.asyncio
async def test_block_list_to_markdown_with_no_comments():
    mock_client = AsyncMock()
    mock_client.comments.list = AsyncMock()

    # Mock empty comments response
    mock_client.comments.list.return_value = {
        "results": []
    }

    n2m = NotionToMarkdownAsync(notion_client=mock_client, config={"parse_comments": True})

    blocks = [
        {
            "id": "block-1",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "plain_text": "No comments here",
                        "annotations": {}
                    }
                ]
            },
            "has_children": False
        }
    ]

    result = await n2m.block_list_to_markdown(blocks)

    # Verify comments.list was called
    mock_client.comments.list.assert_called_once_with(block_id="block-1")

    # Verify "Comments:" section is NOT added when there are no comments
    assert "No comments here" in result[0]["parent"]
    assert "Comments:" not in result[0]["parent"]


@pytest.mark.asyncio
async def test_block_list_to_markdown_with_comments_on_different_block_types():
    mock_client = AsyncMock()

    # Set up different responses for different blocks
    def comments_side_effect(block_id):
        if block_id == "block-1":
            return {
                "results": [
                    {
                        "rich_text": [{"plain_text": "Comment on code", "annotations": {}}],
                        "display_name": {"resolved_name": "Reviewer"}
                    }
                ]
            }
        return {"results": []}

    mock_client.comments.list = AsyncMock(side_effect=comments_side_effect)

    n2m = NotionToMarkdownAsync(notion_client=mock_client, config={"parse_comments": True})

    blocks = [
        {
            "id": "block-1",
            "type": "code",
            "code": {
                "rich_text": [{"plain_text": "print('hello')", "annotations": {}}],
                "language": "python"
            },
            "has_children": False
        },
        {
            "id": "block-2",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"plain_text": "Regular text", "annotations": {}}]
            },
            "has_children": False
        }
    ]

    result = await n2m.block_list_to_markdown(blocks)

    # Verify comments were checked for both blocks
    assert mock_client.comments.list.call_count == 2

    # Verify comment appears only on the code block
    assert "**Reviewer**: Comment on code" in result[0]["parent"]
    assert "Comments:" not in result[1]["parent"]


@pytest.mark.asyncio
async def test_block_list_to_markdown_with_comments_containing_annotations():
    mock_client = AsyncMock()
    mock_client.comments.list = AsyncMock()

    # Mock comment with bold and link
    mock_client.comments.list.return_value = {
        "results": [
            {
                "rich_text": [
                    {
                        "plain_text": "Check ",
                        "annotations": {}
                    },
                    {
                        "plain_text": "this link",
                        "annotations": {"bold": True},
                        "href": "https://example.com"
                    }
                ],
                "display_name": {
                    "resolved_name": "Sarah"
                }
            }
        ]
    }

    n2m = NotionToMarkdownAsync(notion_client=mock_client, config={"parse_comments": True})

    blocks = [
        {
            "id": "block-1",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"plain_text": "Content", "annotations": {}}]
            },
            "has_children": False
        }
    ]

    result = await n2m.block_list_to_markdown(blocks)

    # Verify comment with formatting is correctly parsed
    assert "**Sarah**: Check [**this link**](https://example.com)" in result[0]["parent"]


def test_block_list_to_markdown_breaks_circular_references():
    block_a = _make_paragraph_block("A", "block A", has_children=True)
    block_b = _make_paragraph_block("B", "block B", has_children=True)

    children_by_id = {
        "A": _children_response([block_b]),
        "B": _children_response([block_a]),
    }

    notion_client = MagicMock()
    notion_client.blocks.children.list.side_effect = lambda block_id, start_cursor=None: (
        children_by_id[block_id]
    )

    n2m = NotionToMarkdown(notion_client=notion_client)

    result = n2m.block_list_to_markdown([block_a])

    assert len(result) == 1
    assert result[0]["block_id"] == "A"
    assert len(result[0]["children"]) == 1
    assert result[0]["children"][0]["block_id"] == "B"
    # B's child is A again — appended as a leaf since A is on the recursion path
    assert len(result[0]["children"][0]["children"]) == 1
    assert result[0]["children"][0]["children"][0]["block_id"] == "A"
    assert result[0]["children"][0]["children"][0]["children"] == []


def test_block_list_to_markdown_self_referential_block():
    block_self = _make_paragraph_block("S", "loop", has_children=True)

    notion_client = MagicMock()
    notion_client.blocks.children.list.return_value = _children_response([block_self])

    n2m = NotionToMarkdown(notion_client=notion_client)

    result = n2m.block_list_to_markdown([block_self])

    assert len(result) == 1
    assert result[0]["block_id"] == "S"
    assert len(result[0]["children"]) == 1
    assert result[0]["children"][0]["block_id"] == "S"
    assert result[0]["children"][0]["children"] == []


def test_block_list_to_markdown_visits_same_block_in_separate_branches():
    """A block legitimately reachable twice via different branches should be
    processed in each branch — only ancestor cycles are skipped."""
    shared = _make_paragraph_block("shared", "shared", has_children=True)
    leaf = _make_paragraph_block("leaf", "leaf", has_children=False)
    parent_one = _make_paragraph_block("P1", "p1", has_children=True)
    parent_two = _make_paragraph_block("P2", "p2", has_children=True)

    children_by_id = {
        "P1": _children_response([shared]),
        "P2": _children_response([shared]),
        "shared": _children_response([leaf]),
    }

    notion_client = MagicMock()
    notion_client.blocks.children.list.side_effect = lambda block_id, start_cursor=None: (
        children_by_id[block_id]
    )

    n2m = NotionToMarkdown(notion_client=notion_client)

    result = n2m.block_list_to_markdown([parent_one, parent_two])

    assert len(result) == 2
    assert result[0]["children"][0]["block_id"] == "shared"
    assert result[0]["children"][0]["children"][0]["block_id"] == "leaf"
    assert result[1]["children"][0]["block_id"] == "shared"
    assert result[1]["children"][0]["children"][0]["block_id"] == "leaf"


def test_block_list_to_markdown_breaks_nested_callout_cycle():
    """Cycle across two callouts via a synced_block:
    C1 (callout) > C2 (callout) > S (synced_block, synced_from=C1) > fetches C1's children -> C2 again.
    Without threading visited_ids through block_to_markdown's callout case, this loops forever
    because each callout starts a fresh visited set.
    """
    c1 = _make_callout_block("C1", "outer")
    c2 = _make_callout_block("C2", "inner")
    synced = _make_synced_block("S", synced_from_id="C1")

    children_by_id = {
        "C1": _children_response([c2]),
        "C2": _children_response([synced]),
    }

    notion_client = MagicMock()
    notion_client.blocks.children.list.side_effect = lambda block_id, start_cursor=None: (
        children_by_id[block_id]
    )

    n2m = NotionToMarkdown(notion_client=notion_client)

    result = n2m.block_list_to_markdown([c1])

    assert len(result) == 1
    assert result[0]["block_id"] == "C1"


def test_block_to_markdown_callout_self_reference():
    """A callout whose own child syncs from itself — block_to_markdown's callout case
    must propagate visited_ids so the inner block_list_to_markdown detects the cycle."""
    c = _make_callout_block("C", "self")
    synced = _make_synced_block("S", synced_from_id="C")

    notion_client = MagicMock()
    notion_client.blocks.children.list.return_value = _children_response([synced])

    n2m = NotionToMarkdown(notion_client=notion_client)
    md_str = n2m.block_to_markdown(c)

    assert isinstance(md_str, str)
    assert "self" in md_str


@pytest.mark.asyncio
async def test_block_list_to_markdown_breaks_nested_callout_cycle_async():
    c1 = _make_callout_block("C1", "outer")
    c2 = _make_callout_block("C2", "inner")
    synced = _make_synced_block("S", synced_from_id="C1")

    children_by_id = {
        "C1": _children_response([c2]),
        "C2": _children_response([synced]),
    }

    async def fake_list(block_id, start_cursor=None):
        return children_by_id[block_id]

    notion_client = MagicMock()
    notion_client.blocks.children.list = AsyncMock(side_effect=fake_list)

    n2m = NotionToMarkdownAsync(notion_client=notion_client)

    result = await n2m.block_list_to_markdown([c1])

    assert len(result) == 1
    assert result[0]["block_id"] == "C1"


@pytest.mark.asyncio
async def test_block_list_to_markdown_breaks_circular_references_async():
    block_a = _make_paragraph_block("A", "block A", has_children=True)
    block_b = _make_paragraph_block("B", "block B", has_children=True)

    children_by_id = {
        "A": _children_response([block_b]),
        "B": _children_response([block_a]),
    }

    async def fake_list(block_id, start_cursor=None):
        return children_by_id[block_id]

    notion_client = MagicMock()
    notion_client.blocks.children.list = AsyncMock(side_effect=fake_list)

    n2m = NotionToMarkdownAsync(notion_client=notion_client)

    result = await n2m.block_list_to_markdown([block_a])

    assert len(result) == 1
    assert result[0]["block_id"] == "A"
    assert len(result[0]["children"]) == 1
    assert result[0]["children"][0]["block_id"] == "B"
    assert len(result[0]["children"][0]["children"]) == 1
    assert result[0]["children"][0]["children"][0]["block_id"] == "A"
    assert result[0]["children"][0]["children"][0]["children"] == []
