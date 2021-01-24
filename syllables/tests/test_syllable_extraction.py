# 11/8: managing the imports
# https://stackoverflow.com/questions/4383571/importing-files-from-different-folder
# 11/8: For directory help:
# https://superuser.com/questions/717105/how-to-show-full-path-of-a-file-including-the-full-filename-in-mac-osx-terminal/1533160

import sys

code_path = '/Users/nicolewong/Desktop/urop/code/syllables'
sys.path.insert(1, code_path)

import imports
imports.import_files()

import identify_pieces

def test_double_consonants():

    cases = {
        'apple': ((('æ',), 'a'), (('p',), 'pp'), (('ʌ', 'l'), 'le')), #Tests one before and one after duplicate.
        'app': ((('æ',), 'a'), (('p',), 'pp')), #Tests none after duplicate
        'little' : ((('l',), 'l'), (('ɪ',), 'i'), (('t',), 'tt'), (('ʌ', 'l'), 'le')), #Tests many before duplicate.
        'meet': ((('m',), 'm'), (('i',), 'ee'), (('t',), 't')), #Tests ignore double vowels, no change.
    }

    expected = {
        'apple': ((('æ',), 'a'), (('p',), 'p'), (('p',), 'p'), (('ʌ', 'l'), 'le')),
        'app': ((('æ',), 'a'), (('p',), 'p'), (('p',), 'p')),
        'little': ((('l',), 'l'), (('ɪ',), 'i'), (('t',), 't'), (('t',), 't'), (('ʌ', 'l'), 'le')),
        'meet': ((('m',), 'm'), (('i',), 'ee'), (('t',), 't'))
    }

    actual = identify_pieces.process_dict_double_consonant(cases)

    for w, p in expected.items():
       if p != actual[w]:
           print(f"For {w}")
           print(f"\tExpected{p}")
           print(f"\tActual{actual[w]}")

    assert expected == actual

if __name__ == "__main__":

    tests = [
        test_double_consonants,
    ]

    for test in tests:
        test()
    print('Tests passed.')



