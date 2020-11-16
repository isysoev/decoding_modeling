####### GENERATE CANDIDATES #######

from CandChunks import CandChunks


DEFAULT_CHUNKS = CandChunks.create_default_lookup()
    
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
    Do NOT store full words in either Dictionary.
    """
    #Verified: prefix, suffix generation.
    
    info = df_word['P'].split('|') #See assumption in check_if_all_nan.
    #   Above splits into the p/g pairs.
    
    #Store the entire list for future processing.
    entire_list = info
    cand_chunks['entire'].add(entire_list, df_word)
    
    #Take prefixes and update.
    for end_idx in range(1, len(info)):
        
        #Note that this stops one end idx short of the full word
        #   But that full word is covered in the suffix
        prefix_list = info[:end_idx]
        cand_chunks['pre'].add(prefix_list, df_word)
    
    for start_idx in range(1, len(info)): #Exclude full words!
        suffix_list = info[start_idx:]
        cand_chunks['post'].add(suffix_list, df_word)
            
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
    
    cand_chunks = {'pre': CandChunks(),
                   'post': CandChunks(),
                   'entire': CandChunks(should_init_default = False)
                   } 
    
    for i in range(len(data_df)):
        _update_word_candidate_chunks(data_df.iloc[i], cand_chunks)
    
    #Selects the top pronunication to use.
    top_ipa_chunks = {cand_type: sub_chunks.give_argmax_pronunications()\
                    for cand_type, sub_chunks in cand_chunks.items()} #Do not filter for the words.
        
    #Performs length-delayed filtering on pre and postfixes only.
    #Notice that filter length chunks assumes pre/post identity  
    length_filtered_chunks = {cand_type: _filter_length_chunks(each, (cand_type == 'pre'))\
                              for cand_type, each in top_ipa_chunks.items()\
                                  if cand_type in ['pre', 'post']}
    
    #Entire words don't require length filtering. Pronunciation filtering should not really prompt any changes.
    length_filtered_chunks['entire'] = top_ipa_chunks['entire']
    
    final_chunks = length_filtered_chunks
    return final_chunks


######## GENERATES PREFIXES AND POSTFIXES ############

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
    postfixes = [word[start_idx:] for start_idx in range(1, len(word))]
    return postfixes

def _process_chunk_prepostfixes(long_chunk_grapheme, chunk_dict, this_is_prefix):
    """
    Returns Set of chunks' prefixes/postfixes
        (depending on identity of the original grapheme)
    Inputs:
        long_chunk_grapheme, the key of this chunk
        this_is_prefix (referring to the specific chunk), bool
            if False, is postfix (see the comment below)
    Outputs:
        poss_subchunks, a Set of the prefixes or postfixes of input.
    """
    this_cand_info = chunk_dict[long_chunk_grapheme]
    
    poss_subchunks = []
    #Note that entire words will simply be passed to this function twice.
    if this_is_prefix:
        poss_subchunks += _gen_prefixes(long_chunk_grapheme)
    else:
        poss_subchunks += _gen_postfixes(long_chunk_grapheme)
        
    return set(poss_subchunks)

########## LENGTH FILTERING ###############

def _gen_to_filter_length_chunks(chunk_dict, this_is_prefix):
    """
    Will mutate the list of examples for the chunk_dict (the main source of information)
        to remove jointly held examples (see below for explanation)
        
    Returns chunk candidates to filter out such that:
        the chunk only has examples that are associated
            with the same but larger chunk. 
            
    Accepts a chunk_dict before examples have been filtered out.
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
        this_poss_subchunks = _process_chunk_prepostfixes(long_chunk, chunk_dict, this_is_prefix)
        this_subchunks = (chunk_set & this_poss_subchunks)
        
        #this_subchunks is the the chunks to filter examples from,
        #   the intersection between the larger chunks' pre/postfixes
        #       and the proposed chunks
        
        long_examples = set(chunk_dict[long_chunk]['examples'])
        for short_chunk in this_subchunks:
            
            if short_chunk in DEFAULT_CHUNKS: #Never tamper with or remove a default chunk.
                continue
            
            short_examples = set(chunk_dict[short_chunk]['examples'])
            
            #Remove the words that the long example has in common with the short example
            #   to gauge whether this shorter chunk should be processed 
            
            this_to_filter_example = (long_examples & short_examples)
            
            for to_filter_word in this_to_filter_example:
                
                #Alias to this_example_dict
                this_example_dict = chunk_dict[short_chunk]['examples']
                del(this_example_dict[to_filter_word])
                
                if not this_example_dict: #No more words left
                    all_subchunks_to_filter.add(short_chunk) #Mark for deletion later.

    return all_subchunks_to_filter

def _filter_length_chunks(candchunk_raw_dict, this_is_prefix):
    """
    Performs remove on the candchunk raw to get rid of chunks
        that are either prefixes or postfixes of a larger prefix or postfix
            respectively.
    Inputs:
        candchunk_raw_dict, a CandChunks-style dictionary,
            corresponding to either prefixes or postfixes
        this_is_prefix, a bool
    Outputs:
        new_chunk_dict, the updated CandChunks chunks attribute
            to be assigned to the object.
    """
    
    to_filter_chunks = _gen_to_filter_length_chunks(candchunk_raw_dict, this_is_prefix)
    
    to_keep_chunks = set(candchunk_raw_dict.keys()) - to_filter_chunks
    
    new_chunk_dict = {}
    for keep_grapheme in to_keep_chunks:
        keep_info = candchunk_raw_dict[keep_grapheme]
        new_chunk_dict[keep_grapheme] = keep_info
    
    return new_chunk_dict

