####### POST-CHUNK GENERATION FILTERING ####### 

import numpy as np

def select_top_examples(chunks):
    """
    Formats the examples by selecting only the top examples.
    Inputs: chunks is a final_chunks-style nested Dict.
    Outputs: mutated chunks
    """
    
    for cand_type, each in chunks.items():
        for chunk_key, chunk in each.items():
            chunk['examples'] = _format_examples(chunk)
            
    return chunks

###### PREVIOUSLY CANDCHUNKINFO-STYLE EXAMPLE WORD SELECTION ###### 

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
