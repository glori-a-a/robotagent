# -*- coding:utf-8 -*-

import torch
import torch.nn as nn
from pathlib import Path

from core import BertModel, BertTokenizer


TRAIN_DIR = Path(__file__).resolve().parent.parent


class Config(object):

    def __init__(self, dataset):
        self.dataset = dataset
        self.model_name = 'bert'

        dataset_dir = TRAIN_DIR / 'data' / dataset
        pretrained_dir = TRAIN_DIR / 'pretrained' / 'chinese_roberta_wwm_ext'
        saved_dir = TRAIN_DIR / 'saved' / dataset
        saved_dir.mkdir(parents=True, exist_ok=True)

        self.train_path = str(dataset_dir / 'train.txt')
        self.dev_path = str(dataset_dir / 'dev.txt')
        self.test_path = str(dataset_dir / 'test.txt')
        with open(dataset_dir / 'class.txt', encoding='utf-8') as class_file:
            self.class_list = [x.strip() for x in class_file.readlines()]
        self.save_path = str(saved_dir / (self.model_name + '.ckpt'))
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        self.require_improvement = 1000
        self.num_classes = len(self.class_list)
        self.num_epochs = 3
        self.batch_size = 16
        self.pad_size = 32
        self.learning_rate = 5e-5
        self.bert_path = str(pretrained_dir)
        self.tokenizer = BertTokenizer.from_pretrained(self.bert_path)
        self.hidden_size = 768


class Model(nn.Module):

    def __init__(self, config):
        super(Model, self).__init__()
        self.bert = BertModel.from_pretrained(config.bert_path)
        for param in self.bert.parameters():
            param.requires_grad = True
        self.fc = nn.Linear(config.hidden_size, config.num_classes)

    def forward(self, x):
        context = x[0]
        mask = x[2]
        _, pooled = self.bert(context, attention_mask=mask, output_all_encoded_layers=False)
        out = self.fc(pooled)
        return out
