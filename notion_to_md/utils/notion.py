from typing import List, Optional, Dict
from notion_client import Client, AsyncClient

def get_block_children(notion_client: Client,
                       block_id: str,
                       total_pages: Optional[int] = None) -> List[Dict]:
    """Get all children blocks of a Notion block"""
    result = []
    page_count = 0
    start_cursor = None

    while True:
        response = notion_client.blocks.children.list(
            start_cursor=start_cursor,
            block_id=block_id
        )

        result.extend(response['results'])

        start_cursor = response.get('next_cursor')
        page_count += 1

        if not start_cursor or (total_pages and page_count >= total_pages):
            break

    modify_numbered_list_object(result)
    return result

async def get_block_children_async(notion_client: AsyncClient,
                           block_id: str,
                           total_pages: Optional[int] = None) -> List[Dict]:
    """Get all children blocks of a Notion block"""
    result = []
    page_count = 0
    start_cursor = None

    while True:
        response = await notion_client.blocks.children.list(
            start_cursor=start_cursor,
            block_id=block_id
        )

        result.extend(response['results'])

        start_cursor = response.get('next_cursor')
        page_count += 1

        if not start_cursor or (total_pages and page_count >= total_pages):
            break

    modify_numbered_list_object(result)
    return result

def modify_numbered_list_object(blocks: List[Dict]) -> None:
    """Modify numbered list items to include their numbers"""
    numbered_list_index = 0

    for block in blocks:
        if (isinstance(block, dict) and block.get('type') == 'numbered_list_item'
                and isinstance(block.get('numbered_list_item'), dict)):
            numbered_list_index += 1
            block['numbered_list_item']['number'] = numbered_list_index
        else:
            numbered_list_index = 0