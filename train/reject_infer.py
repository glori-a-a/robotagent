# -*- coding:utf-8 -*-

import os
import sys
import re
import json
import random
import requests
from dotenv import load_dotenv
import base64
import time
import torch
import uvicorn
import numpy as np
import torch.nn.functional as F
from importlib import import_module
from fastapi import FastAPI, Request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))

from utils import logger


app = FastAPI()


dataset = "reject"
model_name = "bert"
x = import_module('models.' + model_name)
config = x.Config(dataset)
if not os.path.isfile(config.save_path):
    raise FileNotFoundError(
        "模型文件不存在: {}\n请在项目根目录执行: python train/run.py --model bert --data reject".format(
            config.save_path
        )
    )
model = x.Model(config).to(config.device)
model.load_state_dict(torch.load(config.save_path, map_location=config.device))
model.eval()
PAD, CLS = '[PAD]', '[CLS]'


def predict(query, threshold):
    with torch.no_grad():
        token = config.tokenizer.tokenize(query)
        token = [CLS] + token
        seq_len = len(token)
        mask = []
        token_ids = config.tokenizer.convert_tokens_to_ids(token)
        if len(token) < config.pad_size:
            mask = [1] * len(token_ids) + [0] * (config.pad_size - len(token))
            token_ids += ([0] * (config.pad_size - len(token)))
        else:
            mask = [1] * config.pad_size
            token_ids = token_ids[:config.pad_size]
            seq_len = config.pad_size

        x = torch.LongTensor([token_ids]).to(config.device)
        seq_len = torch.LongTensor([seq_len]).to(config.device)
        mask = torch.LongTensor([mask]).to(config.device)
        texts = (x, seq_len, mask)
        output = model(texts)
        prob = F.softmax(output, dim=-1).cpu().numpy()[0][1]
        predict = 1 if prob > threshold else 0

        return predict, prob


@app.post("/reject-server/v1")
async def inference(request: Request):
    json_info = await request.json()
    query = json_info.get("query")
    trace_id = json_info.get("trace_id")
    thres = json_info.get("thres", "0.5")

    result = {}
    try:
        response, score = predict(query, float(thres))
    except Exception:
        response, score = 1, 1.0

    result["data"] = response
    result["score"] = str(score)
    logger.info("Trace ID: {}, Request: {}, response: {}, confidence: {}".format(
        trace_id, query, result["data"], result["score"]))

    return result


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8007, workers=1)
