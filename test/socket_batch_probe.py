# -*- coding: utf-8 -*-
"""Batch Socket.IO checks. From repo root: python test/socket_batch_probe.py"""
import json
import os
import sys
import time
from pathlib import Path

import socketio
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
URL = os.environ.get("ENTRY_URL", "http://localhost:8080")

QUERIES = [
    "你好",
    "在吗",
    "导航去充电站",
    "停下",
    "用慢速模式去工作台",
    "怎么抓取易碎物品",
    "扫描一下周围环境",
]


def summarize(payload):
    out = {}
    for k in ("intent", "intent_id", "function", "func", "status"):
        v = payload.get(k)
        if v is not None and v != "":
            out[k] = v
    frame = payload.get("frame")
    if not frame:
        return out
    if isinstance(frame, str) and len(frame) > 100:
        out["frame"] = frame[:100] + "..."
    else:
        out["frame"] = frame
    return out


def main():
    for i, query in enumerate(QUERIES):
        events = []
        sio = socketio.Client(
            logger=False,
            engineio_logger=False,
            request_timeout=60,
        )

        @sio.on("request_nlu")
        def on_resp(data, acc=events):
            p = json.loads(data) if isinstance(data, str) else dict(data)
            acc.append(p)

        try:
            sio.connect(URL, wait_timeout=20)
        except Exception as e:
            print(f"CONNECT FAIL ({URL}): {e}")
            print("请先启动 Redis、8007/8008/8009 与 python start.py")
            return 1

        sio.emit(
            "request_nlu",
            json.dumps(
                {
                    "sender_id": f"probe{i}",
                    "trace_id": f"p{i}",
                    "query": query,
                    "enable_dm": True,
                },
                ensure_ascii=False,
            ),
        )
        time.sleep(28)
        sio.disconnect()
        time.sleep(0.3)

        print("=" * 72)
        print("Q:", query)
        print("frames:", len(events))
        for j, ev in enumerate(events[:15]):
            print(f"  [{j}]", summarize(ev))
        if len(events) > 15:
            print("  ...", len(events) - 15, "more")
    return 0


if __name__ == "__main__":
    sys.exit(main())
