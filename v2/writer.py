#!/usr/bin/python
# encoding: utf-8

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
    '-e': {'configVar': 'entropy', 'type': 'num'},
    '-d': {'configVar': 'dictionaryFile', 'type': 'string'},
    '-n': {'configVar': 'numSentences', 'type': 'num'},
}

def isnum(input): return input.isdigit()
def isString(input): return True
types = {'num': isnum, 'string': isString}

config = {
    'entropy': 1,
    'numSentences': 5,
    'dictionaryFile': 'default'
}



################################################################################
#                         Function Definitions                                 #
################################################################################

def matchesType(value, type):
    # return value.isdigit()
    return types[type](value)

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


def getRandomPos():
    return random.choice(partsOfSpeech.keys())


def getNextPosSuggestions(currentPos):
    suggestions = []
    if currentPos in partsOfSpeech:
        suggestions = partsOfSpeech[currentPos]
    else:
        suggestions = ["."]
    return suggestions

def getNextPos(currentPos):
    choices = getNextPosSuggestions(currentPos)

    totalWeight = 0
    currentWeight = 0
    weightedArray = []

    for choice in choices:
        totalWeight += int(choices[choice])
        for i in range(0, choices[choice]):
            weightedArray.append(choice)
    return random.choice(weightedArray)


def generatePosOrder():
    posOrder = []
    currentPos = getRandomPos()
    while currentPos not in [".", "?", "!"]:
        posOrder.append(currentPos)
        currentPos = getNextPos(currentPos)

    posOrder.append(currentPos)
    return posOrder


def chooseRandomStartingWord(pos):
    return random.choice(lookup[pos])


def makeSentence():
    posOrder = generatePosOrder()
    print posOrder

    sentenceWords = []
    sentenceWords.append(chooseRandomStartingWord(posOrder[0]))


def generateSentences():
    for i in range(0, config['numSentences']):
        print
        print makeSentence()
        print


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












################################################################################
#                         Run The Program                                      #
################################################################################
parseArguments(sys.argv)

(words, partsOfSpeech, lookup, meta) = loadDictionary(config['dictionaryFile'])


generateSentences()
