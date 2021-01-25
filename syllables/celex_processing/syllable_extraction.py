import os
from os.path import join

import imports
imports.import_files()
import load_words
from word_tools import alignment, identify_pieces, word_funcs

from collections import defaultdict
from analysis import impact
from decoding import strict_decoding, onsets_and_rimes

import matplotlib.pyplot as plt

def align_celex_syllables(celex_dict, raw_phonix_dict):
    """
    Merges celex and phonix dict syllable data with alignments.
    Inputs:
        raw_celex_dict, a Dictionary from get_celex_syllables
        phonix_dict, a Dictionary from load_data's second argument
    Outputs:
        a G->P Dict mapping (str -> sorted lists of pronunciations)
            of the words in the intersection of celex and phonix dict.
    """

    non_aligned_words = []

    list_words = sorted(list(set(celex_dict.keys()) & set(raw_phonix_dict.keys())))
    phonix_dict = identify_pieces.process_dict_double_consonant(raw_phonix_dict)

    syllable_dict = defaultdict(set)

    for word in list_words:
        celex_syllables = celex_dict[word].replace('--', '-').split('-')
        #   Above: Replace the special "--" marking between joined compound words with a normal syllable break.
        #   This prevents empty tuples being created that crash the default decoding.
        word_tuple = phonix_dict[word]
        all_syllables = alignment.align_pg_and_syllables(celex_syllables, word_tuple)

        if all_syllables is None:
            non_aligned_words.append((celex_dict[word], word_funcs.mapping_to_str(word_tuple)))
            continue #See message in alignment.py for this function

        for syll in all_syllables:
            this_grapheme = word_funcs.ipa_to_grapheme_str(syll)
            syllable_dict[this_grapheme].add(word_funcs.mapping_to_str(syll))

    return syllable_dict, non_aligned_words

if __name__ == "__main__":

    CELEX_PATH = "/Users/nicolewong/Desktop/urop/celex2/english/eol"
    CELEX_SYLL_PATH = join(CELEX_PATH, 'eol.cd')
    PHONIX_PATH = "/Users/nicolewong/Desktop/urop/data"

    INPUTS_FOLDER = '/Users/nicolewong/Desktop/urop/Data/Inputs'
    DEFAULT_P_PATH = join(INPUTS_FOLDER, 'grapheme_defaults.txt')

    celex_dict = load_words.get_celex_syllables(CELEX_SYLL_PATH)
    phonix_words, phonix_dict = load_words.load_data(PHONIX_PATH) #Already intersected with 5000 popular words.
    default_pg_set = load_words.create_default_pg_tuples(DEFAULT_P_PATH)

    syllable_dict, non_aligned_words = align_celex_syllables(celex_dict, phonix_dict)

    print('Non-nested number of syllables', impact.num_syllables(syllable_dict))

    syllable_dict_post_onsets = onsets_and_rimes.postprocess_to_onsets_and_rimes(syllable_dict)
    syllable_dict_post_strict = strict_decoding.attempt_full_decode(syllable_dict_post_onsets, default_pg_set)

    counts = impact.g2p_to_counts(syllable_dict_post_strict)
    print(counts)
