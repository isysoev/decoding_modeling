#Runs tests on the pre/post/alt decoding.
import pandas as pd

from collections import OrderedDict

#Please see citations in imports.py file
import sys
code_path = '/Users/nicolewong/Desktop/urop/code'
sys.path.insert(1, code_path) 

import imports
imports.import_files()

#My imports
import cand_chunks_funcs as cand_chunks_gen
import decoding_funcs
import decoding

from CandChunks import CandChunks


default_chunks = CandChunks.create_default_lookup()


############################
##### HELPFUL FUNCTIONS ####
############################

def add_default_dict(this_expected_dict):
    """
    Add (Mutation) the default g -> p Dict to this_expected_dict,
        which has the same g -> p mapping.
    Used for equality checks, so that can just type out
        the new chunks, rather than defaults.
    """
    this_expected_dict.update(default_chunks)
    
def gen_data_dict_and_df(words):
    """
    Generates df to use for testing from word/IPA assignments
    
    Inputs: words, a Dict of grapheme -> phonix-style pronunciation strs
    Outputs: a DataFrame with scores inputted that can be used with candidate_chunks
    """
    
    to_df = {'Word': list(words.keys()), 'P': list(words.values())}
    scores = list(range(len(words)-1, -1, -1))
    scores[-1] = 1
    to_df['Frequency'] = scores
    
    return pd.DataFrame.from_dict(to_df)

def subchunks_init(cand_chunks):
    """
    Generates empty chunk memory for use with testing the decodes in isolation.
    """
    chunk_types = ['pre', 'post', 'entire']
     
    true_chunks_dict = {key: OrderedDict() for key in chunk_types}
    #Above: this should guarantee acceptance order for added chunks.
    #However, my version of Python already has ordered normal Dict.
    true_chunks_set = {key: set() for key in chunk_types}
    
    chunk_storage = (cand_chunks, true_chunks_dict, true_chunks_set)
     
    return chunk_storage
 
def subchunks_report(final_subchunks):
    """
    Converts subchunks (pre, post, or entire)
        to an organized str.
    It will NOT display defaults.
    """
    
    report = "" 
    
    for key, sub_chunks in final_subchunks.items():
        
        report += f"{key}\n"
        for word, info in sub_chunks.items():
            if word in default_chunks:
                continue
            report += f'\t{word}\n'
            report += f'\t\t{info}\n'
            
    return report
    

def candchunks_report(final_subchunks):
    """
    Converts candchunks (pre, post, or entire)
        to an organized str.
     It will NOT display defaults.
    """
     
    report = "" 
    
    for key, info in final_subchunks.items():

        if key in default_chunks:
            continue
            
        report += f"{key}\n"
        report += f'\t\t{info}\n'
            
    return report

def spot_check_default_P():
    """
    Generates the default P dict for inspection.
    """
    
    this_dict = CandChunks.create_default_lookup()
    
    assert len(this_dict) == 47, 'Wrong number of entries in dict'
    graph = ['u', 'oy', 'ng']
    phoneme  = ['ʌ', 'ɔɪ', 'ŋ']
    
    assert all(this_p == this_dict[this_g]\
               for this_g, this_p in zip(graph, phoneme)),\
        'Incorrect pronunciation for spot-check of Dict contents.'

 
def run_dict_pg_match(subchunks, pg_only):
    """
    For matching the pg pair correspondences
        Between a pg pair only Dict
            and a subchunks style Dict.
        subchunks is the Dict when 'pre', 'post' is identified.
    """
    
    subchunks_pg = {}
    for graph, info in subchunks.items():
        subchunks_pg[graph] = subchunks[graph]['P']
            
    return subchunks_pg == pg_only
    
######################
###### CHECKS ########
######################


def check_initialize_default_behavior():
    cand_chunks = {
        'pre': CandChunks(),
        'post': CandChunks(),
        'entire': CandChunks(should_init_default = False)
        }
     
    report = candchunks_report(cand_chunks['pre'].chunks)
    
    assert len(cand_chunks['pre'].chunks) == 47,\
        'Cand chunks is not of length 47 for pre Dictionary'
    assert cand_chunks['pre'].chunks == cand_chunks['post'].chunks,\
        'Pre and post candchunks initialization are not equal as they should be.'
    report_entire = candchunks_report(cand_chunks['entire'].chunks)
    
    assert not report_entire,\
        'Entire word candchunks initialization wrongly has elements.'
        
