import os
import json
import random
import numpy as np 
import torch 
from torch.utils.data import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForMaskedLM,
    BartForConditionalGeneration,
    BartConfig,
    Trainer,
    TrainingArguments,
    EarlyStoppingCallback,
)
from datasets import load_metric
from bleu import corpus_bleu, SmoothingFunction
from nltk.tokenize import word_tokenize

from utils import SPECIAL_TOKENS

MODEL_NAME = 'facebook/bart-base'
PROJECT_NAME = 'SqlToText'

n_epochs = 100
batch_size = 16
lr = 3e-5
weight_decay = 1e-2

tables = '/mnt/infonas/data/awasthi/semantic_parsing/smbop/dataset/tables.json'
tables = json.load(open(tables))
db_tables = {}
for table in tables:
    db_tables[table['db_id']] = table 
    db_tables[table['db_id']]['columns'] = [x[1] for x in table['column_names']]

run_name = f'plan-based-{MODEL_NAME}-n_epochs={n_epochs}-lr={lr}-batch_size={batch_size}-weight_decay={weight_decay}'
os.environ['WANDB_PROJECT'] = PROJECT_NAME

training_args = TrainingArguments(
    output_dir=f'./runs/{run_name}',
    overwrite_output_dir=True,
    num_train_epochs=n_epochs,
    per_device_train_batch_size=batch_size,
    per_device_eval_batch_size=batch_size,
    save_total_limit=1,
    prediction_loss_only=False,
    do_train=True,
    do_eval=True,
    evaluation_strategy='epoch',
    save_strategy='epoch',
    weight_decay=weight_decay,
    learning_rate=lr,
    warmup_steps=100,
    lr_scheduler_type='linear',
    metric_for_best_model='bleu',
    load_best_model_at_end=True,
    fp16=True,
    eval_accumulation_steps=8,
    report_to='tensorboard',
    run_name=run_name,
)

class Spider(Dataset):
    def __init__(self, path, training):
        super().__init__()
        self.training = training
        with open(path, 'r') as f:
            self.data = json.load(f)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        data_item = self.data[idx]
        if self.training:
            toss = np.random.uniform()
            if toss < 0.30:
                data_item['bart_input'] = data_item['proc_query']
            else:
                data_item['bart_input'] = data_item['proc_query'] \
                                        + f" <temp> {data_item['template']} </temp>"
        else:
            data_item['bart_input'] = data_item['proc_query'] \
                                    + f" <temp> {data_item['template']} </temp>"
        return data_item


tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
tokenizer.add_tokens(SPECIAL_TOKENS, special_tokens=True)

def compute_bleu(outputs):
    logits = outputs.predictions 
    pred_ids = np.argmax(logits[0], axis=-1)
    pred_ids[pred_ids==-100]=1
    label_ids = outputs.label_ids
    label_ids[label_ids==-100]=1
    pred_str = tokenizer.batch_decode(pred_ids, skip_special_tokens=True)
    label_str = tokenizer.batch_decode(label_ids, skip_special_tokens=True)
    pred_toks = [word_tokenize(item) for item in pred_str]
    label_toks = [[word_tokenize(item)] for item in label_str]
    pseudo_label_toks = [word_tokenize(item) for item in label_str]
    bleu = corpus_bleu(label_toks, pred_toks, smoothing_function=SmoothingFunction().method3)
    print()
    randidx = np.random.randint(0,len(pred_str))
    print(f'pred: {pred_str[randidx]}')
    print(f'gold: {label_str[randidx]}')
    print()
    return {'bleu': bleu}

def get_table_names(item):
    table_names = db_tables[item['db_id']]['table_names'].copy()
    random.shuffle(table_names)
    return table_names

def collate_fn(batch):
    labels = [item['template'] + ' <sep> ' + item['question'] for item in batch]
    inputs = [item['proc_query'] for item in batch]
    ret = tokenizer(inputs, return_tensors='pt', padding=True, max_length=512)
    ret['labels'] = tokenizer(labels, return_tensors='pt', padding=True, max_length=512)['input_ids']
    return ret

def main():
    """
    wandb.init(project=PROJECT_NAME, entity='ashutoshandabhijeet')
    wandb.config.update({
        'n_epochs': n_epochs,
        'batch_size': batch_size,
        'lr': lr,
        'weight_decay': weight_decay,
        'notes': notes,
    })
    """
    model = AutoModelForMaskedLM.from_pretrained(MODEL_NAME)
    model.resize_token_embeddings(len(tokenizer))

    TRAIN_PATH = 'jsons/train_spider_template_improved_blec_th_50.json'
    DEV_PATH = 'jsons/dev_template_improved_blec_th_50.json'
    train = Spider(TRAIN_PATH, training=True)
    dev = Spider(DEV_PATH, training=False)

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train,
        eval_dataset=dev,
        data_collator=collate_fn,
        compute_metrics=compute_bleu,
        tokenizer=tokenizer,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=20)]
    )

    result = trainer.train()
    trainer.save_model()
    trainer.log_metrics('train', result.metrics)
    trainer.save_metrics('train', result.metrics)
    trainer.save_state()

if __name__ == '__main__':
    os.environ['WANDB_DISABLED']='true'
    main()