import imports
imports.import_files()

import load_words
from word_tools import alignment, identify_pieces, word_funcs

from analysis import impact
from decoding import strict_decoding, onsets_and_rimes

from collections import defaultdict

def stabilize_piece_step(piece_dict, parent_dict, piece_to_parent_dict):

    stable_dict = {}
    remains_dict = defaultdict(set)

    for grapheme, grapheme_collection in piece_dict.items():

        if len(grapheme_collection) == 1:
            stable_dict[grapheme] = list(grapheme_collection)[0]
        else:
            for conflict_P in grapheme_collection:
                parent_rep = piece_to_parent_dict[conflict_P]
                parent_grapheme = word_funcs.ipa_to_grapheme_str(parent_rep)
                remains_dict[word_funcs.ipa_to_grapheme_str(parent_rep)] |= {elem for elem in parent_dict[parent_grapheme]}

    return stable_dict, remains_dict


if __name__ == "__main__":
    celex_dict, phonix_dict, default_pg_set = load_words.load_my_celex_phonix_data()

    print('Adding [z]>s to the default set as an experiment!')
    default_pg_set.add((('z',), 's'))

    syllable_dict, non_aligned_words, syllable_parents = alignment.align_celex_syllables(celex_dict, phonix_dict)

    print('Non-nested number of syllables', impact.num_syllables(syllable_dict))

    syllable_dict_post_onsets, onset_parents = onsets_and_rimes.postprocess_to_extended_onsets_and_rimes(syllable_dict)
    syllable_dict_post_strict, cut_parents = strict_decoding.cut_strict_decode(syllable_dict_post_onsets, default_pg_set)

    counts = impact.g2p_to_counts(syllable_dict_post_strict)

    for grapheme, g_collect in syllable_dict_post_strict.items():
        print(f'Grapheme {grapheme}')
        for p in g_collect:
            print(f'\tPhoneme: {p}')

    print('Note: Had added [z]>s to the default set as an experiment!')

    # #Now, revert the chunks to make them stable.
    # lineage_dicts = [cut_parents, onset_parents, syllable_parents]
    # parent_dicts = [syllable_dict_post_onsets, syllable_dict, phonix_dict]
    # print_type = ['cut to onset', 'onset to syll', 'syll to word']
    #
    # current_remains = syllable_dict_post_strict
    # stable_chunks = {}
    #
    # for current_parent_dict, current_lineage_dict, current_type in zip(parent_dicts, lineage_dicts, print_type):
    #     current_stable, current_remains = stabilize_piece_step(current_remains,
    #                                                            current_parent_dict,
    #                                                            current_lineage_dict)
    #
    #     if current_type != 'syll to word':
    #         for g, P in current_parent_dict.items():
    #             # Add the next layer of the hierarchy for processing.
    #             current_remains[g] |= P
    #
    #     stable_chunks.update(current_stable)
    #     print(f'\tStable chunks from this step: {len(stable_chunks)}')
    #
    # stable_counts = impact.g2p_to_counts(stable_chunks)
    # print('Length of remains should be zero. It is currently:', len(current_remains))
