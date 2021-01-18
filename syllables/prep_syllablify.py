########### Need to try to refactor this code to NOT do pooling!

import imports
imports.import_files()

from word_tools import word_funcs, identify_pieces
from collections import defaultdict

def update_grapheme_to_count(word_rep, g2counts):
    """
    Returns for clarity, but actually mutates cvc_words
    """

    grapheme = ''.join(pair[1] for pair in word_rep)
    # New grapheme
    if grapheme not in g2counts:
        g2counts[grapheme] = {word_rep: 1}
        # Grapheme exists,
    else:
        # New phoneme
        if word_rep not in g2counts[grapheme]:
            g2counts[grapheme][word_rep] = 1
        # Phoneme exists
        else:
            g2counts[grapheme][word_rep] += 1

    return g2counts

def pool_and_distr_counts(g2counts):
    """
    g2counts is a nested Dict:
        G (str) -> dict,
            {word_tuple -> count of this g->p mapping.}
    """

    pooled_counts = {}

    for grapheme, g_dict in g2counts.items():
        this_counts = sum(g_dict.values())  # Over all pronunciations, sum the counts.
        pooled_counts[grapheme] = this_counts

    # Transfer to pseudocounts.
    # 12/16: https://stackoverflow.com/questions/30356892/defaultdict-with-default-value-1
    pseudocounts = defaultdict(lambda: 0.5)
    for grapheme, g_dict in g2counts.items():
        for P in g_dict:  # Mark all P for a G with the pooled counts.
            P_str = word_funcs.mapping_to_str(P)
            pseudocounts[P_str] += pooled_counts[grapheme]

    return pseudocounts


def gen_unit_counts(words):
    """
    Generates pseudocounts for all of the units to use in syllable divisions.
    """

    g2counts = {}

    # Below: types where one occurence of each G -> P entry is guaranteed.
    #   If a word appears twice in two classes,
    #   Namely VC or CV and mono,
    #       then in this loop, it will only count as one word.
    #   This should be the only case of possible overcounting
    #       where the unique countable object is (parent word -> unit) pairs.

    single_types_func = [identify_pieces.find_vc, identify_pieces.find_cv, identify_pieces.find_mono]

    for func in single_types_func:
        subset_words = func(words)
        subset_dict = {
            G: {P: 1}  # Because of the constant 1 replacement,
            #               Should not overcount words.
            for G, P in subset_words.items()
        }
        g2counts.update(subset_dict)

    # Extract onsets and rimes from CVC.
    #   Now, there is no guarantee of non-overlapping or single-occurence G->P.

    cvc_words = identify_pieces.find_cvc(words)

    for word, word_rep in cvc_words.items():
        onset = (word_rep[0],)
        rime = word_rep[1:]
        for piece in [onset, rime]:
            update_grapheme_to_count(piece, g2counts)

    # Now, need to calculate pooled counts for each grapheme.
    pseudocounts = pool_and_distr_counts(g2counts)
    return pseudocounts