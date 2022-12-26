import json

qa_data = json.load(open('qa_1000.json'))
meta_data = json.load(open('metadata_1000.json'))

dict_asin = {}
number  = 0
for meta in meta_data:
    dict_asin[number] = []
    for qa in qa_data:
        if qa['asin'] == meta['asin']:
            dict_asin[number].append(json.dumps(qa["question"]))
    number += 1

for key, value in dict_asin.items():
    if value != []:
        print(json.dumps(meta_data[key]))
        print(key, value)