import imports
imports.import_files()

from analysis import impact
from word_tools import word_funcs, identify_pieces

from collections import defaultdict

def postprocess_to_onsets_and_rimes(old_g2p):
    """
    Similiar to generation of initial units for EM syllablification.
    However, only identifies VC, CV, and CVC (mono is too common)
        amongst the old_syllables of the resulting words.
    words here is a g2p dict (see stability),
        but is converted to the expected g->p
    """

    # Need to process individually
    #   because dict assumption in prep won't work for collisons.

    # Which CVC are you seeking to discard?
    # Is it safe to discard the entire key?

    g2p = {k : {sub_v for sub_v in v} for k, v in old_g2p.items()}
    orig_g2p_len = impact.num_syllables(g2p)

    # Find CVC words.
    cvc_words = []
    for g, g_dict in g2p.items():
        for pg_str in g_dict:
            word_tuple = word_funcs.get_mapping(pg_str)
            if identify_pieces.is_cvc(word_tuple):
                cvc_words.append((g, word_tuple))

    # Remove CVC words from g2p.
    for g, word_tuple in cvc_words:
        pg_str = word_funcs.mapping_to_str(word_tuple)
        g2p[g].remove(pg_str)
        if not g2p[g]:
            del (g2p[g])
        # This specific mapping will be accounted for via onset/rime.

    # Find onsets and rimes
    onsets_and_rimes = set()
    for word, word_rep in cvc_words:
        onset = (word_rep[0],)
        rime = word_rep[1:]
        for piece in [onset, rime]:
            this_g = word_funcs.ipa_to_grapheme_str(piece)
            pg_str = word_funcs.mapping_to_str(piece)
            onsets_and_rimes.add((this_g, pg_str))

    # Add onsets and rimes to g2p, convert g2p to a non-count dictionary.
    new_g2p = defaultdict(set)
    new_g2p.update(g2p)

    for pair in onsets_and_rimes:
        this_g, this_pg = pair
        new_g2p[this_g].add(this_pg)

    curr_g2p_len = impact.num_syllables(new_g2p)

    print(f'CVC words detected: {len(cvc_words)}')
    print(f'Onsets and rimes detected: {len(onsets_and_rimes)}')
    print(f'Original g2p length: {orig_g2p_len}')
    print(f'Current g2p length: {curr_g2p_len}')
    print(f'\tDifference: {orig_g2p_len - curr_g2p_len}')

    return new_g2p
