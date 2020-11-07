
#10/17 OrderedDict syntax: https://www.geeksforgeeks.org/ordereddict-in-python/
#10/17 Some OrderedDict advice: http://gandenberger.org/2018/03/10/ordered-dicts-vs-ordereddict/
from collections import OrderedDict

import os
import pandas as pd

import random

import datetime
#10/31: https://www.programiz.com/python-programming/datetime/current-datetime
from datetime import date

import math
import numpy as np

from collections import defaultdict 

#My imports
from CandChunkInfo import *
from CandChunks import *
import decoding_filtering_funcs as filtering

from KeyValuePair import *


####### GENERATE CANDIDATES #######

def _update_word_candidate_chunks(df_word, cand_chunks):
    """
    Generates the p/g prefixes and suffixes of a word.
    Inputs:
        df_word, an entry in the DataFrame
        cand_chunks, a Dict of two CandChunks objects
            keys: 'pre' or 'post'
                    Note: entire words are added to both dictionaries.
    Outputs: None, but will mutate the dictionary cand_chunks
        to reflect the p/g frequencies/scores/pairs contributed
            by the word.
    """
    #Verified: prefix, suffix generation.
    
    info = df_word['P'].split('|') #See assumption in check_if_all_nan.
    #   Above splits into the p/g pairs.
    
    #Take prefixes and update.
    for end_idx in range(1, len(info)):
        
        #Note that this stops one end idx short of the full word
        #   But that full word is covered in the suffix
        prefix_list = info[:end_idx]
        cand_chunks['pre'].add(prefix_list, df_word)
    
    for start_idx in range(len(info)):
            
        suffix_list = info[start_idx:]
        cand_chunks['post'].add(suffix_list, df_word)

        #Mark full words as a prefix as well.
        if start_idx == 0:
            cand_chunks['pre'].add(suffix_list, df_word)
            
            
def candidate_chunks(data_df):
    """
    Generates candidate chunks from information
        in the popular_words.csv as a DataFrame.
    Importantly, returns the dictionary of final word-pronunciation
        selections to maximize score.
        
    Inputs:
        data_df, a DataFrame with the words to be processed.
    Outputs:
        final_chunks, a nested Dictionary with two nested Dictionaries,
            'pre': the Candidate Chunks that are prefixes
            'post': the Candidate Chunks that are postfixes
            Each of these dictionaries contains the following:
                    Keys: the chunk grapheme (String)
                    Values: a Dict,
                        Keys:
                            'P' -> a String IPA pronunciation
                            'score' -> a number, the score of the pronunciation
                            'examples' -> a Dict,
                                Keys: a word with this chunk, a String
                                Values: the score of that word, a number 
    """
    
    cand_chunks = {'pre': CandChunks(), 'post': CandChunks()}
    for i in range(len(data_df)):
        _update_word_candidate_chunks(data_df.iloc[i], cand_chunks)
    
    
    #Selects the top pronunication to use.
    top_ipa_chunks = {cand_type: each.give_argmax_pronunications()\
                    for cand_type, each in cand_chunks.items()}
    
    #Performs length-delayed filtering.
    length_filtered_chunks = {cand_type: filtering._filter_length_chunks(each, (cand_type == 'pre'))\
                              for cand_type, each in top_ipa_chunks.items()}
    
    #Finally, select the top words.
    for cand_type, each in length_filtered_chunks.items():
        for chunk_key, chunk in each.items():
            chunk['examples'] = filtering._format_examples(chunk)
    
    final_chunks = length_filtered_chunks
    return final_chunks

####### END GENERATE CANDIDATES #######


####### DECODING AND CHUNK SELECTION #######

