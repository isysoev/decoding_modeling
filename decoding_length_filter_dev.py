import os
import pandas as pd

import math
import numpy as np

from collections import defaultdict

#My own debugging import
from CandChunks import *
from CandChunkInfo import *
import decoding_test

"""
Need to change style of code for this to be more flexible/permanent.
Some docstrings may not be updated to be consistent with code.

Major changes since last decoding version:
    - added def set_is_pre_postfix, related functions
        and added lines to use this in candchunk generation.
    - added candchunklengthfilter function 
"""

####### GENERATE CANDIDATES #######
    
def _update_word_candidate_chunks(df_word, cand_chunks):
    """
    Generates the p/g prefixes and suffixes of a word.
    Inputs:
        df_word, an entry in the DataFrame
        cand_chunks, CandChunks object
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
        cand_chunks.add(prefix_list, df_word, is_prefix = True)
    
    for start_idx in range(len(info)):
            
        suffix_list = info[start_idx:]
        if start_idx == 0: #Mark entire words as prefix and postfix
            cand_chunks.add(suffix_list, df_word,\
                            is_prefix = True, is_postfix = True)
        else:
            cand_chunks.add(suffix_list, df_word, is_postfix = True)



def _gen_prefixes(word):
    """
    Generates all prefixes (excluding the entire word) of this word.
    Inputs: word, a String
    Outputs: a List of Strings, the prefixes of this word.
    """
    
    #Note that end slicing is inclusive,
    #   so the actual end slice here is excluding the last letter
    #   because n-1 will be passed as the final end slice,
    #       which is exclusive.
    return [word[:end_idx] for end_idx in range(1, len(word))]
        
def _gen_postfixes(word):
    """
    Generates all postfixes (excluding entire word) of this word.
    Inputs: word, a String
    Outputs, a List of Strings, the postfixes of this word.
    """
    return [word[start_idx:] for start_idx in range(1, len(word))]
    
def _process_chunk_prepostfixes(long_chunk_grapheme, chunk_dict):
    """
    Returns Set of chunks' prefixes/postfixes
        (depending on identity of the original grapheme)
    Inputs:
        long_chunk_grapheme, the key of this chunk
        chunk_dict, the .chunks attribute of the CandChunks object
    Outputs:
        poss_subchunks, a Set of the prefixes or postfixes of input.
    """
    this_cand_info = chunk_dict[long_chunk_grapheme]
    
    #Decide to process pre or post fixes (or both)
    this_is_prefix = this_cand_info['is_prefix']
    this_is_postfix = this_cand_info['is_postfix']
    
    poss_subchunks = []
    if this_is_prefix:
        poss_subchunks += _gen_prefixes(long_chunk_grapheme)
    if this_is_postfix:
        poss_subchunks += _gen_postfixes(long_chunk_grapheme)
        
    return set(poss_subchunks)
    
def _gen_to_filter_length_chunks(chunk_dict):
    """
    Returns chunk candidates to filter out such that:
        the chunk only has examples that are associated
            with the same but larger chunk. 
    Accepts a chunk_dict before give_argmax_pronunications has been called.
    Will return a Set of the chunk graphemes (keys) to remove from CandChunks
        before final filtering is done.
    """
    
    all_chunks = chunk_dict.keys()
    chunk_set = set(all_chunks)
    
    chunk_iter = sorted(list(all_chunks), key = len, reverse = True)
    #   The order to iterate over the chunks, preferring larger chunks.
    #       This allows the check for all smaller chunks to be done.
    
    #Return list of the prefixes to process, and update all_chunks accordingly.
    
    all_subchunks_to_filter = set()
    for long_chunk in chunk_iter:
        this_poss_subchunks = _process_chunk_prepostfixes(long_chunk, chunk_dict)
        this_subchunks = (chunk_set & this_poss_subchunks)
        
        long_examples = set(chunk_dict[long_chunk]['examples'])
        for short_chunk in this_subchunks:
            short_examples = set(chunk_dict[short_chunk]['examples'])
            
            #Remove the words that the long example has in common with the short example
            #   to gauge whether this shorter chunk should be processed 
            
            new_short_examples = short_examples - (long_examples & short_examples)
            short_examples = new_short_examples #Note -- this aliases to the main information Dict deliberately.
            
            if not new_short_examples: #No more words left
                all_subchunks_to_filter.add(short_chunk) #Mark for deletion later.

    return all_subchunks_to_filter

def _filter_length_chunks(candchunk_raw_dict):
    """
    Performs remove on the candchunk raw to get rid of chunks
        that are either prefixes or postfixes of a larger prefix or postfix
            respectively.
    Inputs:
        candchunk_raw_dict, a CandChunks-style dictionary
    Outputs:
        new_chunk_dict, the updated CandChunks chunks attribute
            to be assigned to the object.
    """
    
    to_filter_chunks = _gen_to_filter_length_chunks(candchunk_raw_dict)
    to_keep_chunks = set(candchunk_raw_dict.keys()) - to_filter_chunks
    
    new_chunk_dict = {}
    for keep_grapheme in to_keep_chunks:
        keep_info = candchunk_raw_dict[keep_grapheme]
        new_chunk_dict[keep_grapheme] = keep_info
    
    return new_chunk_dict

def select_max_score_examples(this_example_dict, num_examples):
        
        """
        Taken from CandChunkInfo for temporary length-based filtering experiment.
        
        Same as parent, but takes in one Example Dict, the value
            of Dict with IPA key
            and performs actual transformation.
        num_examples, the number of examples to retain
        Does NOT perform mutation yet.
        Returns the updated example Dict.
        """
        
        actual_num_ex = min(num_examples, len(this_example_dict))
        ordered_keys = list(this_example_dict.keys())
        ordered_keys.sort(reverse=True)
        
        which_examples = ordered_keys[:actual_num_ex]
        
        #Transfer example and its score to new Dictionary.
        new_dict = {this_word: this_example_dict[this_word] \
                    for this_word in which_examples}
        
        return new_dict
    
def candidate_chunks(data_df):
    """
    Generates candidate chunks from information
        in the popular_words.csv as a DataFrame.
    Importantly, returns the dictionary of final word-pronunciation
        selections to maximize score.
        
    Inputs:
        data_df, a DataFrame with the words to be processed.
    Outputs:
        final_chunks, a nested Dictionary:
            Keys: the chunk grapheme (String)
            Values: a Dict,
                Keys:
                    'P' -> a String IPA pronunciation
                    'score' -> a number, the score of the pronunciation
                    'examples' -> a Dict,
                        Keys: a word with this chunk, a String
                        Values: the score of that word, a number 
    """
    
    cand_chunks = CandChunks()
    for i in range(len(data_df)):
        _update_word_candidate_chunks(data_df.iloc[i], cand_chunks)
    
    cand_chunks_dict = cand_chunks.give_argmax_pronunications()
    #Above: this will no longer yield CandInfochunks, but the dictionaries.
    
    #Does NOT filter the examples for top 5. this is done later.
    
    #New: filter out the shorter prefixes/postfixes
    filtered_chunks = _filter_length_chunks(cand_chunks_dict)
    
    new_filtered_chunks = {}
    for key, chunk in filtered_chunks.items():
        new_filtered_chunks[key] = select_max_score_examples(chunk, 5)
    
    return new_filtered_chunks

####### END GENERATE CANDIDATES #######


####### DECODING AND CHUNK SELECTION #######


def _find_prefix_chunk(start_idx, cand_chunk, curr_chunk_set, curr_chunk_dict):
    """
    Inputs:
        start_idx, the start index (inclusive) of the substring
            to decode here.
        cand_chunk, String, the entire grapheme being decoded.
    Returns the length and pronunciation of the prefix.
    """
    
    #Find the largest prefixes first.
    #   Starting from non-assigned portions of the grapheme.
        
    #Run on single-letter case (due to start_idx+1 to avoid empty string checks)
    if len(cand_chunk) == 1:
        if cand_chunk in curr_chunk_set:
            return (1, curr_chunk_dict[cand_chunk]['P'])
    
    #Run on multiple letter case
    for end_idx in range(len(cand_chunk), start_idx, -1):
        prefix = cand_chunk[start_idx:end_idx]
            
        if prefix in curr_chunk_set:
            return (end_idx, curr_chunk_dict[prefix]['P'])
    
    
    
def is_regular(cand_graph, cand_ipa, true_chunk_set, true_chunk_dict):
    """
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
    
