import math
import pandas as pd
from collections import defaultdict 
import numpy as np

import decoding

from CandChunks import *
from CandChunkInfo import *
from decoding_test_cases import *

import os


######### VERIFICATION OF CHUNK CODE VERIFICATION  #########

def _gen_manual_computed_dict(keyval_list, is_simple_dict):
    #Manually checked 10/10 6:05 pm.
    """
    Inputs:
        keyval_list, List of Tuples of (word, score), of type (String, number)
        is_simple_dict, if should return simple format.
    Outputs:
        this_dict.
            if is_simple_dict
                simple format of the manual case
            else:
                nested format of the code-computed case.
    """
    
    this_dict = {}
    
    for key, val in keyval_list:
        this_dict[key] = val if is_simple_dict else {'score': val}
    
    return this_dict

def _make_verify_chunk_check_cases():
    """
    For verifying the verification process of the chunk testing.
    """
    
    raw_cases = [
        #Case A: set diff only
        {'manual': [('A', 1), ('B', 2)],
         'computed': [('A', 1), ('C', 2)]},
        #Case B: incorrect scores only
        {'manual':[('A', 1), ('B', 2)],
         'computed':[('A', 3), ('B', 4)]},
        #Case C1: both problems, manual len < computed len
        {'manual':[('A', 2), ('B', 4)],
         'computed':[('A', 2), ('B', 3), ('C', 5)]},
        #Case C2: both problems, manual len > computed len
        {'manual':[('A', 1), ('B', 2)],
         'computed':[('A', 2)]},
        #Case D1: single element, test pass
        {'manual':[('A', 2)],
         'computed':[('A', 2)]},
        #Case D2: multiple element, test pass
        {'manual':[('A', 1), ('B', 2)],
         'computed':[('A', 1), ('B', 2)]},
        #Case E1: empty dicts, test pass
         {'manual':[],
         'computed':[]},
        #Case E2: one empty, one not, test fails
         {'manual':[],
         'computed':[('A', 2)]},
        #Case E3: in the other direction of E2
        {'manual':[('A', 2)],
         'computed':[]}
        ]
    
    
    return raw_cases

def _output_verify_chunk_check_cases():
    
    """
    For verifying the correctness of the verification of chunks.
    Will print out result of the cases for this verification.
    """
    
    report = ""
    raw_cases = _make_verify_chunk_check_cases()
    for case_num, raw_case in enumerate(raw_cases):
        case_args = tuple(
            _gen_manual_computed_dict(raw_case[this_key], this_key == 'manual')\
                for this_key in ['manual', 'computed']
         )
        report = '\n'+ '*' * 8 + ' For Case {}'.format(case_num) +'\n'
        report += '\tManual: {}\n'.format(case_args[0])
        report += '\tComputed: {}\n'.format(case_args[1])
        
        print(report)
        _compare_final_chunks_test_case(*case_args, is_assert = False)
        

######### CHUNK CODE VERIFICATION HELPERS #########
    
def _report_incorrect_elements(this_collection, \
                               manual_case, computed_case,\
                                   is_set_diff):
    #Verified via _comapre_final_chunks_test_case, see comment there.
    
    """
    Reports problematic words, if any.
    Accepts
        is_set_diff, a Boolean:
            If True:
               Report symmetric difference between manual and computer-computed case.
                will output all words that are part of the symmetric difference
                    between the sets.
                will output 'N/A' for the set that doesn't have
                    the word as a key.
            Else:
                Report score differences between manual and computer-computed case.
                will output all the words that have different scores
                    but are in both dicts.
        this_collection:
            if is_set_diff:
                the Set difference between manual and computed
            else:
                the computed_case Dict
        manual_case, computed_case, the manually computed and code-computed
            proposed answers to final number of chunks.
        
    Returns:
        A String report of problematic words.
            Empty if there are none to report.
        Note that for the non-set difference,
            if a word is not in both dictionaries,
            this call may still return it. This is because double errors
                are preferable to accidentally deciding to ignore a
                    potential error.
        
    """
    neg_report = ''
    
    for word in this_collection:

        computed_score = computed_case[word]['score'] if word in computed_case else -float('inf')
        manual_score = manual_case[word] if word in manual_case else -float('inf')
        
        if computed_score != manual_score:
            neg_report += '\nWord: {}'.format(word)
            neg_report += '\n\tScore in manual: {}'.format(manual_score)
            neg_report += '\n\tScore in computed: {}'.format(computed_score)
            
    return '\nDifferences for is_set_diff set to {}'.format(is_set_diff)\
            + (neg_report if neg_report else '\n\tNone to report.')
    
    
