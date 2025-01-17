#!/usr/bin/python
import sys, curses
from curses.ascii import isdigit 
from nltk.corpus import cmudict 

d = cmudict.dict() 

exc = {
    "sappy" : 2,
    "accelerondo" : 5,
    "contextual" : 3,
    "probably" : 3,
    "interest" : 3,
    "different" : 3,
    "our" : 2,
    "trying" : 2, #really? one syllable?
    "history" : 3,
}

def nsyl(word):
    if word.lower() in exc:
        return exc[word.lower()]
    if word.lower() in d:
        prons = [len(list(y for y in x if isdigit(y[-1]))) for x in d[word.lower()]]
        mn = 999
        for p in prons:
            if p < mn:
                mn = p
        return mn
    if "'" in word:
        return nsyl(word.replace("'",""))
    
if __name__ == "__main__":
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            print arg, "-->", nsyl(arg)
    else:
        for i in ["it's", "probably", "aren't", "us", "sappy"]:
            print i, nsyl(i), d[i]
