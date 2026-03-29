# -*- coding: utf-8 -*-

import asyncio
import os
import json
from typing import Any, Optional
from contextlib import AsyncExitStack
from openai import OpenAI


class MCPClient:
    def __init__(self):
        """Create MCP client state."""
        self.exit_stack = AsyncExitStack()
        self.session: Optional[Any] = None

    async def connect_to_server(self, server_script_path: str):
        """Connect to MCP server over stdio and list tools."""
        try:
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client
        except ImportError as e:
            raise ImportError(
                "Package `mcp` missing or Python too old; need Python>=3.10. Run: pip install mcp"
            ) from e

        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be .py or .js")

        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )

        # Start MCP server subprocess and stdio transport
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        # List tools from server
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected; tools:", [tool.name for tool in tools])     
        

    async def process_query(self, query: str) -> str:
        raise NotImplementedError
            
    
    async def execute(self, function_name, tool_args):
        print("\nMCP client running")

        try:
            # Call tool by name
            result = await self.session.call_tool(function_name, tool_args)
            print(f"\n\n[Calling tool with args {tool_args}]\n\n")
            print(f"\n🤖 MCP Response: {result.content[0].text}")
            return result.content[0].text

        except Exception as e:
            print(f"\nError: {str(e)}")
            return "Not Find"


    async def cleanup(self):
        """Close stdio session and subprocess."""
        await self.exit_stack.aclose()


async def main():
    client = MCPClient()
    try:
        await client.connect_to_server("amp_server.py")
        await client.execute("maps_weather", {"city": "北京", "date": "2025-05-02"})
    finally:
        await client.cleanup()


if __name__ == "__main__":
    import sys
    asyncio.run(main())

