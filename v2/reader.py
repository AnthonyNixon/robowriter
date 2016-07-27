#!/usr/bin/python
# encoding: utf-8

################################################################################
#                               Imports                                        #
################################################################################

import random
import csv
import json
import wikipedia
import re
import logging
import os.path
import sys
import subprocess

from nltk import *
import nltk

logging.captureWarnings(True)






################################################################################
#                         Constant Definitions                                 #
################################################################################

flags = {
    '-r': {'configVar': 'readMoreLimit', 'type': 'num'},
    '-d': {'configVar': 'dictionaryFile', 'type': 'string'},
    '-nosave': {'configVar': 'saveDictionary', 'type': 'unary'},
    '-delete': {'configVar': 'deleteDictionary', 'type': 'unary'},
    '-sync': {'configVar': 'syncMaster', 'type': 'unary'}
    }

def isnum(input): return input.isdigit()
def isString(input): return True
types = {'num': isnum, 'string': isString}

config = {
    'readMoreLimit': 3,
    'searchTerms': [],
    'dictionaryFile': 'default',
    'saveDictionary': True,
    'deleteDictionary': False,
    'syncMaster': False
}

restrictedWords = ['[', ']', '(', ')', '{', '}', "''"]



################################################################################
#                         Function Definitions                                 #
################################################################################

def matchesType(value, type):
    # return value.isdigit()
    return types[type](value)

def deleteDictionary(name):
    os.remove('dictionaries/' + name)


def addWord(firstWord, secondPos, secondWord):
    firstWord = firstWord.lower().replace("\n", '')
    secondWord = secondWord.lower().replace("\n", '')

    if firstWord != "" and secondWord not in restrictedWords:
        if firstWord in words:
            if secondPos in words[firstWord]:
                if secondWord in words[firstWord][secondPos]:
                    words[firstWord][secondPos][secondWord] += 1
                else:
                    words[firstWord][secondPos][secondWord] = 1
            else:
                words[firstWord][secondPos] = {}
                words[firstWord][secondPos][secondWord] = 1
        else:
            words[firstWord] = {}
            words[firstWord][secondPos] = {}
            words[firstWord][secondPos][secondWord] = 1

        if secondPos in lookup:
            if secondWord not in lookup[secondPos]:
                lookup[secondPos].append(secondWord)
        else:
            lookup[secondPos] = []
            lookup[secondPos].append(secondWord)

def addPos(firstPos, secondPos):
    if firstPos != "" and secondPos != "":
        if firstPos in partsOfSpeech:
            if secondPos in partsOfSpeech[firstPos]:
                partsOfSpeech[firstPos][secondPos] += 1
            else:
                partsOfSpeech[firstPos][secondPos] = 1
        else:
            partsOfSpeech[firstPos] = {}
            partsOfSpeech[firstPos][secondPos] = 1


def processContent(content):
    content = content.replace("\n", ' ')

    words = word_tokenize(content)
    taggedWords = nltk.pos_tag(words)

    for i in range(0, (len(taggedWords)-1)):
        (word, pos) = taggedWords[i]
        (nextWord, nextPos) = taggedWords[i+1]

        addWord(word.lower(), nextPos, nextWord.lower())
        addPos(pos, nextPos)


def crawlAndLearn(topic):
    print 'topic: ' + str(topic)
    if not 'educatedOn' in meta:
        meta['educatedOn'] = []

    if topic in meta['educatedOn']:
        print "Already Learned: " + topic
    else:
        search = wikipedia.search(topic, results=int(config['readMoreLimit']))
        for page in search:
            print "Learning about: " + page
            try:
                article = wikipedia.page(page)
                content = re.sub(r'=+\sSee also\s=+.+$', ' ', article.content, flags=re.M | re.S)
                content = re.sub(r'=+\s.+\s=+', ' ', content)
                content = re.sub(r'\(.+\)', ' ', content, flags=re.M | re.S)
                #print content
                processContent(content)
            except wikipedia.exceptions.DisambiguationError:
                content = ""
            except wikipedia.exceptions.PageError:
                content = ""
        if not 'educatedOn' in meta:
            meta['educatedOn'] = []
        meta['educatedOn'].append(topic)


