# 11/8: managing the imports
# https://stackoverflow.com/questions/4383571/importing-files-from-different-folder
# 11/8: For directory help:
# https://superuser.com/questions/717105/how-to-show-full-path-of-a-file-including-the-full-filename-in-mac-osx-terminal/1533160

import sys

code_path = '/Users/nicolewong/Desktop/urop/code/'
sys.path.insert(1, code_path)

from syllables.word_tools import alignment, word_funcs, identify_pieces
from syllables import load_words

from syllables.analysis import impact
from syllables.decoding import onsets_and_rimes, strict_decoding

def get_default_onsets_rimes(onset_rime_dict, onset_rime_counts, default_pg_set):

    irregular_onset_rimes = strict_decoding.find_irregular_chunks(onset_rime_dict, default_pg_set)
    default_onset_rimes = strict_decoding.filter_popular_chunks(irregular_onset_rimes, onset_rime_counts)

    default_onset_rimes_as_set = set(default_onset_rimes.values())
    return default_onset_rimes_as_set

def get_default_syllables(syllable_dict, syllable_counts, curr_chunks_set):

    irregular_syllables = strict_decoding.find_irregular_chunks(syllable_dict,
                                                                curr_chunks_set)
    default_syllables = strict_decoding.filter_popular_chunks(irregular_syllables, syllable_counts)
    default_syllables_as_set = set(default_syllables.values())

    return default_syllables_as_set

def get_default_words(phonix_dict_formatted, curr_chunk_set):

    irregular_words = strict_decoding.find_irregular_chunks(phonix_dict_formatted,
                                                            curr_chunk_set)

    irregular_words_as_set = set(list(this_collect)[0] for this_collect in irregular_words.values())

    assert all(len(collect) == 1 for collect in irregular_words.values()), \
        "The word sets internally should be guaranteed to only possess one word."

    return irregular_words_as_set

def find_chunks(celex_dict, raw_phonix_dict):

    #   Above: To match the processing of syllables of all double consonants.
    phonix_dict = identify_pieces.process_dict_double_consonant(raw_phonix_dict)

    default_pg_dict = strict_decoding.find_default_pg_pairs(phonix_dict, top_n=47)

    default_pg_set = set(default_pg_dict.values())
    #   47 was the length of the original grapheme defaults text file,
    #       which was probably with respect to word-freq, not pure word counts.

    # Get the pieces themselves

    syllable_dict, syllable_counts, non_aligned_words = alignment.align_celex_syllables(celex_dict, phonix_dict)
    onset_rime_dict, onset_rime_counts = onsets_and_rimes.onsets_and_rimes(syllable_dict)

    ## Filter the pieces, construct the hierarchy

    curr_chunk_set = {elem for elem in default_pg_set}

    default_onset_rimes_as_set = get_default_onsets_rimes(onset_rime_dict, onset_rime_counts, curr_chunk_set)
    curr_chunk_set |= default_onset_rimes_as_set

    default_syllables_as_set = get_default_syllables(syllable_dict, syllable_counts, curr_chunk_set)
    curr_chunk_set |= default_syllables_as_set

    #   Skipping the morpheme stage due to previous discussion of problems with CELEX inconsistency.

    phonix_dict_formatted = {word: {ipa} for word, ipa in phonix_dict.items()}
    default_words_as_set = get_default_words(phonix_dict_formatted, curr_chunk_set)

    curr_chunk_set |= default_words_as_set

    return curr_chunk_set

if __name__ == "__main__":

    # TODO : Potentially make previous set of default pg pairs unavailable in the code (or at least not returned in this call)
    #  for consistency.
    celex_dict, raw_phonix_dict, _ = load_words.load_my_celex_phonix_speechblocks_data()

    ## TODO: Maybe institute some kind of sorted preference/secondary sorting for tie-breaking popularity?
    ## The non-deterministic behavior is observable after a few runs of the algorithm,
    # and usually results in a small difference in the number of final chunks.

    default_chunks = find_chunks(celex_dict, raw_phonix_dict)

    print(f'default chunk number {len(default_chunks)}')

    terminate_idx = 0
    for c in default_chunks:
        terminate_idx += 1
        if terminate_idx > 5 : break
        print(f'\t{word_funcs.mapping_to_str(c)}')
