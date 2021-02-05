import imports

imports.import_files()

from word_tools import identify_pieces, word_funcs
import segment

def valid_seg(seg):
    """
    Checks whether every proposed syllable in seg is truly a syllable
        (i.e. has at least one "vowel" pg pair).
    """
    result = all(list(map(identify_pieces.has_vowel, seg)))  # All pieces in all segmentations are old_syllables.
    return result

def gen_valid_segmentations(word):
    """
    Word is a word tuple format.
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
    raw_segs is a nested List
        where the first level is the wrapping List
        the second level are Lists of word tuples,
            where each such list is a proposed syllable breakdown.

    Returns:
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
    Input: The output of what was gen_dict_valid_segs.
    Output:
        this_segs, a Dict of the same format as gen_dict_valid_segs,
            but with CVC_any old_syllables broken into onsets and rimes if applicable.
    NOTE: This function does not yet mark the onsets and rimes differently than normal old_syllables.
    """

    new_segs = {}
    for grapheme, raw_segs in raw_segs.items():
        new_segs[grapheme] = broken_segs(raw_segs)

    return new_segs


######################
#### UTILITIES #######
######################

def word_tuple_to_segmentation_input(ipa_str):
    this_ipa_list = []

    for pair in ipa_str:

        if isinstance(pair[0], tuple):
            # For special representations like "k;s"
            new_pair = (';'.join(pair[0]), pair[1])
            join_pair = '>'.join(new_pair)
        else:
            join_pair = '>'.join(pair)

        this_ipa_list.append(join_pair)

    return this_ipa_list

def word_tuple_to_no_seg(word_tuple):
    """
    Giving segmentation string to words that don't have syllable breakdown.
        (these should be monosyllabic)
    """
    return word_funcs.mapping_to_str(word_tuple)