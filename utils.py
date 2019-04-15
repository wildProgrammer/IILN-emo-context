import nltk
import math
import json
import requests
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk.corpus import wordnet as wn
from nltk.wsd import lesk

# nltk.download('maxent_ne_chunker')
# nltk.download('words')

def get_wordnet_pos(word):
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV}

    return tag_dict.get(tag, wordnet.NOUN)

# Use of get_wordnet_pos
# for tweet in tweets:
#         print([wordnet_lemmatizer.lemmatize(w, get_wordnet_pos(w)) for w in nltk.word_tokenize(tweet)])
    

def tf_idf(tweets_dicts):
    tf = {
        "happy" : {},
        "sad" : {},
        "angry" : {},
        "others" : {}
    }
    emo = {
        "happy" : 0,
        "sad" : 0,
        "angry" : 0,
        "others" : 0
    }
    idf = {}
    for dic in tweets_dicts:
        freq = {}
        [tweet1, tweet2, tweet3, aux] = dic["replies"]
        for word_dic in tweet1:
            if word_dic["lemma"] not in freq:
                freq[word_dic["lemma"]] = 1
            else:
                freq[word_dic["lemma"]] += 1
        for word_dic in tweet2:
            if word_dic["lemma"] not in freq:
                freq[word_dic["lemma"]] = 1
            else:
                freq[word_dic["lemma"]] += 1
        for word_dic in tweet3:
            if word_dic["lemma"] not in freq:
                freq[word_dic["lemma"]] = 1
            else:
                freq[word_dic["lemma"]] += 1
        
        for word in freq.keys():
            if word not in idf:
                idf[word] = 1
            else:
                idf[word] += 1
            if word not in tf[dic["emotion"]]:
                tf[dic["emotion"]][word] = freq[word]
            else:    
                tf[dic["emotion"]][word] += freq[word]
        
        
        emo[dic["emotion"]] += 1
    
    for emotion in tf.keys():
        for word in tf[emotion].keys():
            tf[emotion][word] /= emo[emotion]
    
    for word in idf.keys():
        idf[word] = math.log(len(tweets_dicts)/idf[word])

    for emotion in tf.keys():
        for word in tf[emotion].keys():
            tf[emotion][word] *= idf[word]
    
    s = json.dumps(tf)
    open("tf-idf.json", "wt").write(s)
    print(tf)


#tf_idf(json.load(open("parsed_dataset.json", "rt")))
# import spacy
# from spacy import displacy
# from collections import Counter
# import en_core_web_sm
# nlp = en_core_web_sm.load()

def ner(tweets_dicts):
    labels= {"sentences":0,}
    for dic in tweets_dicts:
        labels["sentences"] += 1
        
        [tweet1, tweet2, tweet3, aux] = dic["replies"]
        sentence = []
        for word_dic in tweet1:
            sentence.append( (word_dic["word"], word_dic["pos"]) )
       
        for chunk in nltk.ne_chunk(sentence):
            if hasattr(chunk, 'label') and chunk.label:
                # name_value = ' '.join(child[0] for child in chunk.leaves())
                # print(name_value, chunk.label())
                if chunk.label() in labels:
                    labels[chunk.label()] += 1
                else:
                    labels[chunk.label()] = 1
        
        sentence = []
        for word_dic in tweet2:
            sentence.append( (word_dic["word"], word_dic["pos"]) )
       
        for chunk in nltk.ne_chunk(sentence):
            if hasattr(chunk, 'label') and chunk.label:
                # name_value = ' '.join(child[0] for child in chunk.leaves())
                # print(name_value, chunk.label())
                if chunk.label() in labels:
                    labels[chunk.label()] += 1
                else:
                    labels[chunk.label()] = 1
        sentence = []
        for word_dic in tweet3:
            sentence.append( (word_dic["word"], word_dic["pos"]) )
       
        for chunk in nltk.ne_chunk(sentence):
            if hasattr(chunk, 'label') and chunk.label:
                # name_value = ' '.join(child[0] for child in chunk.leaves())
                # print(name_value, chunk.label())
                if chunk.label() in labels:
                    labels[chunk.label()] += 1
                else:
                    labels[chunk.label()] = 1
    print(labels)   
              

def simplified_lesk(word, context):
    max_overlap = -1
    best_sense = ""
    best_signature = ""
    for sense in wn.synsets(word):
        signature = set(sense.definition().split()) 
        overlap = len(signature & context) 
        if max_overlap < overlap:
            max_overlap = overlap
            best_sense = sense.lemmas()[0].name()
            best_signature = sense.definition()
    
    
    max_overlap = -1
    best_synonym = ""
    for sense in wn.synsets(best_sense):
        if sense.lemmas()[0].name().lower() != best_sense.lower():
            signature = set(sense.definition().split())
            overlap = len(signature & set(best_signature.split()))
            if max_overlap < overlap:
                max_overlap = overlap
                best_synonym = sense.lemmas()[0].name()

    return best_signature, best_synonym


def use_lesk(tweets_dicts):
    for dic in tweets_dicts:
        [tweet1, tweet2, tweet3, aux] = dic["replies"]
        sentence = []
        for word_dic in tweet1:
            if word_dic["pos"][0] == "N":
                sentence.append(word_dic["lemma"])
        for word in sentence:
            print(word, simplified_lesk(word, set(sentence)))
        
        sentence = []
        for word_dic in tweet2:
            if word_dic["pos"][0] == "N":
                sentence.append(word_dic["lemma"])
        for word in sentence:
            print(word, simplified_lesk(word, set(sentence)))
        
        sentence = []
        for word_dic in tweet3:
            if word_dic["pos"][0] == "N":
                sentence.append(word_dic["lemma"])
        for word in sentence:
            print(word, simplified_lesk(word, set(sentence)))

def emo_detection(text):
    response = requests.post(url = "http://text-processing.com/api/sentiment/", data = {"text": text}).json()["probability"]
    maxi = max( [response["neg"], response["neutral"], response["pos"]])
    for key, value in response.items():
        if value == maxi:
            emo = key
    return emo
    

# use_lesk(json.load(open("parsed_dataset.json", "rt")))
# ner(json.load(open("parsed_dataset.json", "rt")))

#emo_detection("Today I'm very happy")