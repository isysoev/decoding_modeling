# 11/8: managing the imports
# https://stackoverflow.com/questions/4383571/importing-files-from-different-folder
# 11/8: For directory help:
# https://superuser.com/questions/717105/how-to-show-full-path-of-a-file-including-the-full-filename-in-mac-osx-terminal/1533160

import sys

code_path = '../../decoding_modeling'
sys.path.insert(1, code_path)

from collections import defaultdict
from syllables.word_tools import word_funcs
import functools

#####################
##### COUNTS ########

def segmentations_to_counts(segmentations, unit2counts):
    """
    Updates segmentation counts.
    Inputs:
        segmentations, a collection of segmentations,
        unit2counts, a defaultdict counting of the pseudocounts of segmentation pieces in the last iteration
            str -> Integer
    Outputs:
        seg_probs, a defaultdict with the scores of segmentations for this iteration.
    """
    # 12/16: https://stackoverflow.com/questions/30356892/defaultdict-with-default-value-1
    seg_probs = defaultdict(lambda: 0.5)

    for seg in segmentations:
        seg_syllables = ['|'.join(list(map(word_funcs.pg_pair_to_str, syllable))) for syllable in seg]
        this_seg_str = ':'.join(seg_syllables)
        syllable_probs = map(lambda this_syllable: unit2counts[this_syllable], seg_syllables)

        prob_val = functools.reduce(lambda x, y: x * y, syllable_probs)

        seg_probs[this_seg_str] = prob_val

    return seg_probs

def calc_piece_freqs(proposed_seg_dict):
    """
    Inputs:
        proposed_seg_dict, output of select_max_probs,
    Outputs:
        new_counts: defaultdict, updated pseudocounts of old_syllables
            str -> pooled counts of the given grapheme, a pseudocount (float).
    """

    segmentations = proposed_seg_dict.values()

    pooled_counts = defaultdict(int)  # g -> pooled counts
    g_to_pg = defaultdict(set)

    for seg in segmentations:  # Seg is string representations.
        list_syllables = seg.split(':')
        for syll in list_syllables:
            grapheme = ''.join(pair.split('>')[1]
                               for pair in syll.split('|'))
            pooled_counts[grapheme] += 1
            g_to_pg[grapheme].add(syll)

    new_counts = defaultdict(lambda: 0.5)
    for g, g_set in g_to_pg.items():
        for pg in g_set:
            new_counts[pg] += pooled_counts[g]

    return new_counts

