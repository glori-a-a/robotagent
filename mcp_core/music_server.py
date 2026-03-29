# -*- coding: utf-8 -*-

try:
    from qqmusic_api import search as qq_search
    from mcp.server.fastmcp import FastMCP

    _HAS_QQ = True
except ImportError:
    qq_search = None
    FastMCP = None
    _HAS_QQ = False


if _HAS_QQ:
    mcp = FastMCP("mcp-qqmusic-test-server")

    @mcp.tool()
    async def search_music(keyword: str, page: int = 1, num: int = 3):
        """
        Search for music tracks
        """
        result = await qq_search.search_by_type(keyword=keyword, page=page, num=num)

        if isinstance(result, list):
            filtered_list = []
            for item in result:
                song_info = {
                    "id": item.get("id"),
                    "mid": item.get("mid"),
                    "name": item.get("name"),
                    "pmid": item.get("pmid", ""),
                    "icon_url": item.get("icon_url", ""),
                    "subtitle": item.get("subtitle", ""),
                    "time_public": item.get("time_public", ""),
                    "title": item.get("title", item.get("name", ""))
                }
                filtered_list.append(song_info)

            return filtered_list
        return []

else:
    async def search_music(keyword: str, page: int = 1, num: int = 3):
        """Stub when qqmusic-api-python / mcp extras are not installed."""
        return []


if __name__ == "__main__":
    if _HAS_QQ:
        mcp.run(transport='stdio')
