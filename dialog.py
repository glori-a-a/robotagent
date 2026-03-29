# -*- coding: utf-8 -*-

import os
import requests
import json
import time
import random
import pprint
from pathlib import Path
from time import sleep
from dotenv import load_dotenv
import socketio

load_dotenv(Path(__file__).resolve().parent / ".env")

URL = os.environ["ENTRY_URL"]

sio = socketio.Client()

@sio.on("connect")
def on_connect():
    print("connected to server")

@sio.on("disconnect")
def on_disconnect():
    print("disconnected to server")

@sio.on("message")
def on_message(data):  
    print('Received message:', data)  

@sio.on("error")
def on_error(e):
    print('Error:', e)  

@sio.on("request_nlu")
def on_response(data):
    print("Response:", end="")
    if isinstance(data, str):
        payload = json.loads(data)
    else:
        payload = data
    print(payload)


def rand_str(size=6):
    return "".join(random.sample("1234567890zyxwvutsrqponmlkjihgfedcba", size))


if __name__ == "__main__":

    data = {
        "sender_id": rand_str(9)
    }

    sio.connect(URL)

    while True:
        data["trace_id"] = rand_str(9)
        print("enter query: ")
        query = input().strip()
        data["query"] = query
        data["enable_dm"] = True 
        sio.emit("request_nlu", json.dumps(data, ensure_ascii=False))

    print("done")

