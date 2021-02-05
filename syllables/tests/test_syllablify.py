
# Please see citations in imports.py file
import sys

code_path = '/Users/nicolewong/Desktop/urop/code/syllables'
sys.path.insert(1, code_path)

imports.import_files()

from em import prep_syllablify as prep, syllablify
from word_tools import word_funcs, identify_pieces
import load_words
from file_gen import data_run_once

from segmentation import process_segs, select_segs, count_segs

from os.path import join

from collections import defaultdict

def test_select():
    phonix_dict = {
        'abb': ((('a',), 'a'), (('b',), 'b')),
        'cde': ((('c', 'd'), 'cd'), (('e',), 'e')),
        'dfe': ((('d',), 'd'), (('f'), 'fe')),
        'ya': ((('y',), 'y'), (('a',), 'a')),
        'xe': ((('x',), 'x'), (('e'), 'e'))
    }

    word_freqs = {
        'abb': 0.1,
        'cde': 0.3,
        'dfe': 0.2,
        'ya': 0.01,
        'xe': 0.01
    }

    cases = [2, 5]
    expected = [
        {
            'cde': ((('c', 'd'), 'cd'), (('e',), 'e')),
            'dfe': ((('d',), 'd'), (('f'), ('fe'))),
        },
        phonix_dict
    ]

    actual = [load_words.select_popular_n(phonix_dict, word_freqs, select_case)[1]
              for select_case in cases]

    assert actual == expected, 'Select test failed.'


