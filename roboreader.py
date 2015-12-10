#!/usr/bin/python
# encoding: utf-8

import random
import csv
import json

################################################################################
#                         Constant Definitions                                 #
################################################################################
punctuationMap = {
    ',': "<<COMMA>>",
    '.': "<<PERIOD>>",
    '!': '<<EXCLAMATION>>',
    '?': '<<QUESTION>>'
    }
finalizeMap = {
    '<<QUESTION>>': '?',
    '<<EXCLAMATION>>': '!',
    '<<PERIOD>>': '.',
    '<<COMMA>>': ','
    }

################################################################################
#                         Function Definitions                                 #
################################################################################

def saveDictionary(dictionaryToSave):
    with open('dictionary','w+') as contents:
        contents.write(json.dumps(dictionaryToSave, indent=2))

def loadDictionary():
    with open('dictionary','r') as contents:
        dictionary = json.loads(contents.read())
    return dictionary

def addWord(firstWord, secondWord):
    firstWord = firstWord.lower()
    secondWord = secondWord.lower()
    firstWord.replace('"', '')
    secondWord.replace('"', '')

    if firstWord in dictionary:
        if secondWord in dictionary[firstWord]:
            dictionary[firstWord][secondWord] += 1
        else:
            dictionary[firstWord][secondWord] = 1
    else:
        dictionary[firstWord] = {}
        dictionary[firstWord][secondWord] = 1

def hasPunctuation(word):
    if word[-1:] in punctuationMap:
        return True
    else:
        return False

def isFullStop(word):
    if word.lower() in ['<<period>>', '<<question>>', '<<exclamation>>']:
        return True
    else:
        return False

def getPunctuation(word):
    return punctuationMap[word[-1:]]

def removePunctuation(word):
    return word[:-1]

def getFileContents(filename):
    if not filename == '':
        with open (filename, "r") as myfile:
            data=myfile.read().replace('\n', ' ')
        return data
    else:
        return ""

def getNextWordSuggestions(word):
    return dictionary[word]

def chooseNextWord(word):
    choices = getNextWordSuggestions(word)

    totalWeight = 0
    currentWeight = 0
    weightedArray = []

    for choice in choices:
        totalWeight += int(choices[choice])
        for i in range(0, choices[choice]):
            weightedArray.append(choice)
    return random.choice(weightedArray)

def iterateInput(input):
    words = input.split(" ")
    for i in range(0, (len(words)-1)):
        word = words[i]
        nextWord = words[i+1]

        word = ''.join([i if ord(i) < 128 else '' for i in word])
        nextWord = ''.join([i if ord(i) < 128 else '' for i in nextWord])

        if hasPunctuation(word):
            punctuation = getPunctuation(word)
            word = removePunctuation(word)
            addWord(word, punctuation)

        if hasPunctuation(nextWord):
            punctuation = getPunctuation(nextWord)
            nextWord = removePunctuation(nextWord)

        addWord(word.lower(), nextWord.lower())

def finalize(sentence):
    sentence = sentence.capitalize()
    sentence = sentence.replace(' <<', '<<')
    for mark in finalizeMap:
        sentence = sentence.replace(mark.lower(), finalizeMap[mark])
    return sentence

def makeSentence(word):
    def makeSentenceHelper(word, sentenceParts):
        if isFullStop(word):
            sentenceParts.append(word)
            return sentenceParts
        else:
            sentenceParts.append(word)
            nextWord = chooseNextWord(word)
            if (nextWord.lower() == '<<comma>>'):
                sentenceParts.append('<<comma>>')
                while (nextWord.lower() == '<<comma>>'):
                    nextWord = chooseNextWord(word)
            return makeSentenceHelper(nextWord, sentenceParts)
    parts = makeSentenceHelper(word, [])
    sentence = ' '.join(parts)


    sentence = finalize(sentence)

    return sentence






################################################################################
#                         Run The Program                                      #
################################################################################
dictionary = loadDictionary()

testString = getFileContents('input.txt')
iterateInput(testString)

# chooseNextWord('united')
# chooseNextWord('the')
# print chooseNextWord('has')
print makeSentence('the')


saveDictionary(dictionary)