def _compare_final_chunks_test_case(manual_case, computed_case, \
                                    is_assert = True, full_report = True):
    #Verified 10/10/20 8:11 pm
    """
    Appropriately compares the Dict inputs to ensure they are the same.
    Inputs:
        manual_case, the Dict handwritten with word->score.
        computed_case, the Dict generated by the code sto describe final chunks
        is_assert, whether to assert failure if needed
            (default to True, only change if trying to verify cases for this function)
    Outputs:
        None, but will fail assertion and report if unexpected behavior in
            final answer for chunks.
    """
    #10/10: Symmetric difference:
    #   https://stackoverflow.com/questions/22736641/xor-on-two-lists-in-python
    #   https://stackoverflow.com/questions/50871370/python-sets-difference-vs-symmetric-difference
    

    #If there are differences between words included.
    set_diff = set(computed_case.keys()) ^ set(manual_case.keys())
    neg_report = _report_incorrect_elements(set_diff,\
                                            manual_case, computed_case, True)
    
    #If there are differences in the scores between words in both Dicts.
    neg_report += _report_incorrect_elements(computed_case, \
                                             manual_case, computed_case, False)
    
    full_report = 'Final chunks (either words or score) are not as expected.'\
        + '' if not full_report else neg_report
        
    if is_assert:
        assert ('\n\tNone to report.' in neg_report), full_report #If anything problematic to report.
    else:
        print(full_report if neg_report != '' else 'Nothing to report.')
            
    
###### CALLABLE CHECK FUNCTIONS ###### 
        

def check_filter_examples(analysis=False):
    """
    Checks if the filter code functions as expected
        according to the constructed test case.
    Returns nothing, but will fail assertion
        and print report if unexpected behavior.
    """
    
    if analysis:
        global print_info
        print_info = []
    
    this_num_examples = 2
    chunk_struct_data_vals, expected_data_vals = _make_filter_test_case()
    
    for this_chunk_data, this_expected_data \
        in zip(chunk_struct_data_vals, expected_data_vals):
            
        #Check all cases. 
        
        chunk_struct = CandChunkInfo(this_num_examples)
        chunk_struct.data = this_chunk_data
        #this_key = list(chunk_struct.data.keys())[0]
        
        result_dict = chunk_struct.give_argmax_score()
        
        expected_behavior = result_dict == this_expected_data
    
        assert expected_behavior, 'Filtered examples were incorrect.'
        
def check_chunks(full_report = False):
    """
    Checks if candidate generation and selection process code is correct.
    Will fail assertion and print report if unexpected behavior
    """ 
    
    manual_case = _make_manual_chunk_answer() 
    
    #Compute code-generated answer.
    test_df = _make_chunk_case()
    candidates = candidate_chunks(test_df)
    final_chunks = find_sight_chunks(candidates)
    
    if full_report:
        #Manually verified with hand calculations, 10/10/20 8:25 pm
        for word in final_chunks:
            info = final_chunks[word]
            print(word, info['score'])
    
    _compare_final_chunks_test_case(manual_case, final_chunks,\
                                   full_report)
         
def check_csv_chunks():
    
    parent_dir = '../Data/'
    input_path = os.path.join(parent_dir, 'debug_words.csv')
    output_path = os.path.join(parent_dir, 'debug_words_chunks.csv')
    
    if not os.path.exists(input_path):
        _make_chunk_case(save_path = input_path)

    final_df = gen_save_chunks(input_path, output_path)
    reload_df = pd.read_csv(output_path)
    
def check_filter_length():
    
    #10/25: Words and pronunications directly from phonix.ipa
    #This checks the split variant of the length filter
    this_case = {
        'some': 's>s|ʌ1>o|m>me',
        'eat': 'i1>ea|t>t',
        'atom': 'æ1>a|t>t|ʌ0>o|m>m',
        'somewhat': 's>s|ʌ1>o|m>me|w>wh|ʌ1>a|t>t',
        'what': 'w>wh|ʌ1>a|t>t' 
        }
    
    these_words = list(this_case.keys())
    this_case = {
        'Word': these_words,
        'Frequency': [5, 1, 3, 2, 4],
        'P': [this_case[this_word] for this_word in these_words]
        }
    
    #Declare a CandChunk chunks dictionary directly? 
    this_df = pd.DataFrame.from_dict(this_case)
    filtered_chunks = candidate_chunks(this_df)
    
    print('Requires manual verification. Please see output.')
    
    report = 'Prefixes'
    for pre_chunk in filtered_chunks['pre'].items():
        report += f'\n\t {pre_chunk}'
    
    report += '\n\nPostfixes'
    for post_chunk in filtered_chunks['post'].items():
        report += f'\n\t {post_chunk}'
        
    return report
    
def check_prefix_postfix_cuts():
    """
    Tests expected behavior for one run of prefix/postfix cuts.
    """
    
    #The real application will need separate pre/postfix "memories"
     
    inputs = ['abe', 'abc', 'a', 'cab']
    memory_set = {'abc', 'a', 'ab'}
    memory_dict = {elem: {'P': -1} for elem in memory_set}
    info_args = (memory_set, memory_dict)
    #Just to avoid error for now, not yet testing pronunication reassembly.
    
    expected_prefix = ['e', '', '', None]
    expected_postfix = [None, '', '', 'c']
    
    actual_prefix = [decoding._find_prefix_chunk(word, *info_args)\
                     for word in inputs]
    actual_postfix = [decoding._find_postfix_chunk(word, *info_args)\
                     for word in inputs]
        
    actual_prefix = [pair[0] if pair is not None else None\
                     for pair in actual_prefix ]
    actual_postfix = [pair[0] if pair is not None else None\
                      for pair in actual_postfix]

    prefix_correct = expected_prefix == actual_prefix
    postfix_correct = expected_postfix == actual_postfix
    
    assert prefix_correct and postfix_correct
    
