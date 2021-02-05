from os.path import join

import imports
imports.import_files()

import load_words
from word_tools import alignment, identify_pieces, word_funcs

from analysis import impact
from decoding import strict_decoding, onsets_and_rimes
import string

#CONSONANT_LETTERS = set(elem for elem in string.ASCII_lowercase) + {'a', 'e', 'i', 'o', 'u'}



def print_post_syllable_dict(this_dict):
    """
    Just for nice printing of dictionary of g->p type, no counts.
    """

    for g, g_collect in this_dict.items():
        print(f'Grapheme: {g}, Number of phonemes: {len(g_collect)}')
        for p in g_collect:
            print(f'\tPhoneme: {p}')

if __name__ == "__main__":

    # Note that function below is for experiment convenience and specifies a file organization.
    celex_dict, phonix_dict, default_pg_set = load_words.load_my_celex_phonix_data()

    print('Adding [z]>s to the default set as an experiment!')
    default_pg_set.add((('z',), 's'))

    syllable_dict, non_aligned_words, _ = alignment.align_celex_syllables(celex_dict, phonix_dict)

    print('Non-nested number of syllables', impact.num_syllables(syllable_dict))

    syllable_dict_post_onsets, _ = onsets_and_rimes.postprocess_to_extended_onsets_and_rimes(syllable_dict, verbose = True)
    syllable_dict_post_strict, _ = strict_decoding.cut_strict_decode(syllable_dict_post_onsets, default_pg_set, verbose = True)

    counts = impact.g2p_to_counts(syllable_dict_post_strict)

    print('Note: Had added [z]>s to the default set as an experiment!')
    print(counts)

    #print_post_syllable_dict(syllable_dict_post_strict)
