#!/usr/bin/python
# encoding: utf-8

import random
import csv
import json
import wikipedia
import re

################################################################################
#                         Constant Definitions                                 #
################################################################################
punctuationMap = {
    ',': "<<COMMA>>",
    '.': "<<PERIOD>>",
    '!': '<<EXCLAMATION>>',
    '?': '<<QUESTION>>',
    ':': '<<COLON>>'
    }
finalizeMap = {
    '<<QUESTION>>': '?',
    '<<EXCLAMATION>>': '!',
    '<<PERIOD>>': '.',
    '<<COMMA>>': ',',
    '<<COLON>>': ':'
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
    firstWord = firstWord.lower().replace("\n", '').replace('.', '')
    secondWord = secondWord.lower().replace("\n", '').replace('.', '')
    firstWord.replace('"', ' ')
    secondWord.replace('"', ' ')

    if firstWord != "" and secondWord != "":
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
    input = input.replace("\n", ' ')
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
    word = word.lower()
    def makeSentenceHelper(word, sentenceParts):
        if isFullStop(word):
            sentenceParts.append(word)
            return sentenceParts
        else:
            sentenceParts.append(word)
            nextWord = chooseNextWord(word.lower())
            if (nextWord.lower() == '<<comma>>'):
                sentenceParts.append('<<comma>>')
                while (nextWord.lower() == '<<comma>>'):
                    nextWord = chooseNextWord(word)
            return makeSentenceHelper(nextWord, sentenceParts)
    try:
        parts = makeSentenceHelper(word, [])
    except KeyError:
        parts = makeSentenceHelper(word, [])

    sentence = ' '.join(parts)


    sentence = finalize(sentence)

    return sentence

def crawlAndLearn(topic):
    search = wikipedia.search(topic, results=5)
    for page in search:
        print "Learning about: " + page
        try:
            article = wikipedia.page(page)
            content = re.sub(r'=+\sSee also\s=+.+$', ' ', article.content, flags=re.M | re.S)
            content = re.sub(r'=+\s.+\s=+', ' ', content)
            content = re.sub(r'\(.+\)', ' ', content, flags=re.M | re.S)
            #print content
            iterateInput(content)
        except wikipedia.exceptions.DisambiguationError:
            content = ""
        except wikipedia.exceptions.PageError:
            content = ""



def learnAbout(topics):
    try:
        for topic in topics.split(): # string case
            crawlAndLearn(topic)
    except AttributeError:
        for topic in topics:
            crawlAndLearn(topic)






################################################################################
#                         Run The Program                                      #
################################################################################
# dictionary = loadDictionary()
dictionary = {}

# testString = getFileContents('input.txt')
# iterateInput(testString)

# chooseNextWord('united')
# chooseNextWord('the')
# print chooseNextWord('has')
# print makeSentence('an')
learnAbout('Minnesota')
print makeSentence(random.choice(dictionary.keys()))


saveDictionary(dictionary)
