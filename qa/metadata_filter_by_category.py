import json
import numpy as np
meta_data = json.load(open('metadata_1000.json'))
categories = json.load(open('category_gt100'))

test_pdt = meta_data[0]
print('test product', json.dumps(test_pdt))
test_cat = test_pdt['category']
vec = np.zeros(len(categories))

for i in range(len(test_cat)):
    test_cat[i] = test_cat[i].lower()
for i, cat in enumerate(categories):
    if cat in test_cat:
        vec[i] = 1
print('vector length', (vec==1).sum())

matching_pdts = []
for pdts in meta_data[1:]:
    pdt_cat = pdts['category']
    for i in range(len(pdt_cat)):
        pdt_cat[i] = pdt_cat[i].lower()
    new_vec = np.zeros(len(categories))
    for i, cat in enumerate(categories):
        if cat in pdt_cat:
            new_vec[i] = 1
    score = new_vec.T@vec
    if score > 3:
        matching_pdts.append(pdts)

print('matching products', len(matching_pdts))
print(json.dumps(matching_pdts, indent=4))