def check_prefix_decode():
    """
    Checks default and prefix decodes without retroactive word filter.
    """
    
    #11/8: Formatting from phonix
    words = {
        'aj': 'æ1>a|j>j', #Test single default decode: NO CHUNK
        'abakj': 'æ1>a|c>b|æ1>a|i>k|j>j',
            #On ab: Test prefix memorization (default fail): CHUNK
            #On abak: Test partial decode and memorize (default fail): CHUNK
        'abj': 'æ1>a|c>b|j>j' #Test full mixed default and memorized decode: NO CHUNK
    }
    
    expected_chunks = {'ab': 'æc', 'abak': 'æcæi'} #Grapheme: Actual P
    add_default_dict(expected_chunks)
     
    del(expected_chunks['oi']) #Because it is decodable
    
    df = gen_data_dict_and_df(words)
    
    #Note: there is no word-based retroactive filter here, or all of chunks would be removed.

    cand_chunks = cand_chunks_gen.candidate_chunks(df)
    final_subchunks = decoding.find_sight_subchunks('pre', *subchunks_init(cand_chunks))
    
    report = ""
    for key, sub_chunks in final_subchunks.items():
        report += f"{key}\n"
        for word, info in sub_chunks.items():
            report += f'\t{word}\n'
            report += f'\t\t{info}\n'
    
    #2 extra chunks, 1 removed because of "oi", 47 default pairs.
    assert len(final_subchunks['pre']) == 2 + 47 - 1, 'Pre wrong length.'
    assert expected_chunks == {this_g : final_subchunks['pre'][this_g]['P']\
                                for this_g in expected_chunks},\
            'Expected behavior for prefix (no retroactive filter) decode failed.'
    
    return report
    

def check_postfix_decode():
    """
    Checks default and postfix decodes without retroactive word filter.
    """
    
    #11/8: Formatting from phonix
    words = {
        'ab': 'æ1>a|c>b', #Test single default mnemorize: CHUNK
        'aaba': 'æ1>a|æ1>a|c>b|æ1>a', #Mixed default (a) and memorized (ab) decode.
        'abakj': 'æ1>a|c>b|æ1>a|i>k|j>j'
            #On j: default decode, then
            #On kj: memorize chunk (CHUNK), then
            #Rest: default/memorized mixed case.
    }
    
    expected_chunks = {'b': 'b', 'aba': 'æcæ', 'bakj': 'cæij'}
    add_default_dict(expected_chunks)
    df = gen_data_dict_and_df(words)
    
    #Does NOT use the retroactive word filter.
    cand_chunks = cand_chunks_gen.candidate_chunks(df)
    
    final_subchunks = decoding.find_sight_subchunks('post', *subchunks_init(cand_chunks))
    
    report = subchunks_report(final_subchunks)
    message = "Will not display 'b' as chunk, however"\
    " will check if default P is preserved in the assert in this function.\n"
    
    report += message
    
    assert final_subchunks['post']['b']['P'] == 'b', 'Default pronunciation of'\
        '"b" was not preserved.'
            
    #2 + 47 from 47 default and 2 extra chunks, minus 1 decodable default.
    #   (b is included in the 47 count.)
    #Note that the default "oi -> ɔɪ" pg pair is considered decodable,
    #   so it will be decoded in this case.
    assert len(final_subchunks['post']) == (2 + 47 - 1), 'Length of final subchunks incorrect.'
    
    del(expected_chunks['oi']) #See the note above.
   
    assert expected_chunks == {this_g : final_subchunks['post'][this_g]['P']\
                            for this_g in expected_chunks},\
        'Expected behavior for postfix decode failed.'
        
    return report
 
    
