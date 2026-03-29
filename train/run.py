# -*- coding:utf-8 -*-
# --------------------------------------------
# 项目名称: LLM任务型对话Agent
# 版权所有  ©2025丁师兄大模型
# 生成时间: 2025-05
# --------------------------------------------

"""
    usage: python run.py --model bert --data intent
    GPU example: python run.py --model bert --data intent --device cuda --gpu 0
"""
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from utils import logger
import time
import torch
import numpy as np
from train_eval import train, test
from importlib import import_module
import argparse
from data_helper import build_dataset, build_iterator, get_time_dif


def resolve_device(mode: str, gpu_id: int) -> torch.device:
    if mode == "cpu":
        return torch.device("cpu")
    if mode == "cuda":
        if not torch.cuda.is_available():
            raise RuntimeError(
                "已指定 --device cuda，但当前 PyTorch 未检测到 CUDA。\n"
                "请安装 GPU 版 PyTorch（与本机驱动匹配的 CUDA 轮子），例如：\n"
                "  pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124"
            )
        if gpu_id < 0 or gpu_id >= torch.cuda.device_count():
            raise RuntimeError(
                "无效的 --gpu %s，当前可见 GPU 数量: %s"
                % (gpu_id, torch.cuda.device_count())
            )
        return torch.device("cuda:%d" % gpu_id)
    # auto: use GPU if available, otherwise CPU
    if torch.cuda.is_available():
        return torch.device("cuda:%d" % gpu_id)
    return torch.device("cpu")


parser = argparse.ArgumentParser(description='Robot intent/reject classifier training')
parser.add_argument('--model', type=str, required=True, help='model name: bert or bert_tiny')
parser.add_argument('--data', type=str, required=True, help='dataset name: intent or reject')
parser.add_argument('--device', type=str, default='auto', choices=['auto', 'cpu', 'cuda'],
                    help='device to use: auto (default), cpu, or cuda')
parser.add_argument('--gpu', type=int, default=0, help='GPU index when --device cuda')
args = parser.parse_args()


if __name__ == '__main__':
    dataset = args.data
    x = import_module('models.' + args.model)
    config = x.Config(dataset)
    config.device = resolve_device(args.device, args.gpu)
    logger.info(f"Using device: {config.device}")

    np.random.seed(1)
    torch.manual_seed(1)
    torch.cuda.manual_seed_all(1)
    torch.backends.cudnn.deterministic = True

    start_time = time.time()
    logger.info("Loading data...")
    train_data, dev_data, test_data = build_dataset(config)
    train_iter = build_iterator(train_data, config)
    dev_iter = build_iterator(dev_data, config)
    test_iter = build_iterator(test_data, config)
    time_dif = get_time_dif(start_time)
    logger.info(f"Data load time: {time_dif}")

    model = x.Model(config).to(config.device)
    train(config, model, train_iter, dev_iter, test_iter)
