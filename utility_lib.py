
import nltk
import math
import json
from nltk.wsd import lesk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from itertools import chain
# from gensim import models, corpora
import re

def get_wordnet_pos(pos):
    tag_dict = {"J": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV}
    return tag_dict.get(pos[0], wordnet.NOUN)


def best_synonym(replies):
    words = tuple([i for reply in replies for i in reply])
    words_str = tuple([i["lemma"] for i in words])
    # print(words_str)
    for i in range(0, len(words)):
        # print(words[i])
        try:
            best_syn = lesk(words_str, words_str[i], get_wordnet_pos(words[i]["pos"]))
            # print(best_syn)
            lemma_names = best_syn.lemma_names()
            if isinstance(lemma_names, list):
                words[i]["best_syn"] = lemma_names[0]
                 
        except:
            print("Except ", words_str[i])
def populate_synonym_db(wordObj, database: dict, emotion):
    synonyms = wordnet.synsets(wordObj["lemma"])
    
    lemmas = chain.from_iterable([word.lemma_names() for word in synonyms])
    wordObj["synonyms"] = list(set(lemmas))
    add_lemma(wordObj["lemma"], wordObj["synonyms"], database, emotion)


def add_lemma(lemma, synonyms, database: dict, emotion):
    weight = 1
    if lemma in database:
            if isinstance(database[lemma], str):
                weight = 0.8
                counter = database[database[lemma]]
            else:
                counter = database[lemma]
    else:
        presentSynonyms = [
            synonym for synonym in synonyms if synonym in database]
        if len(presentSynonyms) == 0:
            counter = {
                "angry": 0,
                "others": 0,
                "happy": 0,
                "sad": 0
            }
            database[lemma] = counter
        else:
            weight = 0.8
            counter = None
            while counter == None:
                foundSyns = []
                for syn in presentSynonyms:
                    if not isinstance(database[syn], str):
                        counter = database[syn]
                        database[lemma] = syn
                        break
                    foundSyns.append(database[syn])
                presentSynonyms = foundSyns

    counter[emotion] += weight



frequent_words = { 
    "a", "an", "he", "she", "it", "you", "be", "the", "i", "u", "to", "from", "of", "your", "his", "her"
    
}

def remove_frequent_words(replies):
    for reply in replies:
        i = 0
        while i < len(reply):
            if reply[i]["lemma"] in frequent_words or reply[i]["word"].lower() in frequent_words:
                del reply[i]
            else:
                i+=1

def detect_capslock(line):
    i = 0
    total = 0
    for reply in line["replies"]:
        total+=len(reply)
        for word in reply:
            if word["word"] == word["word"].upper():
                i+=1
    line["capslock"] = total / 3 < i
        
punct_re = re.compile(r"^(\?|\.|,| |\(|\))+$")

def remove_punctuation(line):
    for reply in line["replies"]:
        i = 0
        while i < len(reply):
            if punct_re.match(reply[i]["word"]):
                del reply[i]
                # print("PUNCTUATION REMOVED")
            else:
                i+=1


def ner_words(line):
    replies = line["replies"]
    for reply in replies:
        tagged_words = [(wordObj["word"][0]+ wordObj["word"][1:], wordObj["pos"]) for wordObj in reply]
        ner_tags = nltk.ne_chunk(tagged_words)
        for chunk in ner_tags:
            if hasattr(chunk, "label") and chunk.label:
                name_value = ' '.join(child[0] for child in chunk.leaves())
                print("------------------------------------")
                print(name_value, chunk.label())
                for i in range(0, len(reply)):
                    wordObj = reply[i]
                    if wordObj['word'] == name_value:   
                        wordObj["ner_tag"] = chunk.label()
                        break


def reply_to_array_of_strings(reply):
    return list(map(lambda wordObj: wordObj["word"]))

# def lda_topic_detect(line):
#     dictionary = corpora.Dictionary( ))