def check_length_filtering_and_decode():
    
    """
    Checks length filtering behavior and decode behavior (pre, post, and entire)
    Also briefly checks preservation of non-decodable words
        in the entire words Dict.
    """

    #10/25: Words and pronunications directly from phonix.ipa
    
    this_case = {
       'some': 's>s|ʌ1>o|m>me',
       'eat': 'i1>ea|t>t',
       'atom': 'æ1>a|t>t|ʌ0>o|m>m',
       'somewhat': 's>s|ʌ1>o|m>me|w>wh|ʌ1>a|t>t',
       'what': 'w>wh|ʌ1>a|t>t',
       'akwhat':'ʌ1>a|k>k|w>wh|ʌ1>a|t>t' 
       #Above: nonsense word, this is to check the filtering
       #    for partial example filtering on "what".
       #It is also a case for undecodable word.
       }

    df = gen_data_dict_and_df(this_case)
    filtered_chunks = cand_chunks_gen.candidate_chunks(df)
    
    #p. 54a
    #Below: exclude "ea" because it is default.
    expected_prefixes = {
        'so': 'sʌ', #Examples: some, only. Is the partial filter examples.
        'ato': 'ætʌ',
        'somewha': 'sʌmwʌ',
        'wha': 'wʌ',
        'akwha': 'ʌkwʌ'
        }
    
    expected_postfixes = {
        'ome': 'ʌm',
        'tom': 'tʌm',
        'at': 'ʌt', #Examples: what, only. Is the partial filter examples.
        'omewhat': 'ʌmwʌt',
        'kwhat': 'kwʌt'
        }
    
    expected_entire_post_decode = {
        'akwhat': 'ʌkwʌt'
        }
    
    expected = {
        'pre': expected_prefixes,
        'post': expected_postfixes,
        }
    
    #Test candidate chunks if is as expected for pre, post.
    
    report = ""
    
    for this_type in ['pre', 'post']:
        
        this_filtered = filtered_chunks[this_type]
        this_expected = expected[this_type]
        
        this_expected.update(default_chunks)
        
        report += candchunks_report(this_filtered) + '\n'
        
        assert all(len(this_filtered[graph]['examples']) == 1\
                   for graph in this_filtered\
                       if graph not in default_chunks),\
            "New chunks' examples length were not all one."
      
        assert run_dict_pg_match(this_filtered, this_expected),\
            f'Equality of expected, actual failed for type {this_type}.'
        
    #Test for undecodable words (also a general test of prefix accept, reject undecodable)
    
    result_decode = decoding.find_sight_chunks(filtered_chunks)

    expected_prefix_decode = {
        'so':'sʌ',
        'ato':'ætʌ',
        'somewha':'sʌmwʌ',
        'akwha': 'ʌkwʌ',
        'wha':'wʌ'
        }
    expected_postfix_decode = {
        'at':'ʌt',
        'ome':'ʌm',
        'tom':'tʌm',
        'omewhat':'ʌmwʌt',
        'kwhat':'kwʌt'
        }
    
    expected_undecodable_words = {
        'some': 'sʌm'
        }
    
    expected_decode = {
        'pre': expected_prefix_decode,
        'post': expected_postfix_decode,
        'entire': expected_undecodable_words
        }
    
    add_default_dict(expected_decode['pre'])
    add_default_dict(expected_decode['post'])
    
    del(expected_decode['pre']['oi']) #Because oi is decodable.
    del(expected_decode['post']['oi']) #Because oi is decodable.

    
    for this_type in ['pre', 'post', 'entire']:
        
        report = subchunks_report(result_decode) + '\n'
        
        assert run_dict_pg_match(result_decode[this_type], expected_decode[this_type]),\
            'Entire undecodable result did not match.'
    
    
def check_decode_pre_post_success():
    """
    Tests for expected behavior for decoding
        within pre, post with smaller pre or post.
    The c -> j is deliberate. It is for testing purposes.
    """
    
    #Prefixes
    pre_case = {
        'abck': 'ʌ>a|b>b|c>c|k>k',
        'abcde': 'ʌ>a|b>b|c>c|d>d|i>e'
        }
    post_case = {
        'dfbcd': 'd>d|f>f|b>b|j>c|d>d',
        'dbcd': 'd>d|b>b|j>c|d>d'
        }
    
    #Expected candchunks by inspection.
    #For Pre: abc with abck as example only. abcd with abcde as example.
    #For Post: bcd with dbcd as example only. fbcd with dfbcd as example.
    
    expected_pre_decode = {
        'abc':'ʌbc', #ʌbcd should be decodable. Mixed default and memorized decode.
        }
    expected_post_decode = {
        'bcd': 'bjd' #fbcd should be decodable, like prefix.
        }
    
    check_which = {'pre': 'abc', 'post':'bcd'}
    
    #Below: because oi is decodable
    add_default_dict(expected_pre_decode); del(expected_pre_decode['oi'])
    add_default_dict(expected_post_decode); del(expected_post_decode['oi'])
    
    cases = {'pre': pre_case, 'post': post_case}
    expected = {'pre': expected_pre_decode, 'post': expected_post_decode}

    
    for this_type in ['pre', 'post']:
        
        df = gen_data_dict_and_df(cases[this_type])
        cand_chunks = cand_chunks_gen.candidate_chunks(df)
    
        this_decode = decoding.find_sight_subchunks(this_type, *subchunks_init(cand_chunks))
        
        #The length is 47 default, minus "oi", plus the one new chunk.
        
        assert len(this_decode[this_type]) == 1 + 47 - 1, 'Result has wrong length'
        
        which_key  = check_which[this_type] 
        
        assert this_decode[this_type][which_key]['P'] == expected[this_type][which_key],\
            "Contents of actual and expected don't match"
            
def check_2_ipa_check():
    """
    This is manually checked. An AssertionError should occur with the neg_case.
    """

    pos_case = pd.DataFrame.from_records({'Word': ['a', 'b']})
    neg_case = pd.DataFrame.from_records({'Word': ['a', 'b', 'a']})
    
    decoding.check_if_no_2_ipa(pos_case)
    print('Positive test case passed.')
    
    decoding.check_if_no_2_ipa(neg_case) #Assertion should happen here
    assert False, 'Negative test case passed, but it should not have.'

if __name__ == '__main__':
    check_prefix_decode()
    check_postfix_decode()
    check_length_filtering_and_decode()
    check_decode_pre_post_success()
    #check_2_ipa_check()
    