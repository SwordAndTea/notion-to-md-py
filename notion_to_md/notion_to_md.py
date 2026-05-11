import re
from typing import Dict, List, Optional, Union
from notion_client import Client, AsyncClient
from notion_to_md.utils import md
from notion_to_md.utils.notion import get_block_children, get_block_children_async


class NotionToMarkdownBase:
    def __init__(self, notion_client: Union[Client, AsyncClient], config: Dict = None):
        if notion_client is None:
            raise ValueError("Notion client is not provided")
        self.notion_client = notion_client
        default_config = {
            "separate_child_page": False,
            "convert_images_to_base64": False,
            "parse_child_pages": True,
            "parse_comments": False,
        }
        self.config = {**default_config, **(config or {})}
        self.custom_transformers = {}

    def set_custom_transformer(self, block_type: str, transformer_func):
        """Set a custom transformer for a specific block type"""
        self.custom_transformers[block_type] = transformer_func
        return self

    def to_markdown_string(self, md_blocks: List[Dict] = None,
                           page_identifier: str = "parent",
                           nesting_level: int = 0) -> Dict[str, str]:
        """Convert markdown blocks to string"""
        md_output = {}
        if not md_blocks:
            return md_output

        for block in md_blocks:
            # Handle parent blocks
            if block.get('parent') and block.get('type') not in ['toggle', 'child_page']:
                if block.get('type') not in ['to_do', 'bulleted_list_item',
                                             'numbered_list_item', 'quote']:
                    md_output[page_identifier] = md_output.get(page_identifier, '')
                    md_output[page_identifier] += f"\n{md.add_tab_space(block['parent'], nesting_level)}\n\n"
                else:
                    md_output[page_identifier] = md_output.get(page_identifier, '')
                    md_output[page_identifier] += f"{md.add_tab_space(block['parent'], nesting_level)}\n"

            # Handle children blocks
            if block.get('children'):
                if block['type'] in ['synced_block', 'column_list', 'column']:
                    md_str = self.to_markdown_string(block['children'], page_identifier)
                    md_output[page_identifier] = md_output.get(page_identifier, '')

                    for key, value in md_str.items():
                        md_output[key] = md_output.get(key, '') + value

                elif block['type'] == 'child_page':
                    child_page_title = block['parent']
                    md_str = self.to_markdown_string(block['children'], child_page_title)

                    if self.config['separate_child_page']:
                        md_output.update(md_str)
                    else:
                        md_output[page_identifier] = md_output.get(page_identifier, '')
                        if md_str.get(child_page_title):
                            md_output[page_identifier] += f"\n{child_page_title}\n{md_str[child_page_title]}"

                elif block['type'] == 'toggle':
                    toggle_children_md = self.to_markdown_string(block['children'])
                    md_output[page_identifier] = md_output.get(page_identifier, '')
                    md_output[page_identifier] += md.toggle(block['parent'],
                                                            toggle_children_md.get('parent', ''))

                else:
                    md_str = self.to_markdown_string(block['children'],
                                                     page_identifier,
                                                     nesting_level + 1)
                    md_output[page_identifier] = md_output.get(page_identifier, '')

                    if page_identifier != 'parent' and md_str.get('parent'):
                        md_output[page_identifier] += md_str['parent']
                    elif md_str.get(page_identifier):
                        md_output[page_identifier] += md_str[page_identifier]

        return md_output

    def _apply_annotations(self, plain_text: str, annotations: Dict[str, bool]) -> str:
        if re.match(r'^\s*$', plain_text):
            return plain_text

        leading_space_match = re.match(r'^(\s*)', plain_text)
        trailing_space_match = re.search(r'(\s*)$', plain_text)

        leading_space = leading_space_match.group(0) if leading_space_match else ""
        trailing_space = trailing_space_match.group(0) if trailing_space_match else ""

        plain_text = plain_text.strip()

        if plain_text:
            """Apply annotations to plain text"""
            if annotations.get('code'):
                plain_text = md.inline_code(plain_text)
            if annotations.get('bold'):
                plain_text = md.bold(plain_text)
            if annotations.get('italic'):
                plain_text = md.italic(plain_text)
            if annotations.get('strikethrough'):
                plain_text = md.strikethrough(plain_text)
            if annotations.get('underline'):
                plain_text = md.underline(plain_text)

        return leading_space + plain_text + trailing_space


