import json

from nltk import pos_tag
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer
import pymorphy2
import re  # regex
from stop_words import get_stop_words
import zmq


def _is_english(string):
    return not re.match(r'[а-яА-ЯёЁ]', string)


def _get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN


def _lemmatize_sentence(sentence):
        my_list = []
        sentence = sentence.lower()
        tokens_pos = pos_tag(tokenizer.tokenize(sentence))
        for word in tokens_pos:
            if _is_english(word[0]):
                if word[0] not in english_stoplist:
                    lemmatized_word = lemmatizer.lemmatize(word[0], _get_wordnet_pos(word[1]))
                    if lemmatized_word not in english_stoplist:
                        my_list.append(lemmatized_word)
            else:
                if word[0] not in russian_stoplist:
                    lemmatized_word = russ_morph.normal_forms(word[0])
                    for variant in lemmatized_word:
                        if variant not in russian_stoplist:
                            my_list.append(variant)
        return list(set(my_list))

if __name__ == '__main__':
    # NLP part
    russ_morph = pymorphy2.MorphAnalyzer()
    english_stoplist = set(stopwords.words('english'))
    russian_stoplist = set(get_stop_words('ru'))
    tokenizer = RegexpTokenizer(r'\w+')
    lemmatizer = WordNetLemmatizer()

    # ZMQ part
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind('tcp://127.0.0.1:9080')

    print('Server is running on 127.0.0.1:9080 ...')
    while True:
        message = socket.recv()
        message = message.decode('utf-8')
        print('\nReceived request: ' + message)
        print('Answered with: ' + json.dumps(_lemmatize_sentence(message), ensure_ascii=False))
        socket.send_unicode(json.dumps(_lemmatize_sentence(message)))