def is_regular_original(cand_graph, cand_ipa, true_chunk_set, true_chunk_dict):
    """
    NOTE: Integration and proper working not guaranteed in this version,
        because this was written before the split of pre/postfix occurred!
        
    Inputs: cand_graph, the grapheme to be considered (String)
            cand_ipa, the pronunciation of above.
            true_chunk_set, the Set of currently chosen sight chunks
            true_chunk_dict, the dictionary of the current
                list of sight chunks.
    Outputs: a Boolean, whether the sight chunk is
        explainable by current chunks. 
    """
    
    #While word not completely decoded
    decoded_ipa_list = []
    curr_start_idx = 0 #Where to start decoding at.
    
    while curr_start_idx != len(cand_graph):
            
        this_ipa = ""
        result = _find_prefix_chunk(curr_start_idx, \
                                    cand_graph, true_chunk_set,\
                                        true_chunk_dict)
            
        if result is None:
            return False #Contains no prefix that can be found in the set
            #   Therefore can't be decoded.
        
        curr_start_idx, this_ipa = result
        decoded_ipa_list.append(this_ipa)
    
    decoded_ipa = ''.join(decoded_ipa_list)
    
    return decoded_ipa == cand_ipa


def _find_prefix_chunk(cand_chunk_rem, curr_chunk_set, curr_chunk_dict):
    """
    Inputs:
        cand_chunk_rem, String, the grapheme remnant to decode.
        curr_chunk_set, curr_chunk_dict,
            the current prefix-only chunk memory
    Returns:
            str, the remaining portion to decode,
            str, the pronunciation chunk found.
    """

    for end_idx in range(len(cand_chunk_rem), 0, -1):
        prefix = cand_chunk_rem[:end_idx]
             
        if prefix in curr_chunk_set: 
            return (cand_chunk_rem[end_idx:], curr_chunk_dict[prefix]['P'])
        
    return None #Indicates that prefix couldn't be found.

    
def _find_postfix_chunk(cand_chunk_rem, curr_chunk_set, curr_chunk_dict):
    
    """
    Inputs:
        cand_chunk_rem, String, the grapheme remnant to decode.
        curr_chunk_set, curr_chunk_dict,
            the current postfix-only chunk memory
    Returns:
        str, the remaining portion to decode,
        str, the pronunciation chunk found.
    """
    
    for start_idx in range(len(cand_chunk_rem)):
        postfix = cand_chunk_rem[start_idx:]
        
        if postfix in curr_chunk_set:
            this_ipa_piece = curr_chunk_dict[postfix]['P']
            return (cand_chunk_rem[:start_idx], this_ipa_piece)

    return None #Postfix couldn't be found.
    

def _find_cut_chunk(cand_chunk_rem, is_prefix_cut,\
                    curr_chunk_set, curr_chunk_dict):
    
    """
    Inputs:
        cand_chunk_rem,
            str, left to decode
        true_chunk_set,
            a Dict of sets either for prefixes or postfixes
                each value the Set of currently chosen sight chunks
        
        true_chunk_dict,
            a Dict of Dicts either for prefixes or postfixes
                each value the dictionary of the current
                    list of sight chunks.
    Outputs:
        Tuple: (str remaining to be decoded, str piece of pronunciation decoded)
        None if the str can't be decoded
    """
    
    which_key = 'pre' if is_prefix_cut else 'post'
    which_func =_find_prefix_chunk if is_prefix_cut else  _find_postfix_chunk
    
    info_args = (curr_chunk_set[which_key], curr_chunk_dict[which_key])
    
    return which_func(cand_chunk_rem, *info_args)

def _reconstruct_ipa_cuts(ipa_piece_list):
    """
    Reconstructs the decoded pronunciation
        stored in ipa_piece_list.
    Assumes that word was decoded by cutting prefix, then postfix, then prefix, repeatedly.
    """
    
    decoded_prefix = ''
    decoded_suffix = ''
    is_prefix_cut = True #Always start with a prefix cut.
    
    for piece in ipa_piece_list:
        if is_prefix_cut:
            decoded_prefix += piece 
        else:
            decoded_suffix = piece + decoded_suffix
        is_prefix_cut = not is_prefix_cut
            
    decoded_P = decoded_prefix + decoded_suffix
    return decoded_P
        
