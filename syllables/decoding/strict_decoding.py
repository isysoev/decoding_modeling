from os.path import join, exists
from analysis import impact
from word_tools import word_funcs
from collections import defaultdict

def default_irregular_remainder_forward(word_tuple, default_set):
    """
    Returns the substring that is not decodable via pg pairs.
    """

    for idx, pair in enumerate(word_tuple):
        if pair not in default_set:
            return word_tuple[idx:]

    return ''  # Decodable in its entirety.


def cut_strict_decode(old_g2p_dict, default_set, verbose = False):
    """
    This has been adapted from its original version to perform cuts.
    """
    print("\nAttempting strict decoding with cuts.")

    new_g2p_dict = defaultdict(set)
    cut_parents = {}

    for g, p_set in old_g2p_dict.items():
        for this_word_tuple in p_set:
            remains = default_irregular_remainder_forward(this_word_tuple, default_set)
            remains = default_irregular_remainder_forward(remains[::-1], default_set)[::-1]

            if remains:
                #   Could not fully decode with default pg pairs.
                cut_grapheme = word_funcs.ipa_to_grapheme_str(remains)
                new_g2p_dict[cut_grapheme].add(remains)
                cut_parents[remains] = this_word_tuple #The parent's pronunciation.
                #   TODO: The parent for now -- in the future, accept highest frequency parent.

    chunks_orig = impact.num_syllables(old_g2p_dict)
    chunks_new = impact.num_syllables(new_g2p_dict)

    if verbose:
        print(f'\nPrevious number of chunks: {chunks_orig}')
        print(f'Current number of chunks: {chunks_new}')
        print(f'\tDifference: {chunks_orig - chunks_new}')

    return new_g2p_dict, cut_parents

