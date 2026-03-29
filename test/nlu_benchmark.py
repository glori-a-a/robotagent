# -*- coding:utf-8 -*-
# --------------------------------------------
# 项目名称: LLM任务型对话Agent
# 版权所有  ©2025丁师兄大模型
# 生成时间: 2025-05
# --------------------------------------------

"""
运行命令：
locust -f nlu_benchmark.py  --host http://127.0.0.1:8009  --headless -u 10 -r 5 -t 60s
"""

import random
import uuid
from pathlib import Path
from locust import HttpUser, task, between

_data_path = Path(__file__).resolve().parent.parent / "train" / "data" / "intent" / "test.txt"
with open(_data_path, encoding="utf-8") as fd:
    samples = [k.split("\t")[0] for k in fd]

class User(HttpUser):
    wait_time = between(3, 5)

    @task
    def task_post_archive(self):
        trace_id = f'cevi{uuid.uuid4().hex}'
        testServer = 'http://127.0.0.1:8009'
        path = '/chatnlu-server/v1'
        url = f'{testServer}{path}'
        headers = {
            'Content-Type': 'application/json'        }
        data = {
            "query": random.choice(samples),
            "trace_id": trace_id
        }
        self.client.post(url, json=data, headers=headers)

