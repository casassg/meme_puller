# -*- coding: utf-8 -*-
"""
Created on Thu Apr 26 12:30:57 2018

@author: NSing
"""

import json
from nltk.corpus import wordnet
from autocorrect import spell
from nltk.metrics import edit_distance

with open('results.json', 'r') as fp:
    data = json.load(fp)
    
dataslice = data.copy()
newdata = []


def fixstring(string):
    # no string, return
    if len(string) == 0:
        return string
    # split words in string
    else: stringlist = string.split()
    
    # add stuff to new string
    newstring = ''; old_st = ''
    for st in stringlist:
        # drop repeats
        if st == old_st: continue
        old_st = st
        # determine if real word
        if wordnet.synsets(st):
            newstring += st + ' '
            continue
        # determine if almost a real word
        try:
            fixword = spell(st)
            if wordnet.synsets(fixword): # word is now real
                # only keep words that are 3 or less edits apart from real
                if edit_distance(st, fixword) < 4:
                    newstring += fixword + ' '
                continue
        except: pass
        # determine if number
        try: 
            float(st)
            # only keep smaller numbers
            if len(st) < 4:
                newstring += st + ' '
            continue
        except: pass
        # determine if money or percent
        if '$' in st or '%' in st:
            money = st.replace('$','').replace('%','')
            try: 
                float(money)
                newstring += st + ' '
                continue
            except: pass
        # if proper noun, keep
        if edit_distance(st, st.lower()) == 1:
            if all(char.isalpha() for char in st):
                newstring += st + ' '
            continue
    # return fixed string
    return newstring

# itterate through all stuff
counter = 0; distance = len(dataslice)
for infos in dataslice:
    newslice = []
    for info in infos:
        if type(info) == str:
            newslice.append(fixstring(info))
        elif type(info) == list:
            newlist = []
            for strings in info:
                newlist.append(fixstring(strings))
            newslice.append(newlist)
    newdata.append(newslice)
    counter += 1
    print("\r", 'Fixing strings: '+str(counter)+' of '+str(distance)+' ('+str(100*counter/distance)+'%)', end="")
            

# save
with open('fixed_results.json', 'w') as fp:
    json.dump(newdata, fp)