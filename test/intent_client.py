# -*- coding:utf-8 -*-

import os
import requests
import uuid
import json
from pathlib import Path
from tqdm import tqdm


URL = os.environ["INTENT_URL"]

def get_completion(query):
    headers = {'Content-Type': 'application/json'}
    data = {"query": query, "trace_id": str(uuid.uuid1())}
    response = requests.post(url=URL, headers=headers, data=json.dumps(data))
    return response.json()

if __name__ == '__main__':
    _data_path = Path(__file__).resolve().parent.parent / "train" / "data" / "intent" / "test.txt"
    with open(_data_path, encoding="utf-8") as fd:
        data = fd.readlines()
    right = 0
    total = 0
    for index in tqdm(range(len(data))):
        line = data[index]
        text, label = line.strip().split("\t")
        label = int(label)
        response = get_completion(text)
        # print(text, response)
        if int(response["data"].split(",")[0]) == label:
            right += 1
        total += 1
    print("test avg acc@1:", right/total)
