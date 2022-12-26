import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.translate.bleu_score import sentence_bleu

data = json.load(open('469_metadata_chatgpt.json'))
mscore = 0
for pdt in data:
    gold_questions = pdt['questions']
    chatgpt_questions = pdt['chatgptQuestions']
    model = SentenceTransformer('bert-base-nli-mean-tokens')
    sentence_embeddings_gold = model.encode(gold_questions)
    sentence_embeddings_chatgpt = model.encode(chatgpt_questions)

    comparison_matrix = cosine_similarity(sentence_embeddings_chatgpt, sentence_embeddings_gold)
    index_matched = comparison_matrix.argmax(axis=1)
    for i in range(len(chatgpt_questions)):
        # print(chatgpt_questions[i])
        # print(gold_questions[index_matched[i]])
        score = sentence_bleu(chatgpt_questions[i], gold_questions[index_matched[i]])
        if score > mscore:
            print(score)
            mscore = score
        # print()