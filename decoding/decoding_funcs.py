import numpy as np
import os
from os.path import join

    
def decode_piece_lookup(piece, curr_chunk_set, curr_chunk_dict):

    """
    If the piece (str) to decode
        has a chunk in the memory,
    then will return
        the proposed Pronunciation (str) of the piece 
    
    If decode of this piece fails, return None.
    """

    if piece in curr_chunk_set:
        return curr_chunk_dict[piece]['P']
    
    return None
    
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
             
        this_ipa_piece = decode_piece_lookup(prefix, curr_chunk_set, curr_chunk_dict)
        
        if this_ipa_piece is not None:
            #Then result is the proposed P for this piece.
            return (cand_chunk_rem[end_idx:], this_ipa_piece)
        
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
        
        this_ipa_piece = decode_piece_lookup(postfix, curr_chunk_set, curr_chunk_dict)
        
        if this_ipa_piece is not None:
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