def decode_alt(cand_graph, true_chunk_set, true_chunk_dict):
    """        
    Inputs: cand_graph, the grapheme to be considered (String)
            
            true_chunk_set, a Dict of sets either for prefixes or postfixes
                each value the Set of currently chosen sight chunks
                
            true_chunk_dict, a Dict of Dicts either for prefixes or postfixes
                each value the dictionary of the current
                    list of sight chunks.
                    
    Outputs: str, a Boolean, whether the sight chunk is
        explainable by current chunks. 
    """
    
    memory_info = (true_chunk_set, true_chunk_dict)
    
    is_prefix_cut = True
    ipa_pieces = []
    #Above: Stored in alternating order: first prefix, last postfix, 2nd prefix, so on.
    
    next_decode = cand_graph 
    while next_decode: #Not empty
        next_decode_info = _find_cut_chunk(next_decode, is_prefix_cut, *memory_info)
        
        if next_decode_info is None:
            return None #Either no prefix or postfix removable. 
    
        next_decode, found_ipa_piece = next_decode_info
        
        ipa_pieces.append(found_ipa_piece)
        
        is_prefix_cut = not is_prefix_cut
        
    #Otherwise, word was deconstructed.
    decoded_ipa = _reconstruct_ipa_cuts(ipa_pieces)
    
    return decoded_ipa

def find_sight_chunks(cand_chunks):
    """
    Inputs:
        cand_chunks, the Dictionary output
            of give_argmax_pronunications
    Outputs:    
        sight_chunks Dict:
            Key: grapheme sight chunks
            Value: a Dict
                'examples': List of [words with this sight chunk]
                'score': Given by the candidate chunk info.
    """
    
    count = 0
    
    true_chunks_dict = {'pre': OrderedDict(), 'post': OrderedDict()}
    #Above: this should guarantee acceptance order for added chunks.
    #However, my version of Python already has ordered normal Dict.

    true_chunks_set = {'pre': set(), 'post': set()}
    
    #Sort the candidate chunks by size.
    order_cand_chunks = []
    for chunk_type, sub_cand_chunks in cand_chunks.items():
        #Mark prefixes and postfixes with separate values.
    
        these_graphemes = list(sub_cand_chunks.keys())
        
        these_grapheme_pairs = [KeyValuePair(grapheme, chunk_type)\
                                for grapheme in these_graphemes] #Second value: is prefix
        order_cand_chunks.extend(these_grapheme_pairs)
    
    #random.shuffle(order_cand_chunks)
        
    #Below sorting from 10/9: https://developers.google.com/edu/python/sorting
    order_cand_chunks.sort() #Sort so shortest comes first. (in KeyValuePair)

    #Run candidate chunks through the is_regular function.
    for pair in order_cand_chunks:
        
        this_chunk_graph, chunk_type = pair.return_pair()
        
        this_chunk = cand_chunks[chunk_type][this_chunk_graph]
        
        this_ipa = this_chunk['P']
        this_score = this_chunk['score']
        
        decoded_ipa = decode_alt(this_chunk_graph,\
                   true_chunks_set, true_chunks_dict)
            
        if decoded_ipa != this_ipa: #If is not regular

            true_chunks_set[chunk_type].add(this_chunk_graph)
            true_chunks_dict[chunk_type][this_chunk_graph] = {
                'P': this_ipa,
                'Decoded P': decoded_ipa,
                'score': this_score,
                'examples': this_chunk['examples']
                }
            
    return true_chunks_dict #In order of acceptance.

####### END DECODING AND CHUNK SELECTION #######


####### CSV WRITING AND SAVING #######
    
def create_chunks_df(final_chunks_dict, save_path = ''):
    """
    Converts the output of find_sight_chunks, a nested Dict,
        to the dataframe.
    Inputs: 
        final_chunks_dict, the nested Dict output of sight_chunks
        save_path, a String path to save the resultant DataFrame at
            (default signifies that no save is desired).
    Outputs:
        final_chunks_df, the DataFrame version of the input Dict
            also written to save_path (if save_path specified)
        wrote_success, if DataFrame was successfully written.
    """
    
    #10/11: DataFrame strategy:
    #   https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.from_dict.html
    #10/11: Advice on speed:
    #   https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.append.html
    
    list_keys = ['G', 'P', 'Decoded P', 'score', 'examples']
    list_cols = { key: [] for key in list_keys}
    
    def _update_list_one_chunk(grapheme, this_chunk_dict):
        """
        Updates the appropriate list with the information of Dict.
        Inputs:
            grapheme, String,
                the key value corresponding to this_chunk_dict
            this_chunk_dict, an element (Dict) of the output
                of the find_sight_chunks function.
        Outputs:
            None, but will append the information from the Dict
                to appropriate list.
        """
        this_chunk_dict['G'] = grapheme
        
        for key in list_keys:
            elem_dict_val = this_chunk_dict[key]
            list_cols[key].append(elem_dict_val)
        
    for this_grapheme, this_val in final_chunks_dict.items(): 
        _update_list_one_chunk(this_grapheme, this_val)
        
    #Write the lists. 
    final_chunk_df = pd.DataFrame.from_dict(list_cols)
    accept_final_chunk_df = final_chunk_df #Acceptance order.
    #10/11: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.sort_values.html
    score_final_chunk_df = final_chunk_df.sort_values('score', ascending = False)
    
    wrote_success = False

    if save_path:
        #10/11: https://stackoverflow.com/questions/5137497/find-current-directory-and-files-directory
        this_dir = os.path.dirname(save_path)
        if os.path.exists(this_dir):
            accept_final_chunk_df.to_csv(save_path+'_accept_order.csv')
            score_final_chunk_df.to_csv(save_path+'_score_order.csv')
            wrote_success = True
    if not wrote_success:
        print('The path {} did not exist, so nothing was saved.'.format(save_path))
        
    return final_chunk_df, wrote_success

