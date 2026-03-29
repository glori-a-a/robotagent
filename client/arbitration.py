# -*- coding: utf-8 -*-
# --------------------------------------------
# 项目名称: LLM任务型对话Agent
# 版权所有  ©2025丁师兄大模型
# 生成时间: 2025-05
# --------------------------------------------

import time
import json
import os
import re
import requests
import prompts
from utils import logger
from utils.redis_tool import RedisClient


TIMEOUT = 2.0
MAX_HIS = 6
TTL = 60
CHUNK_SIZE = 1024
MAX_TOKEN = 2048
REDIS_KEY = "voice:arbitration_history:"
_redis_client = RedisClient() 


API_KEY = os.environ["API_KEY"]
DOUBAO_URL = os.environ["BASE_URL"]
SYSTEM_PROMPT = prompts.ARBITRAION_SYSTEM_PROMPT


def request_arbitration(query, sender_id):
    headers = {
        "Content-Type": "application/json",
        "Authorization": API_KEY
    }
    message = [{"role": "system", "content": SYSTEM_PROMPT}]

    try:
        start_time = time.time()
        history = _redis_client.get(REDIS_KEY + sender_id)
        if history:
            history = json.loads(history)
        else:
            history = []
        # history = []
        history.append({"role": "user", "content": query})

        message.extend(history)

        body = dict(
            model="llama-3.3-70b-versatile",
            messages=message,
            max_tokens=MAX_TOKEN,
            temperature=0,
            stream=True
        )
        response = requests.post(
            DOUBAO_URL,
            headers=headers,
            json=body,
            stream=True,
            timeout=TIMEOUT
        )
        # 拼接完整回复后再取 A/B/C/D；仅读首个 delta 易拿到空串并错误落到默认 A（任务域）
        pieces = []
        for r in response.iter_lines(
                chunk_size=CHUNK_SIZE, decode_unicode=False, delimiter=b'\n'):
            r = r.decode("utf-8")
            if not r.strip():
                continue
            r = r.lstrip("data: ")
            if r.strip() == "[DONE]":
                break
            try:
                obj = json.loads(r)
            except Exception:
                continue
            choice = (obj.get("choices") or [{}])[0]
            delta = choice.get("delta") or {}
            piece = delta.get("content") or ""
            if piece:
                pieces.append(piece)
        raw = "".join(pieces).strip()
        upper = raw.upper()
        candidates = re.findall(r"[ABCD]", upper)
        # 取最后一个字母：模型偶有多余前缀时，结论多在末尾；避免英文词里抢先匹配到 A
        text = candidates[-1] if candidates else ""
        logger.info(
            f"Arbitration history: {history}, query:{query}, raw:{raw!r}, letter:{text!r}, cost time:{time.time() - start_time}")
        if text not in ["A", "B", "C", "D"]:
            text = "C"
            logger.info(f"Arbitration no valid A-D in model output, fallback to C (chat)")
        history.append({"role": "assistant", "content": text})
        history = history[-MAX_HIS:]
        history_str = json.dumps(history, ensure_ascii=False)
        _redis_client.set(REDIS_KEY + sender_id, history_str, ex=TTL)
        if text in ["C", "D"]:
            text = "chat"
        elif text == "B":
            text = "faq"
        else:
            text = "task"

        return text

    except Exception as e:
        logger.info(f"Arbitration API error: {e}")
        return "task"


if __name__ == '__main__':
    while True:
        query = input("输入:")
        res = request_arbitration(query, "131")
        print(res)

