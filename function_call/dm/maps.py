# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime
from sinan import Sinan
from client.nlg import request_nlg
from mcp_core.mcp_client import MCPClient

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MCP_SERVER_PATH = os.path.join(BASE_DIR, "mcp_core", "amp_server.py")


mcp_client = MCPClient()


async def process(func_name, query, slots):

    if func_name not in ["Go_POI"]:
        return

    # MCP-backed implementation
        slots["date"] = datetime.now().strftime("%Y-%m-%d")
    
    formated_slots = {}
    keyword = ""
    if "city" in slots:
        keyword += slots["city"]
    if "landmark" in slots:
        keyword += slots["landmark"]
    if "POI" in slots:
        keyword += slots["POI"]
    formated_slots["keywords"] = keyword
    if "city" in slots:
        formated_slots["city"] = slots["city"]


    await mcp_client.connect_to_server(MCP_SERVER_PATH)
    tool_response = await mcp_client.execute("maps_text_search", formated_slots)
    tool_response = json.loads(tool_response)
    nlg = request_nlg(query, tool_response)

    return (tool_response, nlg)



