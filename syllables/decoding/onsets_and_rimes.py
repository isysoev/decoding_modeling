
from syllables.analysis import impact
from syllables.word_tools import word_funcs, identify_pieces

from collections import defaultdict

def onsets_and_rimes(old_g2p, verbose = False):

    new_g2p = defaultdict(set)
    onset_rime_counts = defaultdict(int)

    for g, g_dict in old_g2p.items():
        for word_tuple in g_dict:
            if not identify_pieces.is_cvc(word_tuple):
                continue
                # IMPORTANT: Do not store syllables here, because they will be processed at a later in the hierarchy.
                #   If they were stored here, then all non-CVC syllables would be memorized at this stage,
                #       resulting in incorrect answers to the new hierarchy design.
            else:
                onset, rime = word_tuple[:1], word_tuple[1:]
                for piece in [onset, rime]:
                    new_g = word_funcs.ipa_to_grapheme_str(piece)
                    new_g2p[new_g].add(piece)
                    onset_rime_counts[piece] += 1

    orig_g2p_len = impact.num_syllables(old_g2p)
    curr_g2p_len = impact.num_syllables(new_g2p)

    return new_g2p, onset_rime_counts
