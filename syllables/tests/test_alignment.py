
# 11/8: managing the imports
# https://stackoverflow.com/questions/4383571/importing-files-from-different-folder
# 11/8: For directory help:
# https://superuser.com/questions/717105/how-to-show-full-path-of-a-file-including-the-full-filename-in-mac-osx-terminal/1533160

import sys

code_path = '/Users/nicolewong/Desktop/urop/code/syllables'
sys.path.insert(1, code_path)

import imports

imports.import_files()

from word_tools import alignment, identify_pieces


def test_align_pg_and_syllables():

    #   Breakdowns are from CELEX.
    #   The syllables

    inputs = {
        'to' : ((('t',), 't'), (('u',), 'o')),
        #   Do nothing, handle single syllable
        'feel-ing' : ((('f',), 'f'), (('i',), 'ee'), (('l',), 'l'), (('ɪ',), 'i'), (('ŋ',), 'ng')),
        #   Ignore double vowels
        'cer-tain-ly': ((('s',), 'c'), (('ɝ',), 'er'), (('t',), 't'), (('ʌ',), 'ai'), (('n',), 'n'), (('l',), 'l'), (('i',), 'y')),
        #   Handle long breakdowns with multiple grapheme letters
        'lit-tle': ((('l',), 'l'), (('ɪ',), 'i'), (('t',), 'tt'), (('ʌ', 'l'), 'le')),
        #  Handle double consonants, multiple phoneme letters
    }

    inputs = identify_pieces.process_dict_double_consonant(inputs)

    expected = {
        'to' : [
            ((('t',), 't'), (('u',), 'o'))
        ],
        'feeling' : [
            ((('f',), 'f'), (('i',), 'ee'), (('l',), 'l')),
            ((('ɪ',), 'i'), (('ŋ',), 'ng')),
        ],
        'certainly' : [
            ((('s',), 'c'), (('ɝ',), 'er')),
            ((('t',), 't'), (('ʌ',), 'ai'), (('n',), 'n')),
            ((('l',), 'l'), (('i',), 'y')),
        ],
        'little': [
            ((('l',), 'l'), (('ɪ',), 'i'), (('t',), 't')),
            ((('t',), 't'), (('ʌ', 'l'), 'le')),
        ]
    }

    actual = {
        word.replace('-', '') : alignment.align_pg_and_syllables(word.split('-'), pg_info)
        for word, pg_info in inputs.items()
    }

    assert expected == actual


def explore_alignment_exceptions():

    """
    Note: This was on non-intersection with SpeechBlocks, so the list of exceptions needs to be re-generated.
    """

    #   1/24 Some "exception" cases from CELEX/phonix.txt
    #   In order: silent letters, merged r, merged double r
    cases = [
        (
            "be-lov-ed",
            "b>b|ɪ>e|l>l|ʌ>o|v>ve|d>d"
        ),
        (
            "co-ro-na",
            "k>c|ɝ>or|oʊ>o|n>n|ʌ>a"
        ),
        (
            "ar-ri-val",
            "ɝ>arr|aɪ>i|v>v|ʌ>a|l>l"
        ),
    ]

    current_celex, current_phonix = cases[0]
    current_celex = current_celex.replace('--', '-').split('-')
    result = alignment.align_pg_and_syllables(current_celex, current_phonix)

    print(result)

if __name__ == "__main__":

    tests = [
        test_align_pg_and_syllables,
        #explore_alignment_exceptions
    ]

    for test in tests:
        test()
    print('Tests passed.')
