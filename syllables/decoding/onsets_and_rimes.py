import imports

imports.import_files()

from analysis import impact
from word_tools import word_funcs, identify_pieces

from collections import defaultdict

def postprocess_to_extended_onsets_and_rimes(old_g2p, verbose = False):
    """
    Similiar to generation of initial units for EM syllablification.
    However, only identifies CVC
        amongst the old_syllables of the resulting words.
    words here is a g2p dict (see stability),
        but is converted to the expected g->p
    """

    # Need to process individually
    #   because dict assumption in prep won't work for collisions.

    onset_parent_dict = {}
    with_onset_g2p = defaultdict(set)

    for g, g_dict in old_g2p.items():
        for word_tuple in g_dict:
            onset_result = identify_pieces.find_c_any_v_c_any(word_tuple)
            if onset_result is None:
                #   If this P is not broken into onsets and rimes, it is its own parent (the syllable still)
                onset_parent_dict[word_tuple] = word_tuple
                with_onset_g2p[g].add(word_tuple)
            else:
                onset, rime = onset_result
                for piece in [onset, rime]:
                    this_g = word_funcs.ipa_to_grapheme_str(piece)
                    with_onset_g2p[this_g].add(piece)
                    onset_parent_dict[piece] = word_tuple
                    #   TODO: The parent for now -- in the future, accept highest frequency parent.

    orig_g2p_len = impact.num_syllables(old_g2p)
    curr_g2p_len = impact.num_syllables(with_onset_g2p)

    if verbose:
        print(f'Tentative C any V C any analysis (onsets/rimes).')
        print(f'\tOriginal g2p length: {orig_g2p_len}')
        print(f'\tCurrent g2p length: {curr_g2p_len}')
        print(f'\t\tDifference: {orig_g2p_len - curr_g2p_len}')

    return with_onset_g2p, onset_parent_dict
