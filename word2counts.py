#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 21 21:23:16 2020

@author: nicolewong
"""

#To save space, this is designed
#     to only process words in popular_words_shift.csv.

import numpy as np
import pandas as pd

import os
from os.path import join
 
def extract_pg_types(df):
  """
  Returns a sorted list (by length)
    of all pg pairs in df, a DataFrame.
  """

  all_pg_pairs = set()
  for this_p in df['P']:
    this_pairs = this_p.split('|')
    all_pg_pairs |= set(this_pairs)
    
  return sorted(list(all_pg_pairs), key = len)

def word2counts(ipa, pg_pairs):
    
    """
    Converts a word's pronunciation to a vector of counts. 
    Inputs:
      ipa, str, a phonix-style formatted pronunciation.
      pg_pairs, a predetermined list of pg pairs. The indices in the counts.
    Outputs:
      a Numpy array where each index corresponds
    to a different pg pair (as det. by pg_pairs)
    and each value is the number of times that pg pair appears in this word.
    """ 
    this_pairs = ipa.split('|')
    this_vec = np.zeros(len(pg_pairs), dtype = int)
      
    for pg_idx, pg in enumerate(pg_pairs):
        for this_pair in this_pairs:
            if this_pair == pg:
                this_vec[pg_idx] += 1
             
    return this_vec
  
def word_data2counts(df):
  """
  Converts words in DataFrame df
    to vectors of counts, indices determined by extract_pg_types
      where each vector indicates
        how many of each pg-pair type there are in the word.
  Returns Numpy arrays pg_arr, words, counts.
  """
  order_pgs = extract_pg_types(df)
  
  words = []

  counts = np.zeros((len(df), len(order_pgs)), dtype = int)
  for word_idx in range(len(df)):
    entry = df.iloc[word_idx]
    words.append(entry['Word'])
    this_ipa = entry['P']
    counts[word_idx] = word2counts(this_ipa, order_pgs)

  pg_arr = np.array(order_pgs)
  return pg_arr, np.array(words), counts

def gen_save_pg_counts(data_path, to_save = ''):
  """
  Saves pg counts of CSV data at data_path (str)
    as an h5py file.
    and returns the counts, a Numpy array
  Inputs:
    data_path, str, the CSV data location
    to_save (optional, default = ''): the location to save to.
  """
  df = pd.read_csv(data_path)
  pg_arr, words, counts = word_data2counts(df)

  if to_save:
      np.save(join(to_save, 'pg_idx.npy'), pg_arr)
      np.save(join(to_save, 'words.npy'), words)
      np.save(join(to_save, 'counts.npy'), counts)
      print(f'Saving words, counts to {to_save}.')

  return words, counts

if __name__ == '__main__':
    
    DATA_FOLDER = '/Users/nicolewong/Desktop/urop/Data'
    DATA_PATH = join(DATA_FOLDER, 'popular_words_shift.csv')
    
    OUTPUT_FOLDER = join(DATA_FOLDER, 'model/counts')
    
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    
    words, counts = gen_save_pg_counts(DATA_PATH, to_save = OUTPUT_FOLDER)

    