#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 22 20:30:12 2020

@author: nicolewong
"""

#Used to handle special cases, such as double consonants or silent e.

def find_double_consonant_idxs(word):
    """
    Returns a List of ints,
        the idxs of the non-first repeated consonant
            in word, a str.
    """
    remove_idxs = []
    vowels = ['a', 'e', 'i', 'o', 'u']
    for idx in range(len(word)):
        if idx == 0:
            continue
        if word[idx-1] == word[idx] and not (word[idx] in vowels):
            remove_idxs.append(idx)
    
    return remove_idxs

def filter_double_consonant(word):
    """
    Return filtered_word, str, with double consonants removed.
    """
    
    remove_idx = set(find_double_consonant_idxs(word))
    chars = [char for char in word]
    
    new_word = []
    for idx in reversed(range(len(chars))):
        if idx not in remove_idx:
            new_word.append(chars[idx])
            
    new_word.reverse()
    new_word = ''.join(new_word)
    
    return new_word

if __name__ == '__main__':
    
    pass