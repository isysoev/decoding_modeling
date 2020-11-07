#Filtering functions

import numpy as np

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
