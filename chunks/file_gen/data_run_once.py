"""
These are used to generate files only once.
    These files correspond to the "all_P" files in the "data" folder.
Note that this is the restructured file used to ensure correctness,
    NOT the code originally used to generate the file of all pg pairs used in practice,
    that is, the sourced divided into "vowel-like" vs. "consonant-like" pg pairs.
        However, if I remember correctly, they were checked to result in same behavior.
"""

import os
from os.path import join, exists
from chunks import load_words

########################
##### GENERATE P #######
########################

def identify_p_types(data_lines):
    """
    You won't have to run this again,
        just use the manually divided consonants and vowels text files.
    Inputs:
        data_lines,
            the lines of the text file.
            If I remember correctly, these should be the lines of phonix.
    Outputs:
        all_phonemes, a List of phonemes in pg pairs.
    """
    all_P = [line.split()[1] for line in data_lines]
    all_phonemes = set()

    for this_p in all_P:
        this_pairs = this_p.split('|')
        all_phonemes |= set(pair.split('>')[0] for pair in this_pairs)

    all_phonemes = sorted(list(all_phonemes))

    return all_phonemes


def save_all_p_types(load_path, save_path=''):
    """
    You won't have to use this,
        just use the consonant and vowel pg pairs in "data" folder.
    Inputs:
        load_path, str, the parent folder of your data generally.
            You will have to change this to fit your local file organization.
        save_path (default: empty str),
            the filename to which to save all phonemes.
    Outputs:
        sorted list (by length)
            of all P types pairs in df, a DataFrame.

        Also will save it to save_path, if specified.
    """

    phonix_path = join(load_path, join('full_data', 'phonix.txt'))

    with open(phonix_path, 'r') as f:
        all_phonemes = identify_p_types(f.readlines())

    all_phonemes = [elem + '\n' for elem in all_phonemes]

    with open(save_path, 'w') as s:
        s.writelines(all_phonemes)

if __name__ == '__main__':

    DATA_FOLDER = '/Users/nicolewong/Desktop/urop/Data'
    popular_words_order, word_dict = load_words.load_data(DATA_FOLDER)

    syllable_path = join(DATA_FOLDER, 'old_syllables')
    if not exists(syllable_path):
        os.makedirs(syllable_path)

    all_P_path = join(syllable_path, 'all_P_check.txt')