
# 11/8: managing the imports
# https://stackoverflow.com/questions/4383571/importing-files-from-different-folder
# 11/8: For directory help:
# https://superuser.com/questions/717105/how-to-show-full-path-of-a-file-including-the-full-filename-in-mac-osx-terminal/1533160

import sys

code_path = '../../decoding_modeling'
sys.path.insert(1, code_path)

from syllables.word_tools import identify_pieces, word_funcs
from syllables.segmentation import segment

def valid_seg(seg):
    """
    Checks whether every proposed syllable in seg, a collection, is truly a syllable
        (i.e. has at least one "vowel" pg pair).
    Returns boolean to answer above.
    """
    result = all(list(map(identify_pieces.has_vowel, seg)))  # All pieces in all segmentations are old_syllables.
    return result

def gen_valid_segmentations(word):
    """
    Generates valid segmentations for a word.
    Inputs:
        word, in word tuple format.
    Outputs:
        true_segs, a list of all valid segmentations.
    """

    # Special case: If cutoff_len is 0,
    #   return immediately.
    # TODO: Why is this the case?

    if len(word) == 1:
        print(f'For {word}: Shortcircuiting segmentation to prevent unwanted segmenting behavior on single pg pair.')
        return []

    # At least one break must be made to be valid.
    all_segs = segment.possibleSegmentations(word,
                                             cutoff_len=len(word) - 1)

    true_segs = [s for s in all_segs if valid_seg(s)]
    return true_segs

########################
#### ONSET BREAKING ####
########################

def broken_segs(raw_segs):
    """
    Processes onset and rime-like pieces
        (CVC_any, which means that CVC must be the prefix, followed by anything.)
    Inputs:
        raw_segs is a nested List
            where the first level is the wrapping List
            the second level are Lists of word tuples,
                where each such list is a proposed syllable breakdown.
    Outputs:
        new_segs, a List of same format as raw_segs,
            with onsets and rimes included as "old_syllables" in the 2nd dimension.
    """
    new_segs = []
    for seg in raw_segs:
        this_breakdown = []
        for piece in seg:
            broken_piece = [[piece[0]], piece[1:]] if identify_pieces.is_cvc_any(piece) else [piece[:]]
            this_breakdown.extend(broken_piece)
        new_segs.append(this_breakdown)

    return new_segs

def apply_segs_onsets_rimes(raw_segs):
    """
    Applies the onset/rime-like breakdowns to a Dictionary of segmentations.
    Input:
        a Dictionary of grapheme to collection of segmentations
    Output:
        this_segs, a Dict of the same format as input
            but with CVC_any old_syllables broken into onsets and rimes if applicable.
    NOTE: This function does not yet mark the onsets and rimes differently in the str representation
        than normal old_syllables.
    """

    new_segs = {}
    for grapheme, raw_segs in raw_segs.items():
        new_segs[grapheme] = broken_segs(raw_segs)

    return new_segs