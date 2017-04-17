import re
import sys
import unicodedata
from collections import defaultdict


'''
converts concordance-style dictionary into dictionary from
key => (# of occurrences) to
key => (occurrences / # of keys in dict)
'''
def makeProbDict(dictionary):
    dictType = type(list(dictionary.values())[0])
    probDict = defaultdict(dictType)
    probDict = {}
    ks = dictionary.keys()

    for k in ks:
        probDict[k] = dictionary[k] / len(ks)

    return probDict



'''
bigrams = makeBigrams(sentences)

takes a string consisting of sentences from which to extract bigrams

returns bigram model represented as dictionary of
(string, string) => # of occurrences
'''

def makeBigrams(sentences):
    sentences = [s for s in sentences if s != '']
    bigrams = defaultdict(int)

    # split sentences into words

    for s in sentences:
        s = cleanupString(s)

        s = str.upper(s)
        s = re.split(r'[,\s]\s*', s)
        s = [w for w in s if w != '']
        if len(s) == 1:
            bigrams[(s[0], '')] = bigrams[(s[0], '')] + 1
            continue

        # get each pair of consecutive words in each sentence
        for i in range(len(s) - 1):
            w1 = ' '.join(list(s[i]))
            w2 = ' '.join(list(s[i + 1]))
            b = (w1, w2)
            bigrams[b] = bigrams[b] + 1

    # record probability of each pair
    bigrams = makeProbDict(bigrams)

    return bigrams



def extractSentences(corpus):
    sentences = re.split(r'[,.?!:;]', corpus)
    return sentences



def extractWords(corpus):
    corpus = str.upper(corpus)

    # Beazley & Jones, Python Cookbook 3e
    words = re.split(r'[,.?!:;\s]\s*', corpus)

    words = [' '.join(list(w)) for w in words if w != '']

    return words



def concordance(wordList):
    conc = defaultdict(int)

    for w in wordList:
        conc[w] = conc[w] + 1

    return conc




def makeFsa(wordProbDict, bigramDict):
    fsa = 'F\n\n'
    for word, prob in wordProbDict.items():
        
        # insert transition from initial state => 
        # state corresponding to this word as start of sentence
        stateName = ''.join(list(word.split()))
        fsa = fsa + '(F (' + stateName + ' \"' + word + '\" ' + str(prob) + '))\n'
        fsa = fsa + '(' + stateName + ' (F *e* 0.001))\n'

        # insert transitions corresponding to bigrams in dictionary
        bigs = [((w1, w2), p) for ((w1, w2), p) in bigramDict.items() if w1 == word]
        for ((w1, w2), p) in bigs:
            nextStateName = ''.join(list(w2.split()))
            fsa = fsa + '(' + stateName + ' (' + nextStateName + ' \"' + w2 + '\" ' + str(p) + '))\n'
        fsa = fsa + '\n'

    return fsa



def removeChars(s, c):
    for sep in list(c):
        s = s.replace(sep, ' ')
    return s



def cleanupString(s):
    badchars = []
    for c in s:
        if ord(c) > 127:
            badchars.append(c)
    for c in badchars:
        s.replace(c, '')

    return s


if __name__ == '__main__':
    #corpus = 'Hello, world!!!  I am here; I am so glad to see you. How are you today? I am fine!'
    corpus = ''

    with open('smallcorpus.txt') as infile:
        corpus = infile.read()

    outfile = open('wsj.fsa', 'w')

    corpus = removeChars(corpus, '~`@#$%^&*()-+=:;\"[]{}|/\\1234567890')

    vocab = extractWords(corpus)

    bigrams = makeBigrams(extractSentences(corpus))

    conc = concordance(vocab)
    wordProb = makeProbDict(conc)

    fsa = makeFsa(wordProb, bigrams)
    
    print (fsa)
    outfile.write(fsa)


