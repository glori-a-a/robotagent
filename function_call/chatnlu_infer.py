# -*- coding: utf-8 -*-
# --------------------------------------------
# 项目名称: LLM任务型对话Agent
# 版权所有  ©2025丁师兄大模型
# 生成时间: 2025-05
# --------------------------------------------


import os
import sys
import json
import re
import uuid
from dotenv import load_dotenv
import random
import numpy as np
import requests
import base64
import time
import uvicorn
from fastapi import FastAPI, Request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FC_DIR = os.path.dirname(os.path.abspath(__file__))
for _p in (BASE_DIR, FC_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))

import prompts
from slot_process import intent_slot
from function import tools1
from utils import logger
from dm.factory import DMFactory


## 创建FastAPI应用
app = FastAPI()


MAX_CONF = 0.98
TIMEOUT = 5
INTENT_URL = os.environ["INTENT_URL"]
DOUBAO_API_KEY = os.environ["API_KEY"]
DOUBAO_URL = os.environ["BASE_URL"]


id2func = {}
func2name = {}
name2id = {}
with open(os.path.join(BASE_DIR, "config", "class.txt"), 'r', encoding='utf-8') as mapfile:
    for line in mapfile:
        id, name, func = line.strip().split(":")
        id2func[id] = func
        func2name[func] = name
        name2id[name] = id

# BERT 意图集未单独训练「停止」类时，仍通过 LLM 选出 Stop_Movement，需可序列化到 API
if "Stop_Movement" not in func2name:
    sid = str(max(int(x) for x in id2func.keys()) + 1)
    func2name["Stop_Movement"] = "停止运动"
    name2id["停止运动"] = sid
    id2func[sid] = "Stop_Movement"

_INSTRUCT_RE = re.compile(r"(怎么|如何|怎样|为啥|为什么|什么意思|教程|步骤|原理)")
_PURE_STOP_RE = re.compile(
    r"^(停下|停止|别动|急停|站住|停下来|不要再走了|立停)(\s|!|！|。|…|~|～)*$",
    re.I,
)


def _is_instructional_question(q: str) -> bool:
    return bool(_INSTRUCT_RE.search((q or "").strip()))


tool_map = {}
with open(os.path.join(BASE_DIR, "config", "slot_intent.json"), "r", encoding="utf-8") as slotfile:
    slot_map = json.load(slotfile)
    for item in tools1:
        name = item["function"]["name"]
        if name not in tool_map.keys():
            lst = [item]
            new_dict = {name: lst}
            tool_map.update(new_dict)
        else:
            tool_map.get(name).append(item)


def send_messages(messages, tool_lst):
    headers = {
        "Authorization": DOUBAO_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.3-70b-versatile", # supports function calling
        "messages": messages,
        "tools": tool_lst,
        "temperature": 1e-6,
        "top_p": 0
    }
    try:
        response = requests.post(
            DOUBAO_URL,
            headers=headers,
            data=json.dumps(data),
            timeout=TIMEOUT
        )
        res = response.content.decode('utf-8')
        res = json.loads(res)
        return res['choices'][0]['message']['tool_calls']
    except Exception as e:
        logger.error(f"Doubao error: {e}")
        return None


def intent_recall(query, trace_id):
    headers = {'Content-Type': 'application/json'}
    data = {"query": query, "trace_id": str(uuid.uuid1())}
    response = requests.post(url=INTENT_URL, headers=headers, data=json.dumps(data))
    return response.json()


def predict(query, trace_id):
    try:
        if _is_instructional_question(query):
            return "未知-无"

        if _PURE_STOP_RE.match((query or "").strip()):
            stop_tools = list(tool_map.get("Stop_Movement", []))
            if stop_tools:
                header = [{"role": "system", "content": prompts.NLU_SYSTEM_PROMPT}]
                messages = header + [{"role": "user", "content": query}]
                result = send_messages(messages, stop_tools)
                logger.info(f"pure-stop llm: {result}")
                if result:
                    return intent_slot(result, func2name, slot_map)
            return "未知-无"

        start = time.time()
        intent_rec = intent_recall(query, trace_id)
        results = intent_rec["data"].split(",")
        max_score = max([float(k) for k in intent_rec["score"].split(",")])
        logger.info(f"top5：{intent_rec['data']}, cost: {time.time() - start}")
        if str(results[0]) == "5" and max_score > MAX_CONF:
            return "未知-无"

        now_tool = []
        for t in results:
            func = id2func.get(t)
            lst_a = tool_map.get(func)
            if lst_a:
                for s in lst_a:
                    now_tool.append(s)
            else:
                continue

        offered = {t["function"]["name"] for t in now_tool}
        if "Navigate_To_Location" in offered and "Stop_Movement" not in offered:
            for st in tool_map.get("Stop_Movement", []):
                now_tool.append(st)

        header = [{"role": "system", "content": prompts.NLU_SYSTEM_PROMPT}]
        context = [{"role": "user", "content": query}]
        messages = header + context
        start_time = time.time()
        result = send_messages(messages, now_tool)
        logger.info(f"llm结果：{result}")
        logger.info(f"function调用时间:{time.time() - start_time}")
        if not result:
            return "未知-无"

        nlu = intent_slot(result, func2name, slot_map)
    except:
        return "未知-无"

    logger.info(f"返回结果：{nlu}")

    return nlu


@app.post("/chatnlu-server/v1")
async def inference(request: Request):
    json_info = await request.json()

    begin = time.time()
    query = json_info.get("query")
    enable_dm = json_info.get("enable_dm", True)
    trace_id = json_info.get("trace_id", "1")

    # 抽取意图和槽位
    nlu = predict(query, trace_id)


    # NLU后处理
    nlu_items = nlu.split("-")
    intent = nlu_items[0]
    if len(nlu_items) > 2:
        slots_str = "-".join(nlu_items[1:])
    else:
        slots_str = nlu_items[1]

    if slots_str != "无":
        slots = {}
        for item in slots_str.split(","):
            if ":" in item:
                if len(item.split(":")) != 2:
                    continue
                k, v = item.split(":")
                slots[k] = v
    else:
        slots = {}
    intent_id = name2id.get(intent)
    func_name = id2func.get(intent_id) 


    response = {
        "query": query,
        "tarce_id": trace_id,
        "intent": intent,
        "intent_id": intent_id,
        "function": func_name,
        "slots": slots,
    }

    if enable_dm:
        for name in ["weather", "music", "maps"]:
            dm_result = await DMFactory.get(name)(func_name, query, slots)
            if dm_result:
                tool_response, nlg = dm_result
                response["tool"] = tool_response
                response["nlg"] = nlg

    cost = time.time() - begin
    response["cost"] = cost

    return response

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8009, workers=1)
