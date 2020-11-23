#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 22 20:33:27 2020

@author: nicolewong
"""

import sys

sys.path.insert(1, '/Users/nicolewong/Desktop/urop/code')

import imports
imports.import_files()

import special_cases
import decoding

import cand_chunks_funcs as cand_chunks_gen
import forward_alt_tests as test_funcs

"""
These all assume that double consonants are in use, i.e. the line:
        this_chunk_graph = special_cases.filter_double_consonant(this_chunk_graph)
        in present and in use in decoding.py.
"""

def check_double_consonant_filter():
    
    pos_case = 'abbbjjeek'; pos_expected = [2, 3, 5]
    neg_case = 'jklee'; neg_expected = []
    
    actual_pos = special_cases.find_double_consonant_idxs(pos_case)
    actual_neg = special_cases.find_double_consonant_idxs(neg_case)
    
    assert actual_pos == pos_expected,\
        'Double consonant location positive case did not pass.'
    assert actual_neg == neg_expected,\
        'Double consonant location negative case did not pass.'
    
    
    expected_pos_filter = 'abjek'
    expected_neg_filter = 'jklee'
    actual_pos_filter = special_cases.filter_double_consonant(expected_pos_filter)
    actual_neg_filter = special_cases.filter_double_consonant(expected_neg_filter)
    
    assert expected_pos_filter == actual_pos_filter,\
        'Positive consonant filtering did not pass.'
    assert expected_neg_filter == actual_neg_filter,\
        'Negative consonant filtering did not pass.'
        
def check_double_to_single_decodable():
    test_case = {
        'appk': 'a>a|m>pp|k>k',
        'apkke': 'a>a|m>p|k>kk|i>e' #Tests memorized and default consonant case.
        }
    
    df = test_funcs.gen_data_dict_and_df(test_case)
    cand_chunks = cand_chunks_gen.candidate_chunks(df)
    
    expected_chunks = {
        'ap': 'am' #Notice that the double consonant is dropped in the save.
        }
    
    test_funcs.add_default_dict(expected_chunks)
    del(expected_chunks['oi'])
     
    actual_chunks = decoding.find_sight_subchunks('pre', *test_funcs.subchunks_init(cand_chunks))
  
    assert test_funcs.run_dict_pg_match(actual_chunks['pre'], expected_chunks),\
        'Double to single decodable consonant test failed.'

    
def check_single_to_double_decodable():
    test_case = {
        'apple': 'a>a|m>pp|j>l|e>e',
        'appelle': 'a>a|m>pp|e>e|j>ll|e>e',
        'apk': 'a>a|m>p|k>k',
        'appk': 'a>a|m>pp|k>k'
        }
    
    df = test_funcs.gen_data_dict_and_df(test_case)
    cand_chunks = cand_chunks_gen.candidate_chunks(df)
    
    expected_chunks = {
        'pre': {'apl': 'amj', 'ap': 'am', 'apel': 'amej'},
        #Notice that all double consonants are removed.
        'post': {'ple': 'mje', 'pk': 'mk', 'pele': 'meje'}
        }
    
    for this_type in ['pre', 'post']:
        
        test_funcs.add_default_dict(expected_chunks[this_type])
        del(expected_chunks[this_type]['oi'])
        
        this_actual_chunks = decoding.find_sight_subchunks(this_type,\
                                                      *test_funcs.subchunks_init(cand_chunks))
    
        actual = this_actual_chunks[this_type]
        expected = expected_chunks[this_type]
             
        assert test_funcs.run_dict_pg_match(this_actual_chunks[this_type], expected_chunks[this_type]),\
            'Double to single decodable consonant test failed.'
        



if __name__ == '__main__':
    #check_double_consonant_filter()
    check_double_to_single_decodable()
    check_single_to_double_decodable()
