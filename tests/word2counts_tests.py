#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 21 21:30:15 2020

@author: nicolewong
"""

import pandas as pd
import numpy as np

#11/8: managing the imports
#https://stackoverflow.com/questions/4383571/importing-files-from-different-folder
#11/8: For directory help: 
#https://superuser.com/questions/717105/how-to-show-full-path-of-a-file-including-the-full-filename-in-mac-osx-terminal/1533160
import sys
code_path = '/Users/nicolewong/Desktop/urop/code'
sys.path.insert(1, code_path)
#end code

import imports
imports.import_files()

import word2counts
import os 

from os.path import join

#Testing for word2counts.py


def give_case():
    """
    Outputs DataFrame for testing ise.
    """
    
    test_data = {
        'Word': ['ab', 'c', 'aba', 'baa'],
        'P': ['kn>a|l>b', 'm>c', 'bn>a|l>b|kn>a', 'l>b|bn>a|bn>a']
        } 
    
    df = pd.DataFrame.from_dict(test_data)
    return df

def check_extract_pg_types():

    df = give_case()
    #Above: tests for disjoint on same grapheme, duplicate pg pair
    
    expected = ['m>c', 'l>b', 'bn>a', 'kn>a']
    
    actual = word2counts.extract_pg_types(df)
    
    assert actual == expected, 'Check all pg correctly extracted incorrect.'
    

def check_word_data2counts():
    
    df = give_case()
    
    for i, j in enumerate(df):
        print(i, j)
        
    #Above: will test for multiple, one, and none of a particular pg present.
    
    counts = [
        [0, 1, 0, 1],
        [1, 0, 0, 0],
        [0, 1, 1, 1],
        [0, 1, 2, 0]
        ]
    
    expected_words = list(df['Word'])
    expected_counts = np.array(counts)
    
    _, actual_words, actual_counts = word2counts.word_data2counts(df)
    

    assert np.all(expected_words == actual_words),\
        'Words did not match in word_data2counts'
    
    print(actual_counts)
    
    assert np.all(expected_counts == actual_counts),\
        'Counts did not match in word_data2counts'
    
    
def manual_large_spot_check():
    
    data_folder = '/Users/nicolewong/Desktop/urop/Data'
    word_path = join(data_folder, 'popular_words_shift.csv')
    counts_folder = join(data_folder, 'model/counts')
    
    counts = np.load(join(counts_folder, 'counts.npy'))
    arr_words = np.load(join(counts_folder, 'words.npy'))
    pg_order = np.load(join(counts_folder, 'pg_idx.npy'))
    
    
    words = pd.read_csv(word_path)
    
    test_idxs = [0, 14, 160, 1008, 2102]
    
    for test_idx in test_idxs:
        entry = words.iloc[test_idx]
        this_word, this_actual_counts = arr_words[test_idx], counts[test_idx]
        
        assert entry['Word'] == this_word,\
            "Order of Numpy and CSV for words doesn't match."
                
        this_ipa = entry['P'] 
        where_pg = np.where(counts[test_idx])[0]
        
        print('IPA', this_ipa)
        print('IPA represented in counts', np.take(pg_order, where_pg))
        print('Where the counts were:', np.take(counts[test_idx], where_pg))
        print() 
    
if __name__ == '__main__':
    
    #check_extract_pg_types() 
    #check_word_data2counts()
    manual_large_spot_check()