def learnAbout(topics):
    try:
        for topic in topics.split(): # string case
            crawlAndLearn(topic)
            print('Words:' + str(len(words)))
            print('POS:' + str(len(partsOfSpeech)))
    except AttributeError:
        for topic in topics:
            crawlAndLearn(topic)
            print('Words:' + str(len(words)))
            print('POS:' + str(len(partsOfSpeech)))

def readRandom():
    randomArticles = wikipedia.random(pages=3)
    try:
        for topic in randomArticles: # string case
            crawlAndLearn(topic)
            print('Words:' + str(len(words)))
            print('POS:' + str(len(partsOfSpeech)))
    except AttributeError:
        for topic in randomArticles:
            crawlAndLearn(topic)
            print('Words:' + str(len(words)))
            print('POS:' + str(len(partsOfSpeech)))


def loadFileContents(name):
    if os.path.isfile(name):
        with open(name,'r') as contents:
            dictionary = json.loads(contents.read())
        return dictionary
    else:
        return {'words': {}, 'partsOfSpeech': {}, 'lookup': {}, 'meta': {'config': config}}


def loadDictionary(name):
    dictionary = loadFileContents('dictionaries/' + name)
    return (dictionary['words'], dictionary['partsOfSpeech'], dictionary['lookup'], dictionary['meta'])


def parseArguments(argv):
    if len(argv) > 1:
        i = 1
        while(i < len(argv)):
            if argv[i] in flags:
                if flags[argv[i]]['type'] == 'unary':
                    config[flags[argv[i]]['configVar']] = not config[flags[argv[i]]['configVar']]
                else:
                    if i+1 < len(argv):
                        if matchesType(argv[i+1], flags[argv[i]]['type']):
                            if flags[argv[i]]['type'] == 'num':
                                config[flags[argv[i]]['configVar']] = int(argv[i+1])
                            else:
                                config[flags[argv[i]]['configVar']] = argv[i+1]
                            i += 1
                        else:
                            print "ERROR: Value entered for flag '" + argv[i] + "' is expected to be type '" + flags[argv[i]]['type'] + "'"
                    else:
                        print "ERROR: value not found for flag '" + argv[i] + "'. Defaulting to " + str(config[flags[argv[i]]['configVar']])
            else:
                config['searchTerms'].append(argv[i])
            i += 1


def saveDictionary(words, partsOfSpeech, lookup, meta, name):
    content = {'meta': meta, 'words': words, 'partsOfSpeech': partsOfSpeech, 'lookup': lookup}
    print "Saving..."
    print "Words: " + str(len(words))
    print "Parts of Speech: " + str(len(partsOfSpeech))
    print "Lookup: " + str(len(lookup))
    with open('dictionaries/' + name,'w+') as contents:
        contents.write(json.dumps(content, indent=2))


def configDiffersFromMeta(config, meta):
    return config['readMoreLimit'] != meta['config']['readMoreLimit']















################################################################################
#                         Run The Program                                      #
################################################################################
parseArguments(sys.argv)

if (config['deleteDictionary']):
    print "deleting"
    deleteDictionary(config['dictionaryFile'])

(words, partsOfSpeech, lookup, meta) = loadDictionary(config['dictionaryFile'])
if configDiffersFromMeta(config, meta):
    print "Config changed."

if len(config['searchTerms']) > 0:
    learnAbout(config['searchTerms'])
else:
    readRandom()

if config['saveDictionary']:
    print "saving to dictionaries/" + config['dictionaryFile']
    print('Words:' + str(len(words)))
    print('POS:' + str(len(partsOfSpeech)))
    saveDictionary(words, partsOfSpeech, lookup, meta, config['dictionaryFile'])
