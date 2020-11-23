#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#The two lines above are taken from Spyder's default output for a new file.

#10/17 OrderedDict syntax: https://www.geeksforgeeks.org/ordereddict-in-python/
#10/17 Some OrderedDict advice: http://gandenberger.org/2018/03/10/ordered-dicts-vs-ordereddict/
from collections import OrderedDict

import os
from os.path import join

import pandas as pd
import math

import datetime
#10/31: https://www.programiz.com/python-programming/datetime/current-datetime



#Please see citations in imports.py file
import sys
code_path = '/Users/nicolewong/Desktop/urop/code'
sys.path.insert(1, code_path) 

import imports
imports.import_files()

#My imports
import cand_chunks_funcs as cand_chunks_gen
import decoding_funcs
import formatting_funcs as formatting

import special_cases

######### DECODING SECTION #########

def which_entire_decoded(cand_chunks, true_chunks_set):
    
    return None #Disable before clarification

    """
    Inputs: cand_chunks, true_chunks_set, Dict and Set information about chunks
    Returns a set of words that were decoded (were not in true_chunks_dict)
    """
    
    all_words = set(cand_chunks['entire'].keys())
    return (all_words - true_chunks_set)
    

def post_chunk_filter_examples(filter_set, this_subchunks_dict):
    """
    "Copies" the subchunk Dict such that words
        in the filter_set, a Set of str,
            will no longer be present as examples in this_subchunks_dict, a Nested Dict.
    If a given chunk no longer has any examples, it is deleted from the dictionary.
    Note however, this is not a deep copy!
    """


    return None #Disable this for now before clarification.

    #11/8/20: Advice on fast Dict processing
    #   https://stackoverflow.com/questions/22668574/python-fastest-strategy-for-remove-a-lot-of-keys-from-dict
    
    new_subchunks = OrderedDict()
    
    for word in filter_set:
        for chunk_graph, chunk_info in this_subchunks_dict.items():
            this_examples = chunk_info['examples']
            if word in this_examples: 
                del(this_examples[word])
    
    for chunk_graph, chunk_info in this_subchunks_dict.items():
        this_examples = chunk_info['examples']
        if not this_examples: #No more examples
            continue
        new_subchunks[chunk_graph] = chunk_info #With the mutation 
        #Above: Then this chunk is no longer needed to decode words.
     
    return new_subchunks
                
    
def find_sight_chunks(cand_chunks):
    
    chunk_types = ['pre', 'post', 'entire']
     
    true_chunks_dict = {key: OrderedDict() for key in chunk_types}
    #Above: this should guarantee acceptance order for added chunks.
    #However, my version of Python already has ordered normal Dict.
    true_chunks_set = {key: set() for key in chunk_types}
    
    chunk_storage = (cand_chunks, true_chunks_dict, true_chunks_set)
     
    for key in chunk_types:
        true_chunks_dict = find_sight_subchunks(key, *chunk_storage)
    
    
    #Disabled post-decoding filtering for now until can clarify understanding.
    
    #Filter prefixes, postfixes that only represent entire words that were decoded.
    #decoded_words = which_entire_decoded(cand_chunks, true_chunks_set['entire'])
    
    #for key in ['pre', 'post']:
    #    true_chunks_dict[key] = post_chunk_filter_examples(decoded_words, true_chunks_dict[key])
    
    final_chunks = formatting.select_top_examples(true_chunks_dict)
     
    return final_chunks
    
def try_update_chunks(this_chunk_graph, this_chunk, chunk_type,\
                      decode_fn,\
                      true_chunks_set, true_chunks_dict):
    """
    Attempts to records and mutates the true_chunks_dict, true_chunks_set to contain
        the new chunk.
    If the proposed chunk is regular, it simply returns the original
        data records without mutation.
        
    Inputs:
        this_chunk_graph, a str, the grapheme to be added
        this_chunk, a Dict with the information about this_chunk_graph
        chunk_type, a str, 'pre', 'post' or 'entire', the type of the chunk
        decode_fn, the decoding function to be used.
        true_chunks_set, true_chunks_dict, Dict, the "memory" of all chunks
            sorted into sub-OrderedDicts of 'pre', 'post', 'entire'
    """
        
    this_ipa = this_chunk['P']
    this_score = this_chunk['score']
    
    this_chunk_graph = special_cases.filter_double_consonant(this_chunk_graph)
    decoded_ipa = decode_fn(this_chunk_graph,\
               true_chunks_set, true_chunks_dict)
        
    #Note that the "oi -> ɔɪ" pg pair is considered decodable,
    #   so it will be decoded in this case.
    
    if decoded_ipa != this_ipa: #If is not regular
        
        true_chunks_set[chunk_type].add(this_chunk_graph)
        true_chunks_dict[chunk_type][this_chunk_graph] = {
            'P': this_ipa,
            'Decoded P': decoded_ipa,
            'score': this_score,
            'examples': this_chunk['examples']
            }
        
    return true_chunks_set, true_chunks_dict
            
            