def find_sight_chunks(cand_chunks):
    """
    Inputs:
        cand_chunks, the Dictionary output
            of give_argmax_pronunications
    Outputs:    
        sight_chunks Dict:
            Key: grapheme sight chunk
            Value: a Dict
                'examples': List of [words with this sight chunk]
                'score': Given by the candidate chunk info.
    """
    true_chunks_dict = {}
    true_chunks_set = set()
    
    #Sort the candidate chunks by size.
    order_cand_chunks = list(cand_chunks.keys())
    #Below sorting from 10/9: https://developers.google.com/edu/python/sorting
    order_cand_chunks.sort(key=len)

    #Run candidate chunks through the is_regular function.
    for this_chunk_graph in order_cand_chunks:
        
        this_chunk = cand_chunks[this_chunk_graph]
        
        this_ipa = this_chunk['P']
        this_score = this_chunk['score']
        
        if not is_regular(this_chunk_graph, this_ipa,\
                   true_chunks_set, true_chunks_dict):
            
            true_chunks_set.add(this_chunk_graph)
            true_chunks_dict[this_chunk_graph] = {
                'P': this_ipa,
                'score': this_score,
                'examples': this_chunk['examples']
                }
            
    return true_chunks_dict #Convert ordering later.

####### END DECODING AND CHUNK SELECTION #######


