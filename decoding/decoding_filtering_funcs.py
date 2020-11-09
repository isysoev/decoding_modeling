#Filtering functions

import numpy as np


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
    return [word[start_idx:] for start_idx in range(1, len(word))]

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

####### FIND NEXT CHUNK #######

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

####### DECODING (IS_REGULAR FUNCTIONS) ########
        
def decode_alt(cand_graph, true_chunk_set, true_chunk_dict):
    """        
    Inputs: cand_graph, the grapheme to be considered (String)
            
            true_chunk_set, a Dict of sets either for prefixes or postfixes
                each value the Set of currently chosen sight chunks
                
            true_chunk_dict, a Dict of Dicts either for prefixes or postfixes
                each value the dictionary of the current
                    list of sight chunks.
                    
    Outputs: str, a decoded pronunciation.
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
    decoded_ipa = _reconstruct_ipa_alt_cuts(ipa_pieces)
    
    return decoded_ipa


def _reconstruct_ipa_alt_cuts(ipa_piece_list):
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

def decode_prefix(cand_graph, true_chunk_set, true_chunk_dict):
    """        
    Prefix-order decoding.
    Inputs: cand_graph, the grapheme to be considered (String)
            
            true_chunk_set, a Dict of sets either for prefixes or postfixes
                each value the Set of currently chosen sight chunks
                
            true_chunk_dict, a Dict of Dicts either for prefixes or postfixes
                each value the dictionary of the current
                    list of sight chunks.
                    
    Outputs: str, a decoded pronunciation.
    """
    
    memory_info = (true_chunk_set, true_chunk_dict)
    ipa_pieces = []
    
    next_decode = cand_graph 
    
    while next_decode: #Not empty
        next_decode_info = _find_cut_chunk(next_decode, True, *memory_info)
        
        if next_decode_info is None:
            return None #Either no prefix or postfix removable. 
    
        next_decode, found_ipa_piece = next_decode_info
        ipa_pieces.append(found_ipa_piece)
        
    #Otherwise, word was deconstructed.
    decoded_ipa = ''.join(ipa_pieces) #Join in forward order.
    
    return decoded_ipa


def decode_suffix(cand_graph, true_chunk_set, true_chunk_dict):
    """   
    Suffix-order decoding.      
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
    ipa_pieces = [] 
    
    next_decode = cand_graph 
    while next_decode: #Not empty
        next_decode_info = _find_cut_chunk(next_decode, False, *memory_info)
        
        if next_decode_info is None:
            return None #Either no prefix or postfix removable. 
    
        next_decode, found_ipa_piece = next_decode_info
        ipa_pieces.append(found_ipa_piece)
        
    #Otherwise, word was deconstructed.
    ipa_pieces.reverse() #Was first stored in suffix adding order 
    decoded_ipa = ''.join(ipa_pieces)
    
    return decoded_ipa


###### CANDCHUNKINFO-STYLE EXAMPLE WORD SELECTION ###### 

def _format_examples(this_chunk_dict, num_examples = 5):
    
    """
    Format the examples into one String,
       with high frequency words appearing first.
    Inputs:
        an element (nested Dict) of the output of find_sight_chunks,
            representing a single chunk. 
        num_examples, int, to display in the CSV 
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
