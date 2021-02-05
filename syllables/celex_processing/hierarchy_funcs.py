
# Per word function restructuring for hierarchy.
# Refactor this maybe later so that all hierarchy funcs are in the same file,
#   then move away from the dictionary-oriented processing.

import load_words
from word_tools import identify_pieces, word_funcs
from decoding import strict_decoding


def process_cut_default_decode(word_tuple, default_set):

    remains = strict_decoding.default_irregular_remainder_forward(word_tuple, default_set)
    remains = strict_decoding.default_irregular_remainder_forward(remains[::-1], default_set)[::-1]

    if remains:
        #   Could not fully decode with default pg pairs.
        cut_grapheme = word_funcs.ipa_to_grapheme_str(remains)

    return cut_grapheme, remains
    # The grapheme and its pg pair.


def process_double_consonants(word_tuple):
    """
    Inputs:
        word_tuple, the tuple representation of the pronunciation
    Outputs:
        a copy of word_tuple with double consonants split into duplicate single consonants.
    """

    replace_idxs = identify_pieces.find_double_consonant(word_tuple)
    return word_tuple[:] if replace_idxs is None else identify_pieces.process_double_consonants(word_tuple, replace_idxs)

def process_extended_onsets_and_rimes(word_tuple):
    """
    Inputs:
        pg_str, the str representation of the word pronunciation.
        If possible later: word_tuple, the tuple representation of the pronunciation
    Outputs:
        if no onsets or rimes, None.
        else, a Tuple of str,
            the tuple representation of the onset,
            and another of the rime.
    """

    #word_tuple = word_funcs.get_mapping(pg_str) # Try not to use this later, if possible.
    onset_result = identify_pieces.find_c_any_v_c_any(word_tuple)
    return word_tuple[:] if onset_result is None else onset_result






