import json
import re
data = json.load(open('mix2.json'))

min_ngram = 2
max_ngram = 5
keyword_collection = []

def getngrams_line(line, keyword_collection):
    words = line.split()#re.split(', |:', line)
    for i in range(len(words)):
        words[i] = words[i].strip('()| :')
    for ngram in range(min_ngram, max_ngram + 1):
        for i in range(len(words)-ngram+1):
            keyword_collection.append(" ".join(words[i:i+ngram]).lower())

for keyword in data.keys():
    if keyword in ["description", "feature"]:
        for line in data[keyword]:
            getngrams_line(line, keyword_collection)
    if keyword in ["title"]:
        getngrams_line(data[keyword], keyword_collection)
    if keyword in ["brand"]:
        keyword_collection.append(data[keyword].lower())

    # print(keyword_collection)

def mask(qa, keywords):
    words = qa.lower().split()
    masked = []
    for ngram in range(min_ngram, max_ngram + 1):
        for i in range(len(words)-ngram+1):
            term = " ".join(words[i:i+ngram])
            if term in keywords:
                masked.append(term)
    print(masked)

for qa in data["qa"]:
    mask(qa, keyword_collection)


         
