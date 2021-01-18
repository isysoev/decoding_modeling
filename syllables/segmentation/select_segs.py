import count_segs
from word_tools import word_funcs

def select_max_probs(word_dict, unit2counts, valid_segs, scoring=False, debugging=False):
    # 12/16: https://stackoverflow.com/questions/30356892/defaultdict-with-default-value-1

    syllablify = {};
    scores = {}

    all_seg_probs = {}

    for idx, (word, word_tuple) in enumerate(word_dict.items()):

        segmentations = valid_segs[word]
        seg_probs = count_segs.segmentations_to_counts(segmentations, unit2counts)

        if debugging:
            all_seg_probs.update(seg_probs)

        if not seg_probs:
            # There are no syllable breaks to insert.
            max_prob_seg = word_funcs.mapping_to_str(word_tuple)
            # If it is a monosyllabic unit.
            if max_prob_seg in unit2counts:
                seg_probs[max_prob_seg] = unit2counts[max_prob_seg]
            # If it is monosyllabic, but not an accepted unit.
            else:
                seg_probs[max_prob_seg] = 0.5
        else:
            # If it is polysyllabic.
            max_prob_seg = max(seg_probs.keys(), key=lambda this_seg: seg_probs[this_seg])

        if scoring:
            max_prob_seg_score = max(seg_probs.values())
            scores[word] = max_prob_seg_score

        syllablify[word] = max_prob_seg

    output = (syllablify,)
    if scoring:
        output += (scores,)
    if debugging:
        output += (all_seg_probs,)

    return syllablify if (not debugging and not scoring) else output



