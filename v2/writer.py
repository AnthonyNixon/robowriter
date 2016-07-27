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
    '-training': {'configVar': 'training', 'type': 'unary'}
}

def isnum(input): return input.isdigit()
def isString(input): return True
types = {'num': isnum, 'string': isString}

config = {
    'entropy': 1,
    'numSentences': 5,
    'dictionaryFile': 'default',
    'training': False
}

startingPosOptions = ['NN', 'NNS', 'NNP', 'EX', 'CD', 'DT', 'JJ', 'PRP',
    'WDT', 'WP', 'WRB']
ignorePos = ["``", ";", ":", "'", '"', "[", "]", '``']

punctuations = ['.', ',', '!', '?']
endPunctuations = ['.', '!', '?']



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


def getStartingPos():
    return random.choice(startingPosOptions)


def getNextPosSuggestions(currentPos):
    suggestions = []
    if currentPos in partsOfSpeech:
        suggestions = partsOfSpeech[currentPos]
    else:
        suggestions = {".": 1}
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
    currentPos = getStartingPos()
    while currentPos not in [".", "?", "!"]:
        if currentPos not in ignorePos:
            posOrder.append(currentPos)
        currentPos = getNextPos(currentPos)

    posOrder.append(currentPos)
    return posOrder


def chooseRandomWordWithPos(pos):
    return random.choice(lookup[pos])


def weightedChoice(choices):
    totalWeight = 0
    currentWeight = 0
    weightedArray = []

    for choice in choices:
        totalWeight += int(choices[choice])
        for i in range(0, choices[choice]):
            weightedArray.append(choice)
    return random.choice(weightedArray)


def onlyHasPunctuations(posList):
    for pos in posList:
        if pos not in endPunctuations:
            return False
    return True



def chooseReplacementPos(previousWord):
    replacement = '.'
    while replacement in endPunctuations:
        replacement = random.choice(words[previousWord].keys())

        if onlyHasPunctuations(words[previousWord].keys()):
            return replacement
    return replacement



def getNextWord(previousWord, pos):
    if previousWord in words.keys():
        if pos in words[previousWord]:
            nextWord = weightedChoice(words[previousWord][pos])
            return (nextWord, pos)
        else:
            if pos not in punctuations:
                replacement = chooseReplacementPos(previousWord)
                return (weightedChoice(words[previousWord][replacement]), replacement)
            else:
                return (pos, pos)
    else:
        return getNextWord(random.choice(lookup[pos]), pos)


def cleanSentence(sentence):
    # Move possesives such as 's to the word without a space.
    #EX: [Anthony 's] => [Anthony's]
    sentence = sentence.replace(" '", "'")

    # Move punctuations to follow the word without a space.
    #EX: [word .] => [word.]
    sentence = sentence.replace(" .", ".")
    sentence = sentence.replace(" !", "!")
    sentence = sentence.replace(" ?", "?")
    sentence = sentence.replace(" ,", ",")


    #Capitalize the first Letter of the first word
    #EX: [the quick brown fox.] => [The quick brown fox.]
    sentence = sentence.capitalize()

    #Capitalize single i's
    #EX: [I think i can] => [I think I can]
    sentence = sentence.replace(' i ', ' I ')

    return sentence


def isAcceptable(sentence):
    wordList = sentence.split(' ');

    # Accept only sentences longer than 4 words
    if len(wordList) < 5:
        return False

    # Accept only sentences with non-repeating words
    for i in range(len(wordList)-1):
        if wordList[i] in wordList[i+1] or wordList[i+1] in wordList[i]:
            return False

    return True

def makeSentence():
    posOrder = []
    currentPos = getStartingPos()
    posOrder.append(currentPos)

    sentenceWords = []

    prevWord = chooseRandomWordWithPos(currentPos)
    sentenceWords.append(prevWord)

    while currentPos not in endPunctuations:
        currentPos = getNextPos(currentPos)

        (nextWord, nextPos) = getNextWord(prevWord, currentPos)
        if nextWord in words.keys():
            sentenceWords.append(nextWord)
            posOrder.append(nextPos)
            prevWord = nextWord
            currentPos = nextPos

    sentence = ' '.join(sentenceWords)

    sentence = cleanSentence(sentence)

    if isAcceptable(sentence):
        for pos in posOrder:
            print pos + " ",
        print
        return sentence
    else:
        return makeSentence()

def makeTrainingSentence():
    posOrder = []
    currentPos = getStartingPos()
    posOrder.append(currentPos)

    sentenceWords = []

    prevWord = chooseRandomWordWithPos(currentPos)
    sentenceWords.append(prevWord)

    while currentPos not in endPunctuations:
        currentPos = getNextPos(currentPos)

        (nextWord, nextPos) = getNextWord(prevWord, currentPos)
        if nextWord in words.keys():
            sentenceWords.append(nextWord)
            posOrder.append(nextPos)
            prevWord = nextWord
            currentPos = nextPos

    sentence = ' '.join(sentenceWords)

    sentence = cleanSentence(sentence)

    if isAcceptable(sentence):
        for pos in posOrder:
            print pos + " ",
        print
        print sentence
        return (sentenceWords, posOrder)
    else:
        return makeTrainingSentence()


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


def trainOnSentence((wordList, posOrder)):
    for i in range(0, (len(wordList) - 2)):
        words[wordList[i]][posOrder[i+1]][wordList[i+1]] += 1
        partsOfSpeech[posOrder[i]][posOrder[i+1]] += 1
    saveDictionary(words, partsOfSpeech, config['dictionaryFile'])




def train():
    print ".\n.\n.\n.\n.\n.\n."
    trainingArray = []
    for i in range(0, 5):
        print str(i+1) + ")\t",
        trainingArray.append(makeTrainingSentence())
        print
    print "[Enter -1 to quit]"
    response = raw_input("Enter sentences which made sense: ")

    if len(response) > 0:
        for i in response:
            if 'q' in i:
                return response
            else:
                i = int(i)
                if i > 0:
                    trainOnSentence(trainingArray[i-1])

    return response





def training():
    command = ''
    while 'q' not in command:
        command = train()


def saveDictionary(words, partsOfSpeech, name):
    content = {'meta': meta, 'words': words, 'partsOfSpeech': partsOfSpeech, 'lookup': lookup}
    with open('dictionaries/' + name,'w+') as contents:
        contents.write(json.dumps(content, indent=2))







################################################################################
#                         Run The Program                                      #
################################################################################
parseArguments(sys.argv)

(words, partsOfSpeech, lookup, meta) = loadDictionary(config['dictionaryFile'])

if config['training']:
    training()
else:
    generateSentences()
