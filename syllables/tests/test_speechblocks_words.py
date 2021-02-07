# 11/8: managing the imports
# https://stackoverflow.com/questions/4383571/importing-files-from-different-folder
# 11/8: For directory help:
# https://superuser.com/questions/717105/how-to-show-full-path-of-a-file-including-the-full-filename-in-mac-osx-terminal/1533160

import sys

code_path = '/Users/nicolewong/Desktop/urop/code/'
sys.path.insert(1, code_path)

from syllables.celex_processing import hierarchy
from syllables import load_words

from syllables.word_tools import word_funcs
from syllables.decoding import strict_decoding

from collections import defaultdict

from os.path import join

def test_filter_popular_chunks():

    this_input_words = {
        'a': {'ab', 'ac'},
        'b': {'bc'},
    }

    this_input_counts = {
        'ab': 2,
        'ac': 4,
        'bc': -1,
    }

    expected = {
        'a': 'ac',
        'b': 'bc',
    }
    actual = hierarchy.filter_popular_chunks(this_input_words, this_input_counts)

    print(actual)
    assert expected == actual

def test_load_words():

    # 2/5: Test_case from reference-dictionary.txt
    expected = {'adolescent', 'adornment', 'diamond', 'pearl', 'necklace', 'ring'}
    test_case = (
        "adolescent adolescent_1,adolescent_2,adolescent_3,adolescent_4,adolescent_5,adolescent_6,adolescent_7,adolescent_8,adolescent_9,adolescent_10,adolescent_11,adolescent_12,adolescent_13,adolescent_14,adolescent_15\nadornment diamond,pearl,necklace,ring.1").split(
        '\n')

    actual = load_words.process_word_list(test_case)

    assert actual == expected


def test_find_irregular_chunks():

    ## Testing with arbitrary chunks.

    # 2/6: Inputs from phonix.
    inputs = {
        'apple': {'æ>a|p>pp|ʌ;l>le'}, # Testing partial decode
        'cap': {'k>c|æ>a|p>p', 'k>c|æ>a|x>p'}, # Testing full decode, then partial decode.
        'ap': {'æ>a|p>p'}, #Testing full decode for entry
        'blue': {'b>b|l>l|u>ue'}, # Testing entire no decode.
    }

    chunks = {
        'k>c',
        'æ>a|p>p',
        'æ>a|p>pp',
    }

    inputs = { word : set(map(word_funcs.get_mapping, ipa_collect)) for word, ipa_collect in inputs.items()}
    chunks = set(map(word_funcs.get_mapping, chunks))

    expected = defaultdict(set)
    expected.update({
        'apple': {'æ>a|p>pp|ʌ;l>le'},
        'cap': {'k>c|æ>a|x>p'},
        'blue': {'b>b|l>l|u>ue'},
    })

    expected = {word: set(map(word_funcs.get_mapping, ipa_collect)) for word, ipa_collect in expected.items()}

    actual = strict_decoding.find_irregular_chunks(inputs, chunks)

    ## Test decoding with default pg pairs.
    INPUTS_FOLDER = '/Users/nicolewong/Desktop/urop/Data/Inputs'
    DEFAULT_P_PATH = join(INPUTS_FOLDER, 'grapheme_defaults.txt')

    default_pg_set = load_words.create_default_pg_tuples(DEFAULT_P_PATH)
    assert expected == actual

    ## Testing with default pg pairs.

    pg_input = {
        'gskoa' : {word_funcs.get_mapping('g>g|s>s|k>k|oʊ>oa')},
        'gskob': {word_funcs.get_mapping('g>g|s>s|k>k|oʊ>ob')}
    }

    #TODO: Update this for the new default pg pairs

    expected_decode_on_pg = defaultdict(set)
    expected_decode_on_pg['gskob'] = pg_input['gskob']

    decode_on_pg = strict_decoding.find_irregular_chunks(pg_input, default_pg_set)

    assert decode_on_pg == expected_decode_on_pg

