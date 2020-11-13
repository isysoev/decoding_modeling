import numpy as np
import math as math
import os as os

def get_pg_freq():
    # open word_freq.txt
    word_freq_file = open("../data/word-freqs.txt")
    words = word_freq_file.read().splitlines()
    word_freq_file.close()

    # create a dictionary representation of words to frequencies
    word_freq = {}
    for word in words:
        w, f = word.split(' ')
        word_freq[w] = float(f)

    #open phonix.txt
    phonix_file = open("../data/phonix.txt")
    words_phonemes = phonix_file.read().splitlines()
    phonix_file.close()

    #create a dictionary representation of words to their p-g representation
    pg_rep = {}
    for word in words_phonemes:
        w, pg = word.split(' ')
        pg_rep[w] = pg

    #find the words that are common to word_freq and to pg_rep
    shared_words = set(word_freq.keys()).intersection(set(pg_rep.keys()))

    #Idea! split the shared words in pg_rep up by each `|` character to count how many of those specific pg pairs there are
    pg_freq = {}
    for word in shared_words:
        pgs = pg_rep[word].split("|")
        for pg in pgs:
            pg_freq.setdefault(pg, 0)
            pg_freq[pg] += word_freq[word] #check that this is the correct calculation

    #normalize the pg pair frequencies
    total_mass = sum(pg_freq.values())
    for pg in pg_freq.keys():
        pg_freq[pg] /= total_mass
    return pg_freq