class NotionToMarkdown(NotionToMarkdownBase):
    def __init__(self, notion_client: Client, config: Dict = None):
        super().__init__(notion_client, config)

    def page_to_markdown(self, page_id: str, total_pages: Optional[int] = None) -> List[Dict]:
        """Convert a Notion page to markdown blocks"""
        blocks = get_block_children(self.notion_client, page_id, total_pages)
        parsed_data = self.block_list_to_markdown(blocks)
        return parsed_data

    def block_list_to_markdown(self, blocks: List[Dict] = None,
                               total_pages: Optional[int] = None,
                               md_blocks: List[Dict] = None,
                               _visited_block_ids: Optional[set] = None) -> List[Dict]:
        """Convert Notion blocks to markdown blocks"""
        if md_blocks is None:
            md_blocks = []
        if _visited_block_ids is None:
            _visited_block_ids = set()
        if not blocks:
            return md_blocks

        for block in blocks:
            if (block['type'] == 'unsupported' or
                    (block['type'] == 'child_page' and not self.config['parse_child_pages'])):
                continue

            if block.get('has_children'):
                block_id = (block['synced_block']['synced_from']['block_id']
                            if block['type'] == 'synced_block' and
                               block['synced_block'].get('synced_from')
                            else block['id'])

                if block_id in _visited_block_ids:
                    md_blocks.append({
                        'type': block['type'],
                        'block_id': block['id'],
                        'parent': self.block_to_markdown(block, _visited_block_ids),
                        'children': []
                    })
                    continue

                child_blocks = get_block_children(self.notion_client,
                                                  block_id,
                                                  total_pages)

                md_blocks.append({
                    'type': block['type'],
                    'block_id': block['id'],
                    'parent': self.block_to_markdown(block, _visited_block_ids),
                    'children': []
                })

                if not (block['type'] in self.custom_transformers):
                    _visited_block_ids.add(block_id)
                    try:
                        self.block_list_to_markdown(
                            child_blocks,
                            total_pages,
                            md_blocks[-1]['children'],
                            _visited_block_ids)
                    finally:
                        _visited_block_ids.discard(block_id)
                continue

            md_blocks.append({
                'type': block['type'],
                'block_id': block['id'],
                'parent': self.block_to_markdown(block, _visited_block_ids),
                'children': []
            })

        return md_blocks

    def block_to_markdown(self, block: Dict, _visited_block_ids: Optional[set] = None) -> str:
        """Convert a single Notion block to markdown"""
        if not isinstance(block, dict) or 'type' not in block:
            return ""

        if _visited_block_ids is None:
            _visited_block_ids = set()

        block_type = block['type']
        parsed_data = ""

        # Check for custom transformer
        if block_type in self.custom_transformers:
            result = self.custom_transformers[block_type](block)
            if isinstance(result, str):
                return result

        # Handle different block types
        if block_type == "image":
            block_content = block['image']
            image_title = "image"

            image_caption_plain = "".join(
                item.get('plain_text', '')
                for item in block_content.get('caption', [])
            )

            image_type = block_content['type']
            link = (block_content['external']['url']
                    if image_type == 'external'
                    else block_content['file']['url'])

            image_title = (image_caption_plain.strip() or
                           (link.split('/')[-1] if '/' in link else image_title))

            return md.image(image_title, link, self.config['convert_images_to_base64'])

        elif block_type == "divider":
            return md.divider()

        elif block_type == "equation":
            return md.equation(block['equation']['expression'])

        elif block_type in ["video", "file", "pdf"]:
            block_content = block.get(block_type)
            title = block_type

            if block_content:
                caption = "".join(
                    item.get('plain_text', '')
                    for item in block_content.get('caption', [])
                )

                file_type = block_content['type']
                link = (block_content['external']['url']
                        if file_type == 'external'
                        else block_content['file']['url'])

                title = caption.strip() or (link.split('/')[-1] if '/' in link else title)
                return md.link(title, link)


        elif block_type in ["bookmark", "embed", "link_preview", "link_to_page"]:
            if block_type == "link_to_page" and block[block_type].get('type') == "page_id":
                block_content = {
                    "url": f"https://www.notion.so/{block[block_type]['page_id']}"
                }
            elif block_type == "link_to_page" and block[block_type].get('type') == "database_id":
                block_content = {
                    "url": f"https://www.notion.so/{block[block_type]['database_id']}"
                }
            else:
                block_content = block[block_type]
            url = block_content.get('url', '')
            return md.link(block_type, url)

        elif block_type == "child_page":
            if not self.config["parse_child_pages"]:
                return ""

            page_title = block["child_page"]["title"]

            if self.config["separate_child_page"]:
                return page_title

            return md.heading2(page_title)

        elif block_type == "child_database":
            page_title = block["child_database"].get("title", "child_database")
            return md.heading2(page_title)

        elif block_type == "table":
            table_rows = []

            # Check if the table has children
            if block.get("has_children"):
                table_children = get_block_children(self.notion_client, block["id"])
                for child in table_children:
                    if child["type"] == "table_row":
                        cells = child["table_row"].get("cells", [])

                        # Convert each cell content to paragraphs and reuse block_to_markdown
                        row_content = [
                            self.block_to_markdown({
                                "type": "paragraph",
                                "paragraph": {"rich_text": cell},
                            })
                            for cell in cells
                        ]
                        table_rows.append(row_content)

            return md.table(table_rows)

        else:
            # Rest of the types
            # "paragraph"
            # "heading_1"
            # "heading_2"
            # "heading_3"
            # "bulleted_list_item"
            # "numbered_list_item"
            # "quote"
            # "to_do"
            # "template"
            # "synced_block"
            # "child_page"
            # "child_database"
            # "code"
            # "callout"
            # "breadcrumb"
            # "table_of_contents"
            # "link_to_page"
            # "audio"
            # "unsupported"

            block_data = block.get(block_type, {})
            block_content = block_data.get("text", [])
            if not block_content:
                block_content = block_data.get("rich_text", [])

            for content in block_content:
                if content.get("type") == "equation":
                    parsed_data += md.inline_equation(content["equation"]["expression"])
                    continue

                plain_text = content.get("plain_text", "")
                annotations = content.get("annotations", {})

                # Apply annotations to plain_text
                plain_text = self._apply_annotations(plain_text, annotations)

                # Add link if present
                if content.get("href"):
                    plain_text = md.link(plain_text, content["href"])

                parsed_data += plain_text

        if block_type == "code":
            return md.code_block(parsed_data, block['code']['language'])

        elif block_type == "heading_1":
            return md.heading1(parsed_data)

        elif block_type == "heading_2":
            return md.heading2(parsed_data)

        elif block_type == "heading_3":
            return md.heading3(parsed_data)

        elif block_type == "quote":
            return md.quote(parsed_data)

        elif block_type == "callout":
            callout_string = ""
            if not block['has_children']:
                return md.callout(parsed_data, block['callout'].get('icon'))

            if block['id'] in _visited_block_ids:
                return md.callout(parsed_data, block['callout'].get('icon'))

            callout_children_object = get_block_children(self.notion_client, block['id'], 100)
            _visited_block_ids.add(block['id'])
            try:
                callout_children = self.block_list_to_markdown(
                    callout_children_object,
                    _visited_block_ids=_visited_block_ids)
            finally:
                _visited_block_ids.discard(block['id'])

            callout_string += f"{parsed_data}\n"
            for child in callout_children:
                callout_string += f"{child['parent']}\n\n"

            return md.callout(callout_string.strip(), block['callout'].get('icon'))

        elif block_type == "bulleted_list_item":
            return md.bullet(parsed_data)

        elif block_type == "numbered_list_item":
            return md.bullet(
                parsed_data,
                block['numbered_list_item'].get('number')
            )
        elif block_type == "to_do":
            return md.todo(
                parsed_data,
                block['to_do']['checked']
            )

        return parsed_data


