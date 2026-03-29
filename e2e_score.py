# -*- coding: utf-8 -*-

"""End-to-end scoring helper for multi-turn test logs."""

import json
fd = open("test/result/multi_test_output.txt")
for line in fd:
    info = json.loads(line)
    query = info["query"]    
    res = ""
    for msg in info["res"]:
        if msg["intent"] == "闲聊百科":
            res += msg["frame"].replace("\n", " ") 
        else:
            res += msg["intent"] + "\t" + json.dumps(msg["slots"], ensure_ascii=False)
    print(query + "############" + res)

# Label multi_test_output.txt by hand, then run this block for accuracy.
print("\n" + "="*50)
with open("test/result/multi_test_output_labeled.txt") as file_handler:
    right, total = 0, 0
    for line in file_handler:
        if line.startswith("1"):
            right += 1
        total += 1
    print("E2E accuracy: {}%".format(round(right/total * 100, 3)))
print("="*50)