def test_find_default_pg_pairs():

    # 2/7: Inputs modified from phonix.
    inputs = {
        'appa': 'æ>a|p>pp|æ>a|i>a',
        'ccce': 'k>c|k>c|k>ce',
        'f>f' : 'f>f',
        'lelea': 'l>le|l>le|æ>a',
        'æ>a': 'æ>a',
    }

    inputs = {word: word_funcs.get_mapping(ipa) for word, ipa in inputs.items()}

    expected_all_pgs = defaultdict(set)
    expected_all_pgs.update({
        'a': {word_funcs.get_mapping('æ>a'), word_funcs.get_mapping('i>a')},
        #   Notice that double consonants and consonant silent e are not accepted!
        'c': {word_funcs.get_mapping('k>c')},
        'f': {word_funcs.get_mapping('f>f')},
    })

    expected_counts = defaultdict(int)
    expected_counts.update({
        word_funcs.get_mapping('æ>a') : 4,
        word_funcs.get_mapping('i>a'): 1,
        word_funcs.get_mapping('k>c') : 2,
        word_funcs.get_mapping('f>f'): 1,
    })

    all_pgs, all_pg_counts = strict_decoding.find_all_pg_pairs(inputs)

    assert all_pgs == expected_all_pgs, 'Failed at all pgs'
    assert all_pg_counts == expected_counts, 'Failed at expected counts for pgs'

    default_pg_pairs = strict_decoding.find_default_pg_pairs(inputs)

    expected_default_pg_pairs = {
        'a': word_funcs.get_mapping('æ>a'),
        'c': word_funcs.get_mapping('k>c'),
        'f': word_funcs.get_mapping('f>f'),
    }

    assert default_pg_pairs == expected_default_pg_pairs, 'Failed at default pg pair comparison'

    default_pg_pairs_with_top_n = strict_decoding.find_default_pg_pairs(inputs, top_n = 2)

    expected_default_pg_pairs_top_n = {
        'a': word_funcs.get_mapping('æ>a'),
        'c': word_funcs.get_mapping('k>c'),
    }

    assert default_pg_pairs_with_top_n == expected_default_pg_pairs_top_n,\
        "Failed at top n filtering for default pg pairs."


def test_hierarchy():

    celex_inputs = {
        'abc': 'abc',
        'abecaaacd': 'abe-caaa-cd',
        'cdee': 'cd-ee',
        'b': 'b',
        'cat': 'cat',
        'lat': 'lat',
        'latcd': 'lat-cd',
        'bat': 'bat',
        'ddd': 'ddd',
    }
    phonix_inputs = {
        'abc' : 'i>a|b>b|c>c',
        'abecaaacd': 'a>a|b>be|c>c|a>a|a>a|a>a|c>c|f>d',
        'cdee': 'c>c|f>d|e>e|e>e',
        'b': 'b>b',
        'cat': 'k>c|æ>a|t>t',
        'lat': 'l>l|ʌ>a|q>t',
        'latcd': 'l>l|ʌ>a|q>t|c>c|g>d',
        'bat': 'b>b|æ>a|t>t',
        'rat': 'r>r|æ>a|t>t',
        'ddd': 'd>d|d>d|d>d',
    }

    phonix_inputs = {word: word_funcs.get_mapping(ipa) for word, ipa in phonix_inputs.items()}

    expected_chunks = {
        'a>a', 'b>b', 'c>c', 'd>d', 'l>l', 'd>d', 'e>e', 't>t', 'r>r', #pg pairs
        'k>c', 'æ>a|t>t', # Onsets/rimes
        'a>a|b>be', 'i>a|b>b|c>c', 'l>l|ʌ>a|q>t', 'c>c|f>d', # Syllables
        'l>l|ʌ>a|q>t|c>c|g>d', # Words
    }

    expected_chunks = set(map(word_funcs.get_mapping, expected_chunks))
    actual_chunks = hierarchy.find_chunks(celex_inputs, phonix_inputs)

    assert actual_chunks == expected_chunks, 'Hierarchy chunk-finding test failed.'

if __name__ == '__main__':

    tests = [
        #test_load_words,
        #test_filter_popular_chunks,
        #test_find_irregular_chunks,
        #test_find_default_pg_pairs
        test_hierarchy,
    ]

    for test in tests:
        test()

    print('Tests passed')
