###### DEBUGS AND CHECKS #######
from decoding import *
import os

####### TEST CASE DATA CREATION ####### 


def _make_filter_test_case():
    
    """
    Returns Lists of Dicts, input and output for filter test case.
    """
    
    chunk_struct_data_vals = [
        
        {'P1':{ #Select examples in an excess of examples
            'score': 1,
            'examples':  {'i1no': 1, 'i1yes1': 100, 'i1yes2': 1000}
            }},
        
        {'P2':{#Select entire set
              'score': 2,
              'examples': {'i2yes1': 2, 'i2yes2': 200}
              }},
        
       {'P3':{#Less examples than max to filter available.
            'score': 3,
            'examples': {'i3yes': -3000} 
            }}

        ]
    
    expected_data_vals = [
        
        {#Select examples in an excess of examples
         'P': 'P1',
         'score': 1,
         'examples':  {'i1yes1': 100, 'i1yes2': 1000}
            },
        
        {#Select entire set
         'P': 'P2',
         'score': 2,
         'examples': {'i2yes1': 2, 'i2yes2': 200},
              },
        
        {#Less examples than max to filter available.
         'P': 'P3',
         'score': 3,
         'examples': {'i3yes': -3000} 
            }

        ]
    
    return chunk_struct_data_vals, expected_data_vals
         
def _make_chunk_case(save_path = ''):
    
    #Words and the pronunications are from the original data.
    debug_dict = {
        'Unnamed': [1, 2, 3, 9, 8, 7, 4],
        'Word': ['the', 'there', 'herself', 'her', 'more', 'under', 'fer'],
        'Frequency': [1, 1.5, 2 , 0.5, 0.3, 1.1, 0.7],
        'P': ['ð>th|i1>e', 'ð>th|ɛ1>e|r>re', \
              'h>h|ɝ0>er|s>s|ɛ1>e|l>l|f>f', 'h>h|ɝ1>er', \
                  'm>m|ɔ1>o|r>re',\
                      'ʌ1>u|n>n|d>d|ɝ0>er',\
                          'f>f|ɝ1>er'],
        'P1': [math.nan]*7 #['hi'] + [math.nan]*6
        #10/4: https://stackoverflow.com/questions/43638759/python-how-to-get-nan
        }
    debug_df = pd.DataFrame.from_dict(debug_dict)
    
    if save_path:
        debug_df.to_csv(save_path)
        
    return debug_df

def _make_manual_chunk_answer():
    """
    Return value (a Dict) for use as manual_case
        in check_final_chunks_test_case.
    """
    
    return {
       
       'th':2.5, 'e':1,
       'the':1.5, 'ere':1.5, 're':1.8,
       'h':2.5,
       'hers':2, 'herse':2, 'hersel':2, 'elf':2, 'self':2, 'lf':2,
       'er':2.3,
       'm':0.3,'mo':0.3,'ore':0.3,
       'u':1.1, 'un':1.1, 'und':1.1, 'nder':1.1, 'der':1.1,
       'f':2.7
   
       }

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
        

def check_filter_examples():
    """
    Checks if the filter code functions as expected
        according to the constructed test case.
    Returns nothing, but will fail assertion
        and print report if unexpected behavior.
    """
    
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
    
####### END INDIVIDUAL CHECKS #######


def check_code():
    
    """
    Callable from other imports, runs specified test cases.
    Returns True if all cases succeeded.
            Else, will fail an assertion and report according
                to behavior of that case.
    """
    
    test_cases = [
        check_chunks,
        check_filter_examples
        ]
    
    for test_case in test_cases:
        test_case()
    
    return True

if __name__ == '__main__':
    check_csv_chunks()
        