def _format_examples(this_chunk_dict, num_examples = 5):
    
    """
    Note that this was merged with later code, so the description may not be fully updated.
    
    Format the examples into one String,
        selecting num_examples to display with highest scores
            with words with high scores appearing first.
    Inputs:
        an element (nested Dict) of the output of find_sight_chunks,
            representing a single chunk. 
        num_examples = 5
    Output:
        a String, such that value of 'example' is converted to String
            where different word pairs are joined by |
                word and its score is separated by >,
                    where score follows the word.
    """
    
    orig_example_dict = this_chunk_dict['examples']
    
    orig_example_tuples = [(word, score) for word, score\
                         in orig_example_dict.items()]
      
    scores_only = [score for _, score in orig_example_tuples]
    order_idxs = np.argsort(scores_only).tolist()
    order_idxs.reverse()
    
    order_idxs = order_idxs[:num_examples]
    
    new_example_list = []
    for order_idx in order_idxs:
        this_word, this_word_score = orig_example_tuples[order_idx]
        this_example_str = '{}>{}'.format(this_word, this_word_score)
        new_example_list.append(this_example_str)
    
    new_example_str = '|'.join(new_example_list)
    return new_example_str

    #10/11: https://docs.python.org/3/howto/sorting.html
    #order_words = sorted(list(orig_example_dict.keys()), reverse = True)
    
    #new_example_list = []
    #for this_word in order_words:
    #    this_word_score = orig_example_dict[this_word]
    #    this_example_str = '{}>{}'.format(this_word, this_word_score)
    #    new_example_list.append(this_example_str)
    
    #new_example_str = '|'.join(new_example_list)
    #return new_example_str

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
    
    list_keys = ['G', 'P', 'score', 'examples']
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
        this_chunk_dict['examples'] = _format_examples(this_chunk_dict)
        
        for key in list_keys:
            elem_dict_val = this_chunk_dict[key]
            list_cols[key].append(elem_dict_val)
        
    for this_grapheme, this_val in final_chunks_dict.items(): 
        _update_list_one_chunk(this_grapheme, this_val)
        
    #Write the lists. 
    final_chunk_df = pd.DataFrame.from_dict(list_cols)
    #10/11: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.sort_values.html
    final_chunk_df = final_chunk_df.sort_values('score', ascending = False)
    
    wrote_success = False

    if save_path:
        #10/11: https://stackoverflow.com/questions/5137497/find-current-directory-and-files-directory
        this_dir = os.path.dirname(save_path)
        if os.path.exists(this_dir):
            final_chunk_df.to_csv(save_path)
            wrote_success = True
    if not wrote_success and save_path:
        print('The path {} did not exist.'.format(save_path))
        print('The function will return the DataFrame '+\
                  'and save to current directory.') 
        
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

def gen_save_chunks(data_path, save_path):
    """
    The function to call to generate and save the final chunks.
    Inputs:
        data_path, the location of the DataFrame
            (popular_words.csv) with word information
        save_path, where to save the DataFrame
    Outputs:
        chunk_df, the resultant DataFrame with the following columns:
            'G', the grapheme chunk (String),
            'P', the IPA pronunciation (String),
            'score', the score for this chunk (number),
            'examples', a list of the highest frequency words
                with this chunk (String),
                    Formatted according to _gen_example_string.
    """
    
    data_df = pd.read_csv(data_path)
        
    assert check_if_all_nan(data_df), \
        'Has some multiple pronunications available. Assumption fails.'
        
    this_cand_chunks = candidate_chunks(data_df)
    
    print('Candidate chunks length', len(this_cand_chunks))
    
    final_chunks = find_sight_chunks(this_cand_chunks)
    chunk_df, successfully_wrote = create_chunks_df(final_chunks, save_path)
    
    print('Final chunks length', len(chunk_df))
    
    #Backup if file not saved correctly first time -- 
    #   just save the output somewhere to avoid rerunning entire program.
    
    if not successfully_wrote and save_path:
        save_path = './popular_words_chunks.csv'
        if os.path.exists(save_path):
            print('Overwriting the file at this location.')
        chunk_df.to_csv(save_path)
        print('DataFrame saved to {}'.format(save_path))
    
    
    return chunk_df

if __name__ == '__main__':
    #I broke the 'main' name above to prevent accidental re-runs
    
    DATA_PATH = '/Users/nicolewong/Desktop/urop/Data/popular_words_shift.csv' #'../Data/debug_words.csv'
    result_folder = '/Users/nicolewong/Desktop/urop/Data/old_length_dev'
    
    if not os.path.exists(result_folder):
       os.makedirs(result_folder)
        
        
    RESULT_PATH = os.path.join(result_folder, 'popular_words_chunks_shift_length_filter_tentative.csv')
  
    #result_chunks_df = gen_save_chunks(DATA_PATH, RESULT_PATH)
    result_chunks_df = gen_save_chunks(DATA_PATH, '') #Don't save yet.
    
    print(result_chunks_df)
    
    print('Chunks generated and saved. Complete.')
    print('Chunks generated. Complete.')
    
    
    
    
        
    
        
     