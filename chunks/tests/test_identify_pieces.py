# 11/8: managing the imports
# https://stackoverflow.com/questions/4383571/importing-files-from-different-folder
# 11/8: For directory help:
# https://superuser.com/questions/717105/how-to-show-full-path-of-a-file-including-the-full-filename-in-mac-osx-terminal/1533160


import sys

code_path = '../..'
sys.path.insert(1, code_path)

"""
Tests relating to vowel and consonants,
    as well as word classes like CV, VC, and CVC.
"""

from chunks.word_tools import word_funcs, identify_pieces
from chunks import load_words
from chunks.file_gen import data_run_once

from os.path import join

def post_test_compare():
    """
    For ensuring that refactored and regenerated all phoneme text file
        matches the phonemes in the union of the vowels and consonants pg pairs.
    Note that the original file divided into consonants and vowels,
        was not generated using the code currently in this repository,
            to avoid having to re-divided consonants and vowels.
    This test confirms, however, the behavior would have been equivalent.
    """

    save_split_path = '/Users/nicolewong/Desktop/urop/code/chunks/files'

    vowel_path = join(save_split_path, 'all_P_vowels.txt')
    consonant_path = join(save_split_path, 'all_P_pure_consonants.txt')

    resaved_path = join(save_split_path, 'all_P_check.txt')

    with open(resaved_path, 'r') as resaved:
        resaved_text = sorted(resaved.readlines())

    union_text = []
    with open(vowel_path, 'r') as v:
        union_text += v.readlines()

    with open(consonant_path, 'r') as c:
        union_text += c.readlines()

    resaved_text = [piece.strip() for piece in sorted(resaved_text)]
    union_text = [piece.strip() for piece in sorted(union_text)]

    assert union_text == resaved_text, 'post_test_compare failed.'


def test_identify_P():
    """
    For identifying all of the phonemes in the data.
    """

    # Below: from phonix 12/17
    text = [
        'abatement ʌ>a|b>b|eɪ>a|t>te|m>m|ɛ>e|n>n|t>t',
        'burro b>b|ɝ>urr|oʊ>o',
        'abating ʌ>a|b>b|eɪ>a|t>t|ɪ>i|ŋ>ng'
    ]

    expected = sorted(['ʌ', 'b', 'eɪ', 't', 'm', 'ɛ', 'n', 'ɝ', 'oʊ',
                       'ɪ', 'ŋ'])
    actual = data_run_once.identify_p_types(text)

    assert sorted(expected) == actual, 'Identity test failed.'


def test_is_vowel_consonant():
    """
    Note that this test relies on correct file organization.
        The correct vowel and consonant txt files from the main
            will have to be downloaded from Github,
                and the path correctly specified.
    """

    cases = ['j>hy', 'aɪ>yi', 'ɪ>y', 'b>b', 'dʒ>je', 'oʊ>eaux']

    cases = [pair[0] for pair in list(map(word_funcs.get_pg_pair, cases))]

    expected_vowel = [False, True, True, False, False, True]
    expected_consonant = [not answer for answer in expected_vowel]

    actual_vowel = list(map(identify_pieces.is_vowel, cases))
    actual_consonant = list(map(identify_pieces.is_consonant, cases))

    assert actual_vowel == expected_vowel and expected_consonant == actual_consonant


def test_identify_units():
    """
    CVC, VC, CV tests.
    """

    cases_cvc = ['cat', 'up', 'egg']
    expected_cvc = [True, False, False]

    # Below: This tests for pg pair being used as the unit, not letters.
    # Therefore, ea/ch is still a VC under this definition.
    cases_vc = ['at', 'each', 'by']
    expected_vc = [True, True, False]

    # "Shy", "see" are CV, as it counts pg as unit, not letters.
    cases_cv = ['shy', 'at', 'see']
    expected_cv = [True, False, True]

    case_funcs = [
        identify_pieces.is_cvc,
        identify_pieces.is_vc,
        identify_pieces.is_cv,
    ]

    case_sets = [cases_cvc, cases_vc, cases_cv]
    expected_sets = [expected_cvc, expected_vc, expected_cv]

    for case_set, expected_set, func in zip(case_sets, expected_sets, case_funcs):
        this_result = [func(word_dict[word]) for word in case_set]
        assert expected_set == this_result, 'Failure in identify units tests.'


DATA_FOLDER = '../files'
word_dict = load_words._load_raw_phonix(DATA_FOLDER)

if __name__ == '__main__':
    tests = [
        test_is_vowel_consonant,
        test_identify_units,
        test_identify_P,
        post_test_compare,
    ]

    for test in tests:
        test()

    print('Passed tests')