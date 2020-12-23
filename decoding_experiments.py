### Decoding experiments with syllable postprocessing.
### You should add double consonants back in?


import os
curr_dir = os.getcwd()
os.chdir('/Users/nicolewong/Desktop/urop/code')

import imports
imports.import_files()

os.chdir(curr_dir)

import special_cases
import word_funcs
import postprocessing

import CandChunks

#   Just decode forward with default pg pairs.
#       Stop decoding when the word is complete,
#            or the first irregular word is found.
#       Re-evaluate at that point.
#   You can integrate true decoding later, with words that aren't fully decoded.

def create_default_pg_tuples():
    
    default_pg = CandChunks.create_default_lookup()
    default_pg_set = set(word_funcs.get_pg_pair(f'{p}>{g}')
                         for g,p in default_pg.items())
    return default_pg_set

def default_irregular_remainder(word_tuple, default_set):
    """
    Returns the substring that is not decodable via pg pairs.
    """
    
    for idx, pair in enumerate(word_tuple):
        if pair not in default_set:
            return word_tuple[idx:]
        
    return '' #Decodable in its entirety.

def attempt_full_decode(g2p_dict, default_set):
    
    chunks_orig = postprocessing.num_syllables(g2p_dict)
    count_removed = 0
    
    for g, p_set in g2p_dict.items():
        decodable = set()
        for p in p_set:
            this_word_tuple = word_funcs.get_mapping(p)
            if not default_irregular_remainder(this_word_tuple, default_set):
                #Is fully decodable with default pg pairs.
                decodable.add(p)
        g2p_dict[g] = p_set - decodable #Remove the decodable words.
        count_removed += len(decodable)
        
    chunks_new = postprocessing.num_syllables(g2p_dict)
    print()
    print(f'Removed due to full decoding: {count_removed}')
    print(f'Previous number of chunks: {chunks_orig}')
    print(f'Current number of chunks: {chunks_new}')
    print(f'\tDifference: {chunks_orig - chunks_new}')
    
    #See if you can collapse the remainders,
    #   such that the decoded sections are still taken away.
    
    return g2p_dict
                
if __name__ == '__main__':
    
    g2p_dict = special_cases.load_syllables()
    default_pg_set = create_default_pg_tuples()
    
    g2p_dict = attempt_full_decode(g2p_dict, default_pg_set)
    