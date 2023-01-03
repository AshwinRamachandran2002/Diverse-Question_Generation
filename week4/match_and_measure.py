import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.translate.bleu_score import sentence_bleu
import evaluate

metric = 'bleu'
if metric == 'meteor':
    meteor = evaluate.load('meteor')
if metric == 'entailment':
    entail = None

data = json.load(open('469_metadata_chatgpt.json'))
for pdt in data:
    mscore = 0
    avgscore = 0
    gold_questions = pdt['questions']
    chatgpt_questions = pdt['chatgptQuestions']
    model = SentenceTransformer('bert-base-nli-mean-tokens')
    sentence_embeddings_gold = model.encode(gold_questions)
    sentence_embeddings_chatgpt = model.encode(chatgpt_questions)

    comparison_matrix = cosine_similarity(sentence_embeddings_chatgpt, sentence_embeddings_gold)
    index_matched = comparison_matrix.argmax(axis=1)
    for i in range(len(chatgpt_questions)):
        if metric == "bleu":
            score = sentence_bleu(chatgpt_questions[i], gold_questions[index_matched[i]])
        elif metric == "meteor":
            score = meteor.compute(predictions=[chatgpt_questions[i]], references=[gold_questions[index_matched[i]]])['meteor']

        avgscore += score
        if score > mscore:
            # print(score)
            mscore = score

    print("Max score: ", mscore)
    print("Avg score: ", avgscore/len(data))
