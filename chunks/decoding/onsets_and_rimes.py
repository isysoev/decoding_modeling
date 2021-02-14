
from chunks.word_tools import word_funcs, identify_pieces
from collections import defaultdict

def onsets_and_rimes(old_g2p):

    """
    Returns information about onsets and rimes found.
    Inputs:
        old_g2p,
            a Dict of String -> Sets of Tuples
                where the String is a grapheme,
                and the Set is a collection of word_tuples
                    that represent the possible pronunciations of the grapheme.
    Outputs:
        new_g2p, of the same form as old_g2p, but defaultdict.
            however, only contains the onset and rimes of CVC words.
        onset_rime_counts, a defaultdict of tuple -> number,
            of each word tuple matched with its pure count frequency
                (i.e. not real world frequencies, but literal occurrences in the original old_g2p)
    """

    new_g2p = defaultdict(set)
    onset_rime_counts = defaultdict(int)

    for g, g_dict in old_g2p.items():
        for word_tuple in g_dict:
            if not identify_pieces.is_cvc(word_tuple):
                continue
                # IMPORTANT: Do not store chunks here, because they will be processed at a later in the hierarchy.
                #   If they were to be stored here, then all non-CVC chunks would be memorized at this stage,
                #       resulting in incorrect answers to the new hierarchy design.
            else:
                onset, rime = word_tuple[:1], word_tuple[1:]
                for piece in [onset, rime]:
                    new_g = word_funcs.ipa_to_grapheme_str(piece)
                    new_g2p[new_g].add(piece)
                    onset_rime_counts[piece] += 1

    return new_g2p, onset_rime_counts