def find_sight_subchunks(chunk_type, cand_chunks, true_chunks_dict, true_chunks_set):
    """
    Inputs:
        chunk_type, str, 'pre' or 'post' or 'entire', the type of chunk class.
        cand_chunks, the result of candidate_chunks
        true_chunks_dict, true_chunks_set,
            the Dict and Set containing the chunks (prefix, postfix) already found so far.
    Outputs:    
        sight_chunks Dict:
            Key: grapheme sight chunks
            Value: a Dict
                'examples': List of [words with this sight chunk]
                'score': Given by the candidate chunk info.
    """
    
    #Sort the candidate chunks by size.
    sub_cand_chunks = cand_chunks[chunk_type]
    
    order_word_chunks = list(sub_cand_chunks.keys())
    
    order_word_chunks.sort(key = len)

 
    this_decoding_func = {
        'pre':decoding_funcs.decode_prefix,
        'post': decoding_funcs.decode_suffix,
        'entire': decoding_funcs.decode_alt
        }
    
    #Run candidate chunks through the is_regular function.
    for this_chunk_graph in order_word_chunks:
        this_chunk = sub_cand_chunks[this_chunk_graph]
        #Note -- the try_update_chunks mutates, not copies, the Dict and Set
        true_chunks_set, true_chunks_dict = try_update_chunks(this_chunk_graph, this_chunk,
                                                              chunk_type, this_decoding_func[chunk_type],
                                                              true_chunks_set, true_chunks_dict)

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
            #11/21: Encoding problems: https://forum.openoffice.org/en/forum/viewtopic.php?f=9&t=69798
            #11/21: Working with CSV encoding: https://stackoverflow.com/questions/25788037/pandas-df-to-csvfile-csv-encode-utf-8-still-gives-trash-characters-for-min/43684587
            accept_final_chunk_df.to_csv(save_path+'_accept_order.csv', encoding = 'utf-8')
            score_final_chunk_df.to_csv(save_path+'_score_order.csv', encoding = 'utf-8')
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

def check_if_no_2_ipa(data_df):
    """
    Checks to ensure that no words appear twice in the DataFrame
        (i.e. no word has two pronunciations, or code
             may not be appropriate.)
    """
    
    all_df = list(data_df['Word'])
    set_all_df = set(all_df)

    return len(all_df) == len(set_all_df)

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
    
    assert check_if_no_2_ipa(data_df),\
        'Some word appeared twice in the DataFrame.'
        
    this_cand_chunks = cand_chunks_gen.candidate_chunks(data_df)
    
    num_cand_chunks = sum(len(this_cand_chunks[key]) for key in this_cand_chunks)
    print('Candidate chunks length (including full words)', num_cand_chunks)
    
    final_chunks = find_sight_chunks(this_cand_chunks)
    
    prefix_chunk_df, _ = create_chunks_df(final_chunks['pre'], save_path+'_prefix'\
                                          if to_save else '')
    postfix_chunk_df, _ = create_chunks_df(final_chunks['post'], save_path+'_postfix'\
                                           if to_save else '')
    entire_chunk_df, _ = create_chunks_df(final_chunks['entire'], save_path+'_entire'\
                                           if to_save else '')
    
    actual_chunks = set(final_chunks['pre'].keys()) |\
        set(final_chunks['post'].keys()) |\
            set(final_chunks['entire'].keys())
        
    print('Final chunks length', len(actual_chunks))
    print('Prefixes', len(final_chunks['pre']))
    print('Postfixes', len(final_chunks['post']))
    print('Entire', len(final_chunks['entire'])) 
    
    return prefix_chunk_df, postfix_chunk_df, entire_chunk_df

    
if __name__ == '__main__':
    
    #10/31: https://www.programiz.com/python-programming/datetime/current-datetime
    today_date = str(datetime.date.today())
    
    #11/8: For directory help:
    #https://superuser.com/questions/717105/how-to-show-full-path-of-a-file-including-the-full-filename-in-mac-osx-terminal/1533160
    
    DATA_DIR = '/Users/nicolewong/Desktop/urop/Data'
    DATA_PATH = join(DATA_DIR, 'popular_words_shift.csv')
    result_folder = os.path.join(DATA_DIR, today_date)
    
    if not os.path.exists(result_folder):
        os.makedirs(result_folder)
        
    RESULT_PATH = join(result_folder, 'pre_post_alt_no_postfilter')
    result_chunks_df = gen_save_chunks(DATA_PATH, RESULT_PATH, to_save = True)
    
    print('Chunks generated and saved. Complete.')
    
if __name__ == '__gmain__':
    pass
    
    
    
        
    
        
     