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


# FastAPI intent (BERT top-k) service
app = FastAPI()


dataset = "intent"
model_name = "bert"
x = import_module('models.' + model_name)
config = x.Config(dataset)
if not os.path.isfile(config.save_path):
    raise FileNotFoundError(
        "Model checkpoint missing: {}\nFrom repo root run: python train/run.py --model bert --data intent".format(
            config.save_path
        )
    )
model = x.Model(config).to(config.device)
model.load_state_dict(torch.load(config.save_path, map_location=config.device))
model.eval()
PAD, CLS = '[PAD]', '[CLS]'
TOPK = 5


def predict(query):
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
        prob = F.softmax(output,dim=-1).cpu().numpy()[0]
        index = np.argsort(-prob)[:TOPK]

        return index, prob[index] 


@app.post("/intent-server/v1")
async def inference(request: Request):
    json_info = await request.json()
    query = json_info.get("query")
    trace_id = json_info.get("trace_id")

    result = {}
    try:
        response, score = predict(query)
    except:
        response, score = [3] * TOPK, [1.0] * TOPK

    result["data"] = ",".join([str(k) for k in response])
    result["score"] = ",".join([str(k) for k in score])
    logger.info("Trace ID: {}, Request: {}, response: {}, confidence: {}".format(
        trace_id, query, result["data"], result["score"]))

    return result 


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8008, workers=1)
