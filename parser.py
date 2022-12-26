import json

f = open('raw_sample.json')

data = json.load(f)

for word in data['feature']:
    print(word)

# print(data)