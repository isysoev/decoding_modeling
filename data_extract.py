#Filter code to only consider intersection of texts.
#Extraction of most frequent words for initial analysis.

import os
import pandas as pd
from os.path import join

############################
######## FILTERING #########
############################
    
def get_word_data_dict(this_df, intersection_words):
    """
    Extracts the data related to the intersection of the two sets of words.
    Assumes:
        that this_df has only two columns:
            first column: word
            second column: one piece of data related to word.
    Inputs:
        this_df, a DataFrame
        intersection_words, a Set of Strings, the words found in
            both datasets.
    Outputs:
        word_to_data, a Dictionary:
            key - a String, the word
            value - the information from this_df associated with the word,
                in a List (used for concatenation later)
                    and in case of multiple pronunications (should not happen)
    """
    
    #10/3: Methodology inspired by:
    #   https://stackoverflow.com/questions/4664850/how-to-find-all-occurrences-of-a-substring
    
    word_to_data = {}
    added_words = set()
    for i, word in enumerate(this_df.iloc[:, 0]):
        
        if not word in intersection_words:
            continue #Not valid for use.
        
        this_data = this_df.iloc[i][1]
        if word in added_words:
            #Check to ensure that no exact duplicates of information
            #   are entered into the dictionary (e.g. same frequency
            #       or same pronunication.)
            if word_to_data[word] == this_data:
                #If the old data is identical to new data
                continue #Don't store any new data.
                
        #If valid word
        word_to_data.setdefault(word, []).append(this_data)
        #  Above is to catch multiple pronunications.
        #   There should not be any as I checked,
        #       but I preferred to protect against loss of data.
        added_words.add(word)

    return word_to_data

def merge_intersection_data(phonix_df, freq_df, intersection_words, FINAL_PATH):
    
    """
    Merges the results of extracting relevant data from each dataset
        to produce and write the final intersection dataset.
    Inputs:
        phonix_df, freq_df, DataFrames
        intersection_words, a Set of Strings produced by _find_intersection
        FINAL_PATH, the String full path of where to write final dataset
    """
    
    sub_phonix_data = get_word_data_dict(phonix_df, intersection_words)
    sub_freq_data = get_word_data_dict(freq_df, intersection_words)
    
    sub_final_data = {}
    
    for this_word in sub_phonix_data:
    
        this_phonix_info = sub_phonix_data[this_word]
        this_freq_info = sub_freq_data[this_word]
        
        if len(this_freq_info) != 1:
            print('Frequency list has duplicates, contrary to assumption.')
            #It was observed that NaN at index 25848 with frequency 3.9443e-07 appeared.
            #As well as NaN at 0.00012839.
            #However, when searching in the actual text file,
            #Neither of these values were able to be found.
            #Therefore, these values are being dropped.
            print('Discarding this input -- see comment in code.')
            continue
        
        sub_final_data[this_word] = \
            this_freq_info + this_phonix_info
    
    #10/3: Advice on conversion to DF:
    #https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.from_dict.html
    
    final_df = pd.DataFrame.from_dict(sub_final_data, orient = 'index')
    
    final_df.to_csv(FINAL_PATH)
    
    print('Merged CSV written to {}'.format(FINAL_PATH))   
    return final_df
        
def intersection_texts(PHONIX_PATH, FREQ_PATH, FINAL_PATH):
    
    """
    Performs all of the functions related to intersection and writing the datasets.
    """
    
    def _get_intersection():
        
        #Note that below requires re-save of data as .csv.    
        phonix_words = set(phonix_df.iloc[:, 0])
        freq_words = set(freq_df.iloc[:, 0])
        
        intersection_words = phonix_words & freq_words
    
        return intersection_words 
    
    
    phonix_df = pd.read_csv(PHONIX_PATH, " ", \
                            header = None)
    freq_df = pd.read_csv(FREQ_PATH, " ", \
                            header = None)

    intersection_words = _get_intersection()
    final_df = merge_intersection_data(phonix_df, freq_df, intersection_words, FINAL_PATH)
    
    return final_df 

def find_duplicates(df_path):
    #For debugging use only.
    #Note that dept, mi, and sec are all simply misentered twice.
    #Instead, there should be no multiple pronunications provided.
    
    this_df = pd.read_csv(df_path, delimiter = " ", header = None)
    
    index_dict = {}
    duplicate_dict = {}
    visited = set()
    
    for i, word in enumerate(this_df.iloc[:, 0]):
        if word in visited:
            duplicate_dict[word] = i
        else:
            visited.add(word)
            index_dict[word] = i
                       
    if len(duplicate_dict) > 0:
        print('Duplicates:')
        for word in duplicate_dict:
            print(this_df.iloc[duplicate_dict[word]])
            print(this_df.iloc[index_dict[word]])
            print()
    else:
        print('No duplicates.')
        
#10/30/20: Reminder on syntax for method header:
#   https://docs.python.org/3/library/__main__.html

if __name__ == '__main__':
    
    
    TXT_PATH = '../Data'
    PHONIX_PATH = join(TXT_PATH, 'phonix.csv')
    FREQ_PATH = join(TXT_PATH, 'word-freqs.csv')
    FINAL_PATH = '../Data/phonix_word_freqs.csv'  
    
    final_intersection_df = intersection_texts(PHONIX_PATH, FREQ_PATH, FINAL_PATH)
    
    
        
        