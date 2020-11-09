
#10/17 OrderedDict syntax: https://www.geeksforgeeks.org/ordereddict-in-python/
#10/17 Some OrderedDict advice: http://gandenberger.org/2018/03/10/ordered-dicts-vs-ordereddict/
from collections import OrderedDict

import os
import pandas as pd

import datetime
#10/31: https://www.programiz.com/python-programming/datetime/current-datetime

#My imports
import cand_chunks_funcs as cand_chunks_gen

import decoding_filtering_funcs as filtering
import decoding_formatting as formatting

######### DECODING SECTION #########

def which_entire_decoded(cand_chunks, true_chunks_set):
    """
    Inputs: cand_chunks, true_chunks_set, Dict and Set information about chunks
    Returns a set of words that were decoded (were not in true_chunks_dict)
    """
    
    all_words = set(cand_chunks['entire'].keys())
    return (all_words - true_chunks_set)
    

def post_chunk_filter_examples(filter_set, this_subchunks_dict, this_subchunks_set):
    """
    Mutates the subchunk Dict such that words
        in the filter_set, a Set of str,
            will no longer be present as examples in this_subchunks_dict, a Nested Dict.
                this_subchunks_set is just a Set of the words in the Dict.
    If a given chunk no longer has any examples, it is deleted from the dictionary.
    """
    
    
    #11/8/20: Advice on fast Dict processing
    #   https://stackoverflow.com/questions/22668574/python-fastest-strategy-for-remove-a-lot-of-keys-from-dict
    for chunk_graph, chunk_info in this_subchunks_dict.items():
        if chunk_graph in this_subchunks_set:
            del(chunk_info['Examples'][chunk_graph])
        if not chunk_info['Examples']: #No more examples
            del(this_subchunks_dict[chunk_graph])
    
def find_sight_chunks(cand_chunks):
    
    chunk_types = ['pre', 'post', 'entire']
     
    true_chunks_dict['entire'] = {key: OrderedDict() for key in chunk_types}
    #Above: this should guarantee acceptance order for added chunks.
    #However, my version of Python already has ordered normal Dict.
    true_chunks_set = {key: set() for key in chunk_types}
    
    chunk_storage = (cand_chunks, true_chunks_dict, true_chunks_set)
    
    print('Need to initialize default pronunciations here soon!')
     
    true_chunks_dict = find_sight_subchunks('pre', *chunk_storage)
    true_chunks_dict = find_sight_subchunks('post', *chunk_storage)
    true_chunks_dict = find_sight_subchunks('entire', *chunk_storage)
    
    
    #Filter prefixes, postfixes that only represent entire words that were decoded.
    decoded_words = which_entire_decoded(cand_chunks, true_chunks_set)
    post_chunk_filter_examples(filter_set, true_chunks_dict['pre'], true_chunks_set['pre'])
    post_chunk_filter_examples(filter_set, true_chunks_dict['post'], true_chunks_set['post'])
    
    filtering._format_examples()
     
    #Filter prefixes, postfixes
    print('TODO: For entire calls only: Add a "for filtering" thing here to remove this ENTIRE word from the chunks.')
     
    raise NotImplementedError
    
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
    
    decoded_ipa = decode_fn(this_chunk_graph,\
               true_chunks_set, true_chunks_dict)
        
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
    
    order_word_chunks = list(sub_cand_chunks[chunk_type].keys())
    order_word_chunks.sort(key = len)

    #Run candidate chunks through the is_regular function.
    for this_chunk_graph in order_word_chunks:
        
        this_chunk = sub_cand_chunks[this_chunk_graph]
        #Note -- the try_update_chunks mutates, not copies, the Dict and Set
        true_chunks_set, true_chunks_dict = try_update_chunks(this_chunk_graph, this_chunk,
                                                              chunk_type, decode_alt,
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
        
    this_cand_chunks = cand_chunks_gen.candidate_chunks(data_df)
    
    num_cand_chunks = sum(len(this_cand_chunks[key]) for key in this_cand_chunks)
    print('Candidate chunks length (including full words)', num_cand_chunks)
    
    final_chunks = find_sight_chunks(this_cand_chunks)
    prefix_chunk_df, _ = create_chunks_df(final_chunks['pre'], save_path+'_prefix')
    postfix_chunk_df, _ = create_chunks_df(final_chunks['post'], save_path+'_postfix')
    
    num_final_chunks = len(final_chunks['pre']) + len(final_chunks['post'])
    print('Final chunks length', num_final_chunks)
    
    return prefix_chunk_df, postfix_chunk_df

if __name__ == '__gmain__':
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
    
if __name__ == '__main__':

    DATA_PATH = '../Data/popular_words_shift.csv'
    RESULT_PATH = None
    result_chunks_df = gen_save_chunks(DATA_PATH, RESULT_PATH, to_save = False)
    
    
    
    
        
    
        
     