class NotionToMarkdownAsync(NotionToMarkdownBase):
    def __init__(self, notion_client: AsyncClient, config: Dict = None):
        super().__init__(notion_client, config)

    async def page_to_markdown(self, page_id: str, total_pages: Optional[int] = None) -> List[Dict]:
        """Convert a Notion page to markdown blocks"""
        blocks = await get_block_children_async(self.notion_client, page_id, total_pages)
        parsed_data = await self.block_list_to_markdown(blocks)
        return parsed_data

    async def block_list_to_markdown(self, blocks: List[Dict] = None,
                                     total_pages: Optional[int] = None,
                                     md_blocks: List[Dict] = None,
                                     _visited_block_ids: Optional[set] = None) -> List[Dict]:
        """Convert Notion blocks to markdown blocks"""
        if md_blocks is None:
            md_blocks = []
        if _visited_block_ids is None:
            _visited_block_ids = set()
        if not blocks:
            return md_blocks

        for block in blocks:
            if (block['type'] == 'unsupported' or
                    (block['type'] == 'child_page' and not self.config['parse_child_pages'])):
                continue

            content = await self.block_to_markdown(block, _visited_block_ids)
            if self.config['parse_comments']:
                comments = (await self.notion_client.comments.list(block_id=block['id'])).get('results', [])
                if comments:
                    content += "\n\nComments:\n"
                    for c in comments:
                        content += await self.comment_to_markdown(c) + "\n"

            if block.get('has_children'):
                block_id = (block['synced_block']['synced_from']['block_id']
                            if block['type'] == 'synced_block' and
                               block['synced_block'].get('synced_from')
                            else block['id'])

                if block_id in _visited_block_ids:
                    md_blocks.append({
                        'type': block['type'],
                        'block_id': block['id'],
                        'parent': content,
                        'children': []
                    })
                    continue

                child_blocks = await get_block_children_async(self.notion_client,
                                                              block_id,
                                                              total_pages)

                md_blocks.append({
                    'type': block['type'],
                    'block_id': block['id'],
                    'parent': content,
                    'children': []
                })

                if not (block['type'] in self.custom_transformers):
                    _visited_block_ids.add(block_id)
                    try:
                        await self.block_list_to_markdown(child_blocks,
                                                          total_pages,
                                                          md_blocks[-1]['children'],
                                                          _visited_block_ids)
                    finally:
                        _visited_block_ids.discard(block_id)
                continue

            md_blocks.append({
                'type': block['type'],
                'block_id': block['id'],
                'parent': content,
                'children': []
            })

        return md_blocks

    async def block_to_markdown(self, block: Dict, _visited_block_ids: Optional[set] = None) -> str:
        """Convert a single Notion block to markdown"""
        if not isinstance(block, dict) or 'type' not in block:
            return ""

        if _visited_block_ids is None:
            _visited_block_ids = set()

        block_type = block['type']
        parsed_data = ""

        # Check for custom transformer
        if block_type in self.custom_transformers:
            result = await self.custom_transformers[block_type](block)
            if isinstance(result, str):
                return result

        # Handle different block types
        if block_type == "image":
            block_content = block['image']
            image_title = "image"

            image_caption_plain = "".join(
                item.get('plain_text', '')
                for item in block_content.get('caption', [])
            )

            image_type = block_content['type']
            link = (block_content['external']['url']
                    if image_type == 'external'
                    else block_content['file']['url'])

            image_title = (image_caption_plain.strip() or
                           (link.split('/')[-1] if '/' in link else image_title))

            return await md.image_async(image_title, link, self.config['convert_images_to_base64'])

        elif block_type == "divider":
            return md.divider()

        elif block_type == "equation":
            return md.equation(block['equation']['expression'])

        elif block_type in ["video", "file", "pdf"]:
            block_content = block.get(block_type)
            title = block_type

            if block_content:
                caption = "".join(
                    item.get('plain_text', '')
                    for item in block_content.get('caption', [])
                )

                file_type = block_content['type']
                link = (block_content['external']['url']
                        if file_type == 'external'
                        else block_content['file']['url'])

                title = caption.strip() or (link.split('/')[-1] if '/' in link else title)
                return md.link(title, link)


        elif block_type in ["bookmark", "embed", "link_preview", "link_to_page"]:
            if block_type == "link_to_page" and block[block_type].get('type') == "page_id":
                block_content = {
                    "url": f"https://www.notion.so/{block[block_type]['page_id']}"
                }
            elif block_type == "link_to_page" and block[block_type].get('type') == "database_id":
                block_content = {
                    "url": f"https://www.notion.so/{block[block_type]['database_id']}"
                }
            else:
                block_content = block[block_type]
            url = block_content.get('url', '')
            return md.link(block_type, url)

        elif block_type == "child_page":
            if not self.config["parse_child_pages"]:
                return ""

            page_title = block["child_page"]["title"]

            if self.config["separate_child_page"]:
                return page_title

            return md.heading2(page_title)

        elif block_type == "child_database":
            page_title = block["child_database"].get("title", "child_database")
            return md.heading2(page_title)

        elif block_type == "table":
            table_rows = []

            # Check if the table has children
            if block.get("has_children"):
                table_children = await get_block_children_async(self.notion_client, block["id"])
                for child in table_children:
                    if child["type"] == "table_row":
                        cells = child["table_row"].get("cells", [])

                        # Convert each cell content to paragraphs and reuse block_to_markdown
                        row_content = [
                            await self.block_to_markdown({
                                "type": "paragraph",
                                "paragraph": {"rich_text": cell},
                            })
                            for cell in cells
                        ]
                        table_rows.append(row_content)

            return md.table(table_rows)

        else:
            # Rest of the types
            # "paragraph"
            # "heading_1"
            # "heading_2"
            # "heading_3"
            # "bulleted_list_item"
            # "numbered_list_item"
            # "quote"
            # "to_do"
            # "template"
            # "synced_block"
            # "child_page"
            # "child_database"
            # "code"
            # "callout"
            # "breadcrumb"
            # "table_of_contents"
            # "link_to_page"
            # "audio"
            # "unsupported"

            block_data = block.get(block_type, {})
            block_content = block_data.get("text", [])
            if not block_content:
                block_content = block_data.get("rich_text", [])

            for content in block_content:
                if content.get("type") == "equation":
                    parsed_data += md.inline_equation(content["equation"]["expression"])
                    continue

                plain_text = content.get("plain_text", "")
                annotations = content.get("annotations", {})

                # Apply annotations to plain_text
                plain_text = self._apply_annotations(plain_text, annotations)

                # Add link if present
                if content.get("href"):
                    plain_text = md.link(plain_text, content["href"])

                parsed_data += plain_text

        if block_type == "code":
            return md.code_block(parsed_data, block['code']['language'])

        elif block_type == "heading_1":
            return md.heading1(parsed_data)

        elif block_type == "heading_2":
            return md.heading2(parsed_data)

        elif block_type == "heading_3":
            return md.heading3(parsed_data)

        elif block_type == "quote":
            return md.quote(parsed_data)

        elif block_type == "callout":
            callout_string = ""
            if not block['has_children']:
                return md.callout(parsed_data, block['callout'].get('icon'))

            if block['id'] in _visited_block_ids:
                return md.callout(parsed_data, block['callout'].get('icon'))

            callout_children_object = await get_block_children_async(self.notion_client, block['id'], 100)
            _visited_block_ids.add(block['id'])
            try:
                callout_children = await self.block_list_to_markdown(
                    callout_children_object,
                    _visited_block_ids=_visited_block_ids)
            finally:
                _visited_block_ids.discard(block['id'])

            callout_string += f"{parsed_data}\n"
            for child in callout_children:
                callout_string += f"{child['parent']}\n\n"

            return md.callout(callout_string.strip(), block['callout'].get('icon'))

        elif block_type == "bulleted_list_item":
            return md.bullet(parsed_data)

        elif block_type == "numbered_list_item":
            return md.bullet(
                parsed_data,
                block['numbered_list_item'].get('number')
            )
        elif block_type == "to_do":
            return md.todo(
                parsed_data,
                block['to_do']['checked']
            )

        return parsed_data

    async def comment_to_markdown(self, comment: Dict) -> str:
        """Convert a Notion comment to markdown"""
        if not isinstance(comment, dict) or 'rich_text' not in comment:
            return ""

        parsed_data = ""
        block_content = comment.get("rich_text", [])
        display_name = comment.get("display_name") or {}
        name = display_name.get("resolved_name") or "Anonymous"
        if name:
            parsed_data += f"**{name}**: "
        for content in block_content:
            plain_text = content.get("plain_text", "")
            annotations = content.get("annotations", {})

            # Apply annotations to plain_text
            plain_text = self._apply_annotations(plain_text, annotations)

            # Add link if present
            if content.get("href"):
                plain_text = md.link(plain_text, content["href"])

            parsed_data += plain_text

        return parsed_data + "\n"