def check_decoding_alt():
    
    """
    Tests expected behavior for decoding alternating cuts function.
    """
    
    #10/25: Words and pronunications directly from phonix.ipa
    memory_set_prefix = {
        's': 's',
        'a': 'æ',
        't': 't',
        'wh': 'w'
        }
    
    memory_set_suffix = {
        'me':  'm',
        'o':'ʌ',
        'm': 'm'
        }
    
    memory_set_prefix = {key: {'P': val} for key, val in memory_set_prefix.items()}
    memory_set_suffix = {key: {'P': val} for key, val in memory_set_suffix.items()}
    chunk_dict = {'pre': memory_set_prefix, 'post': memory_set_suffix}
    chunk_set = {'pre': set(memory_set_prefix.keys()), 'post': set(memory_set_suffix.keys())}
        
    words_to_test = {
        'some': 's>s|ʌ1>o|m>me', #Decode partial, fails on prefix (no o prefix grapheme)
        'atom': 'æ1>a|t>t|ʌ0>o|m>m', #Decode complete
        'what': 'w>wh|ʌ1>a|t>t', #Decode partial, fails on suffix (because t is not a postfix)
        'apples': 'apples' #Completely fails on prefix
        }
    
    expected_decodes = [None, 'ætʌm', None, None]
    
    actual_decodes = [decoding.decode_alt(word, chunk_set, chunk_dict) for word in words_to_test]

    assert expected_decodes == actual_decodes

def check_additional_reconstruction():
    
    """
    Tests for expected IPA reconstruction behavior.
    Multiple even terminates on prefix case is in (atom) for check_decoding_alt.
    """
    
    mult_odd_term_suffix = ['ab', 'fg', 'c', 'e', 'd']
    answer_mult = 'abcdefg'
    
    single = ['a']
    answer_single = 'a'
    
    actual_mult = decoding._reconstruct_ipa_cuts(mult_odd_term_suffix)
    actual_single = decoding._reconstruct_ipa_cuts(single)

    assert actual_mult == answer_mult and actual_single == answer_single

def check_find_sight_chunks():
    
    #10/25 and 11/1: Words and pronunications from phonix.ipa
    words = {
        'at': 'æ1>a|t>t',
        'atom': 'æ1>a|t>t|ʌ0>o|m>m', 
        'w': 'w>w',
        'talked': 't>t|ɔ1>a|k>lk|t>ed',
        'walked': 'w>w|ɔ1>a|k>lk|t>ed',
        
        }
    #Case explanations:
    #at and atom: Front is decodable: at should have 2 examples at least.
    #talked and walked: Back is decodable: "alked" should have 2 examples at least.
    #At, atom, talked are not fully decoable on being encountered.
    #Walked will be fully decodable.
    to_df = {'Word': list(words.keys()), 'P': list(words.values())}
    scores = list(range(len(words)-1, -1, -1))
    scores[-1] = 1
    to_df['Frequency'] = scores
    
    df = pd.DataFrame.from_dict(to_df)
    cand_chunks = decoding.candidate_chunks(df)
    
    cand_report = 'CandChunks:'
    cand_report += '\npre'
    for graph, info in cand_chunks['pre'].items():
        cand_report += f'\n\t{graph}'
        cand_report += f'\n\t\t{info}'
        
        
    cand_report += '\npost'
    for graph, info in cand_chunks['post'].items():
        cand_report += f'\n\t{graph}'
        cand_report += f'\n\t\t{info}'
        
    final_chunks = decoding.find_sight_chunks(cand_chunks)
    
    report = 'Decoding:'
    report += '\npre'
    for graph, info in final_chunks['pre'].items():
        report += f'\n\t{graph}'
        report += f'\n\t{info}'
        
        
    report += '\npost'
    for graph, info in final_chunks['post'].items():
        report += f'\n\t{graph}'
        report += f'\n\t{info}'
        
    print('Please see comment in code about pronunciation change for "was"'
          ' for testing purposes'
          ' (only changed manually in this code, not in the text file).')
        
    print()
    print(report)
    
    
####### END INDIVIDUAL CHECKS #######


def check_code():
    
    """
    Callable from other imports, runs specified test cases.
    Returns True if all cases succeeded.
            Else, will fail an assertion and report according
                to behavior of that case.
    """
    
    test_cases = [
        #check_chunks,
        #check_filter_examples
        ]
    
    for test_case in test_cases:
        test_case()
    
    return True

if __name__ == '__main__':
    #check_csv_chunks()
    #check_code()
    #check_decoding_alt()
    #check_additional_reconstruction()
    check_find_sight_chunks()
        
