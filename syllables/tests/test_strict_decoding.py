#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 20:12:13 2020

@author: nicolewong
"""

# 11/8: managing the imports
# https://stackoverflow.com/questions/4383571/importing-files-from-different-folder
# 11/8: For directory help:
# https://superuser.com/questions/717105/how-to-show-full-path-of-a-file-including-the-full-filename-in-mac-osx-terminal/1533160

import sys

code_path = '/Users/nicolewong/Desktop/urop/code/syllables'
sys.path.insert(1, code_path)

import imports

imports.import_files()

from word_tools import word_funcs
from decoding import strict_decoding
import load_words

def test_default_irregular_remainder():
    # 12/22 Text from phonix
    cases = [
        'p>p|r>r|i>ea|tʃ>ch',
        'p>p|r>r|ʌ>o|t>t|ɛ>e|s>s|t>t',
        'ʌ>a|b>b'
    ]

    cases = map(word_funcs.get_mapping, cases)

    _, _, default_set = load_words.load_my_celex_phonix_data()

    expected = ['',
                word_funcs.get_mapping('ʌ>o|t>t|ɛ>e|s>s|t>t'),
                word_funcs.get_mapping('ʌ>a|b>b')
                ]
    actual = [
        strict_decoding.default_irregular_remainder_forward(case, default_set)
        for case in cases
    ]

    cases = [
        'p>p|r>r|i>ea|tʃ>ch',
        'p>p|r>r|ʌ>o|t>t|ɛ>e|s>s|t>t',
        'ʌ>a|b>b'
    ]
    cases = map(word_funcs.get_mapping, cases)

    expected = [
        '',
        word_funcs.get_mapping('p>p|r>r|ʌ>o|t>t|ɛ>e'),
        word_funcs.get_mapping('ʌ>a')
    ]
    actual = [
        strict_decoding.default_irregular_remainder_forward(case[::-1], default_set)[::-1]
        for case in cases
    ]

    assert expected == actual


if __name__ == '__main__':

    tests = [
        test_default_irregular_remainder
    ]

    for test in tests:
        test()
    print('Passed tests')