def post_test_compare():
    """
    For ensuring that refactored and regenerated all phoneme text file
        matches the phonemes in the union of the vowels and consonants.
    """

    DATA_FOLDER = '/Users/nicolewong/Desktop/urop/Data'
    save_split_path = join(DATA_FOLDER, 'syllables')

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
    Note that this test relies on some file organization in prep_syllablify.py
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
    Mono, CVC, VC, CV tests.
    """

    cases_cvc = ['cat', 'up', 'egg']
    expected_cvc = [True, False, False]

    cases_mono = ['hello', 'hawk', 'funny']
    expected_mono = [False, True, False]

    # Below: This tests for pg pair being used as the unit, not letters.
    # Therefore, ea/ch is still a VC under this definition.
    cases_vc = ['at', 'each', 'by']
    expected_vc = [True, True, False]

    # "Shy", "see" are CV, as it counts pg as unit, not letters.
    cases_cv = ['shy', 'at', 'see']
    expected_cv = [True, False, True]

    cases_cvc_any = ["even", "break", "beak", "cats"]
    expected_cvc_any = [False, False, True, True]

    case_funcs = [
        identify_pieces.is_cvc,
        identify_pieces.is_mono,
        identify_pieces.is_vc,
        identify_pieces.is_cv,
        identify_pieces.is_cvc_any
    ]

    case_sets = [cases_cvc, cases_mono, cases_vc, cases_cv, cases_cvc_any]
    expected_sets = [expected_cvc, expected_mono, expected_vc, expected_cv, expected_cvc_any]

    for case_set, expected_set, func in zip(case_sets, expected_sets, case_funcs):
        this_result = [func(word_dict[word]) for word in case_set]
        assert expected_set == this_result, 'Failure in identify units tests.'


def test_gen_seg_funcs():
    cases = ['sleigh', 'any']
    short_P = list(word_dict['any'])
    # IPA string below from phonix.
    long_P = list(word_funcs.get_mapping('ɪ>e|k;s>xc|ɛ>e|l>ll|d>ed'))

    assert identify_pieces.has_vowel(word_dict['hawk']) == True
    assert identify_pieces.has_vowel(word_dict['hello']) == True
    assert identify_pieces.has_vowel(word_funcs.get_mapping('d>d|c>c|b>b')) == False

    true_seg = [[long_P[0]], long_P[1:]]
    false_seg = [long_P[:3], long_P[3:]]

    assert process_segs.valid_seg(true_seg) == True
    assert process_segs.valid_seg(false_seg) == False

    expected = [
        [],  # Sleigh is empty -- no way to divide it.
        [
            [[short_P[0]], short_P[1:]],
            [short_P[:2], [short_P[2]]]  # Rejects all, no divisions
        ],
        [
            [[long_P[0]], long_P[1:]],  # e/xcelled
            [long_P[:2], long_P[2:]]  # exc/elled
        ]
    ]

    actual = [process_segs.gen_valid_segmentations(word_dict[case])
              for case in cases]
    actual += [process_segs.gen_valid_segmentations(long_P)]

    assert actual == expected, ''


def test_gen_unit_counts():
    """
    Designed to work with strict unstable filtering.
    """

    words = ['cat', 'at', 'my', 'bat', 'hello', 'care', 'cen']
    cen_P = word_funcs.get_mapping('s>c|i>e|n>n')

    word_inputs = {word: word_dict[word]
                   for word in words[:-1]}

    word_inputs['cen'] = cen_P

    # Above: tests:
    # CVC, VC, CV, mono, word that should not be a unit.
    # "at" part of two classes (mono and VC)
    #   Tests if overcounting is prevented.
    # Non-singular count of stable "at" across classes, within a single class (CVC).
    #   This is accumulating counts.
    # Tests if pooled counts allocated to all types of g>p pairs.

    # 12/16: https://stackoverflow.com/questions/30356892/defaultdict-with-default-value-1
    expected_counts = defaultdict(lambda: 0.5)

    values = {  # Pooled values.
        'k>c': 3, 'k>c|æ>a|t>t': 1,
        'æ>a|t>t': 3,
        'm>m|aɪ>y': 1,
        'b>b': 1, 'b>b|æ>a|t>t': 1,
        'i>e|n>n': 1,
        's>c': 3, 's>c|i>e|n>n': 1,
        'k>c|ɛ>a|r>re': 1, 'ɛ>a|r>re': 1
    }

    values = {key: val + 0.5
              for key, val in values.items()}

    expected_counts.update(values)
    actual_counts = prep.gen_unit_counts(word_inputs)

    assert expected_counts == actual_counts, 'Gen unit counts test failed.'
    assert actual_counts['lizard'] == 0.5, 'Retrieval of unseen unit failed.'


def test_select_max_probs():
    words = ['at', 'cat', 'er', 'singer', 'cater']

    # 12/17: Phonix text throughout this case.
    word_data = {word: word_dict[word] for word in words[:-3]}
    word_data['er'] = word_funcs.get_mapping('ɝ>er')

    word_data['singer'] = word_funcs.get_mapping('s>s|ɪ>i|ŋ>ng|ɝ>er')
    word_data['cater'] = word_funcs.get_mapping('k>c|eɪ>a|t>t|ɝ>er')

    expected_freq_dict = {
        'æ>a|t>t': 2.5,  # No breakdown possible.
        'k>c|æ>a|t>t': 1.5,  # No breakdown possible.
        'ɝ>er': 1.5,  # No breakdown possible.

        's>s|ɪ>i|ŋ>ng:ɝ>er': 0.5 * 1.5,  # Accept a breakdown.
        's>s|ɪ>i:ŋ>ng|ɝ>er': 0.5 * 0.5,  # Unpopular divison.

        'k>c|eɪ>a|t>t:ɝ>er': 0.5 * 1.5,  # Reject breakdown of "cat" to "æ>a", even if same G.
        'k>c|eɪ>a:t>t|ɝ>er': 0.5 * 0.5  # Reject breakdown of "cat" to "æ>a", even if same G.
    }

    expected_selections = {
        'at': 'æ>a|t>t',  # No breakdown possible.
        'cat': 'k>c|æ>a|t>t',  # No breakdown possible.
        'er': 'ɝ>er',  # No breakdown possible.
        'singer': 's>s|ɪ>i|ŋ>ng:ɝ>er',  # Accept a breakdown.
        'cater': 'k>c|eɪ>a|t>t:ɝ>er'  # Reject breakdown of "cat" to "æ>a", even if same G.
    }

    unit2counts = prep.gen_unit_counts(word_data)
    valid_segs = {word: process_segs.gen_valid_segmentations(ipa_str)
                  for word, ipa_str in word_data.items()}

    actual_selections, actual_freq_dict = select_segs.select_max_probs(word_data,
                                                                      unit2counts,
                                                                      valid_segs, debugging = True)
    assert expected_selections == actual_selections, \
        "Selections for select max prob didn't match."

    for seg in actual_freq_dict:
        a_val = actual_freq_dict[seg]
        e_val = expected_freq_dict[seg]

        assert int(a_val * 100) == int(e_val * 100), \
            "Segmentation scores for select max prob didn't match."


def test_calc_piece_freq():
    # From Phonix 12/19
    word_data = {
        'singer': 's>s|ɪ>i|ŋ>ng:ɝ>er',
        'er': 'ɝ>er',
        'singing': 's>s|ɪ>i|ŋ>ng:ɪ>i|ŋ>ng',
        'cater': 'k>c|eɪ>a|t>t:ɝ>er',
        'cat': 'k>c|æ>a|t>t',
    }

    actual = count_segs.calc_piece_freqs(word_data)
    expected = {
        'ɝ>er': 3.5,
        's>s|ɪ>i|ŋ>ng': 2.5,
        'ɪ>i|ŋ>ng': 1.5,
        'k>c|eɪ>a|t>t': 2.5,
        'k>c|æ>a|t>t': 2.5  # This and above: test pooling behavior across graphemes.
    }

    assert expected == actual


def test_mult_iterations():
    """
    Note: This has to be updated for onsets and rimes behavior, but it worked on normal EM algorithm.
    """

    # 12/19: Phonix text throughout case.
    word_data = {
        'lyon': 'l>l|i>y|oʊ>o|n>n',
        'sad': 's>s|æ>a|d>d',
        'sadly': 's>s|æ>a|d>d|l>l|i>y',
        'only': 'oʊ>o|n>n|l>l|i>y',
        'adly': 'æ>a|d>d|l>l|i>y'  # Fictional to get non-uniform second update case.
    }

    word_data = {k: word_funcs.get_mapping(v)
                 for k, v in word_data.items()
                 }

    asserts_values = {
        0: {
            'score': {
                'lyon': 0.5 ** 2,
                'sad': 1.5,
                'sadly': 1.5 * 0.5,
                'only': 0.5 ** 2,
                'adly': 1.5 * 0.5
            },
            'old_syllables': {
                'lyon': 'l>l|i>y:oʊ>o|n>n',
                'sad': 's>s|æ>a|d>d',
                'sadly': 's>s|æ>a|d>d:l>l|i>y',
                'only': 'oʊ>o:n>n|l>l|i>y',
                'adly': 'æ>a|d>d:l>l|i>y'
            },
            'this_counts': {
                'l>l|i>y': 3.5,
                'oʊ>o|n>n': 1.5,
                's>s|æ>a|d>d': 2.5,
                'oʊ>o': 1.5,
                'n>n|l>l|i>y': 1.5,
                'æ>a|d>d': 1.5
            }
        },
        1: {
            'score': {
                'lyon': 3.5 * 1.5,
                'sad': 2.5,
                'sadly': 2.5 * 3.5,
                'only': 1.5 * 3.5,
                'adly': 1.5 * 3.5
            },
            'old_syllables': {
                'lyon': 'l>l|i>y:oʊ>o|n>n',
                'sad': 's>s|æ>a|d>d',
                'sadly': 's>s|æ>a|d>d:l>l|i>y',
                'only': 'oʊ>o|n>n:l>l|i>y',
                'adly': 'æ>a|d>d:l>l|i>y'
            },
            'this_counts': {
                'l>l|i>y': 4.5,
                'oʊ>o|n>n': 2.5,
                's>s|æ>a|d>d': 2.5,
                'æ>a|d>d': 1.5
            }
        },
        2: {
            'score': {
                'lyon': 4.5 * 2.5,
                'sad': 2.5,
                'sadly': 2.5 * 4.5,
                'only': 2.5 * 4.5,
                'adly': 1.5 * 4.5
            },
            'old_syllables': {
                'lyon': 'l>l|i>y:oʊ>o|n>n',
                'sad': 's>s|æ>a|d>d',
                'sadly': 's>s|æ>a|d>d:l>l|i>y',
                'only': 'oʊ>o|n>n:l>l|i>y',
                'adly': 'æ>a|d>d:l>l|i>y'
            },
            'this_counts': {
                'l>l|i>y': 4.5,
                'oʊ>o|n>n': 2.5,
                's>s|æ>a|d>d': 2.5,
                'æ>a|d>d': 1.5
            }
        },
    }

    should_run = True
    if should_run:
        syllables = syllablify.gen_syllable_divisions(sorted(word_data.keys()), word_data,
                                                      '', num_epochs=3, scoring=True, verbose=True,
                                                      asserts=asserts_values)

        assert syllables == asserts_values[2]['old_syllables']

DATA_FOLDER = '/Users/nicolewong/Desktop/urop/Data'
_, word_dict = load_words.load_data(DATA_FOLDER)

if __name__ == '__main__':
    tests = [
        test_is_vowel_consonant,
        test_identify_units,
        test_identify_P,
        test_gen_seg_funcs,
        post_test_compare,
        test_select,
        test_gen_unit_counts,
        test_select_max_probs,
        test_calc_piece_freq,
        # test_mult_iterations, #This will definitely broken by the onset and rime function.
    ]

    for test in tests:
        test()

    print('Passed tests')