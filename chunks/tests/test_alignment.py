
# 11/8: managing the imports
# https://stackoverflow.com/questions/4383571/importing-files-from-different-folder
# 11/8: For directory help:
# https://superuser.com/questions/717105/how-to-show-full-path-of-a-file-including-the-full-filename-in-mac-osx-terminal/1533160

import sys

code_path = '/Users/nicolewong/Desktop/urop/code/'
sys.path.insert(1, code_path)

from chunks.word_tools import alignment, identify_pieces


def test_align_pg_and_syllables():

    #   Breakdowns are from CELEX.
    #   The chunks

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

if __name__ == "__main__":

    tests = [
        test_align_pg_and_syllables,
    ]

    for test in tests:
        test()
    print('Tests passed.')