####### END CSV WRITING AND SAVING #######

####### ASSUMPTION CHECK #######

def check_if_all_nan(data_df):  
    """
    Checks to ensure that P1 is really full of all NaNs.
    Returns bool, with answer to above.
    """
    
    #Because I discard the P1 for the first 5000 common words
    #   as it is all nan for these words.
    
    give = []
    for i in range(len(data_df)):
        word = data_df['P1'].iloc[i]
        if not isinstance(word, str) and math.isnan(word):
            #10/4: https://stackoverflow.com/questions/944700/how-can-i-check-for-nan-values
            continue
        give.append(word)
        
    return give == []


####### END ASSUMPTION CHECK #######

def gen_save_chunks(data_path, save_path, to_save = True):
    """
    The function to call to generate and save the final chunks.
    Inputs:
        data_path, the location of the DataFrame
            (popular_words.csv) with word information
        save_path, where to save the DataFrame, without the csv extension.
    Outputs:
        chunk_df, the resultant DataFrame with the following columns:
            'G', the grapheme chunk (String),
            'P', the IPA pronunciation (String),
            'score', the score for this chunk (number),
            'examples', a list of the highest frequency words
                with this chunk (String),
                    Formatted according to _gen_example_string.
    """
    
    print('Will {}attempt to save the output.'.format('not ' if not to_save else ''))
    
    data_df = pd.read_csv(data_path)
        
    assert check_if_all_nan(data_df), \
        'Has some multiple pronunications available. Assumption fails.'
        
    this_cand_chunks = candidate_chunks(data_df)
    
    num_cand_chunks = len(this_cand_chunks['pre']) + len(this_cand_chunks['post'])
    print('Candidate chunks length', num_cand_chunks)
    
    final_chunks = find_sight_chunks(this_cand_chunks)
    prefix_chunk_df, _ = create_chunks_df(final_chunks['pre'], save_path+'_prefix')
    postfix_chunk_df, _ = create_chunks_df(final_chunks['post'], save_path+'_postfix')
    
    num_final_chunks = len(final_chunks['pre']) + len(final_chunks['post'])
    print('Final chunks length', num_final_chunks)
    
    return prefix_chunk_df, postfix_chunk_df

if __name__ == '__main__':
    #I broke the 'main' name above to prevent accidental re-runs
    

    #10/31: https://www.programiz.com/python-programming/datetime/current-datetime
    today_date = str(datetime.date.today())
    
    DATA_PATH = '../Data/popular_words_shift.csv'
    result_folder = os.path.join('../Data', today_date)
    if not os.path.exists(result_folder):
        os.makedirs(result_folder)
    
    RESULT_PATH = os.path.join('../Data/'+today_date, 'popular_words_chunks_shift')
    result_chunks_df = gen_save_chunks(DATA_PATH, RESULT_PATH)
    
    print('Chunks generated and saved. Complete.')
    
if __name__ == '__gmain__':

    DATA_PATH = '../Data/popular_words.csv'
    RESULT_PATH = None
    #result_chunks_df = gen_save_chunks(DATA_PATH, RESULT_PATH, to_save = False)
    
    
    
    
        
    
        
     