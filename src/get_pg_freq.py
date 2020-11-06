import numpy as np
import math as math
import os as os


'''need to calculate the frequency of p-g pairs given words in word_freq.txt'''
# open word_freq.txt
word_freq_file = open(os.getcwd()+"/data/word-freqs.txt")
words = word_freq_file.read().splitlines()
word_freq_file.close()

# create a dictionary representation of words to frequencies
word_freq = {}
for word in words:
    w, f = word.split(' ')
    word_freq[w] = float(f)
#print(word_freq['sevens'])

#open phonix.txt
phonix_file = open(os.getcwd() + "/data/phonix.txt")
words_phonemes = phonix_file.read().splitlines()
phonix_file.close()

#create a dictionary representation of words to their p-g representation
pg_rep = {}
for word in words_phonemes:
    w, pg = word.split(' ')
    pg_rep[w] = pg
#print(pg_rep)

#find the words that are common to word_freq and to pg_rep
shared_words = set(word_freq.keys()).intersection(set(pg_rep.keys()))

#get the pg pairs of each word, multiply by the frequency of the word, and then output this somehow?
