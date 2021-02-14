# 11/8: managing the imports
# https://stackoverflow.com/questions/4383571/importing-files-from-different-folder
# 11/8: For directory help:
# https://superuser.com/questions/717105/how-to-show-full-path-of-a-file-including-the-full-filename-in-mac-osx-terminal/1533160

import sys

code_path = '/Users/nicolewong/Desktop/urop/code/'
sys.path.insert(1, code_path)

from chunks.word_tools import alignment, identify_pieces
from chunks import load_words

from chunks.decoding import onsets_and_rimes, filter_chunks


"""
All of the below functions have the same form.
Inputs:
    The first argument, _dict, will be a g2p-style Dict.
        grapheme (str) -> Set of proposed chunks in tuple format.
    The second argument, _counts, will be a Tuple (chunk pronunciation) -> integer defaultdict.
    The third argument, _set, will be the pre-existing set of Tuple-style chunks.
Outputs:
    _as_set, the default set of Tuple-style chunks that could not be decoded
        and must be memorized.
"""
def get_default_onsets_rimes(onset_rime_dict, onset_rime_counts, default_pg_set):

    """
    Finds the default onsets and rimes to add to list of chunks to memorize.
    Please see the general comment at the top of hierarchy.py
        for the docstring for this function.
    """

    irregular_onset_rimes = filter_chunks.find_irregular_chunks(onset_rime_dict, default_pg_set)
    default_onset_rimes = filter_chunks.filter_popular_chunks(irregular_onset_rimes, onset_rime_counts)

    default_onset_rimes_as_set = set(default_onset_rimes.values())
    return default_onset_rimes_as_set

def get_default_syllables(syllable_dict, syllable_counts, curr_chunks_set):

    """
    Finds the default chunks to add to list of chunks to memorize.
    Please see the general comment at the top of hierarchy.py
        for the docstring for this function.
    """

    irregular_syllables = filter_chunks.find_irregular_chunks(syllable_dict,
                                                              curr_chunks_set)
    default_syllables = filter_chunks.filter_popular_chunks(irregular_syllables, syllable_counts)
    default_syllables_as_set = set(default_syllables.values())

    return default_syllables_as_set

def get_default_words(phonix_dict_formatted, curr_chunk_set):

    """
    Finds the default words to add to list of chunks to memorize.
    Please see the general comment at the top of hierarchy.py
        for the docstring for this function.
    """

    irregular_words = filter_chunks.find_irregular_chunks(phonix_dict_formatted,
                                                          curr_chunk_set)

    irregular_words_as_set = set(list(this_collect)[0] for this_collect in irregular_words.values())

    assert all(len(collect) == 1 for collect in irregular_words.values()), \
        "The word sets internally should be guaranteed to only possess one word."

    return irregular_words_as_set

def find_chunks(celex_dict, raw_phonix_dict):

    """
    Finds the chunks in the intersection of given data from CELEX and phonix.
    Inputs:
        celex_dict, a Dictionary of str (word) -> List of str (each str is a syllable, of the chunks of the word)
        raw_phonix_dict, a Dictionary of str (word) -> the Tuple form of the word's pronunciation
    """
    #   Above: To match the processing of chunks of all double consonants.
    phonix_dict = identify_pieces.process_dict_double_consonant(raw_phonix_dict)

    default_pg_dict = filter_chunks.find_default_pg_pairs(phonix_dict, top_n=47)

    default_pg_set = set(default_pg_dict.values())
    #   47 was the length of the original grapheme defaults text file,
    #       which was probably with respect to word-freq, not pure word counts.

    # Get the pieces themselves

    syllable_dict, syllable_counts, non_aligned_words = alignment.align_celex_syllables(celex_dict, phonix_dict)
    onset_rime_dict, onset_rime_counts = onsets_and_rimes.onsets_and_rimes(syllable_dict)

    #   Filter the pieces, construct the hierarchy

    curr_chunk_set = {elem for elem in default_pg_set}

    default_onset_rimes_as_set = get_default_onsets_rimes(onset_rime_dict, onset_rime_counts, curr_chunk_set)
    curr_chunk_set |= default_onset_rimes_as_set

    default_syllables_as_set = get_default_syllables(syllable_dict, syllable_counts, curr_chunk_set)
    curr_chunk_set |= default_syllables_as_set

    #   Skipping the morpheme stage due to previous discussion of problems with CELEX inconsistency.
    #   Basically, CELEX may not separate all morphemes.

    phonix_dict_formatted = {word: {ipa} for word, ipa in phonix_dict.items()}
    default_words_as_set = get_default_words(phonix_dict_formatted, curr_chunk_set)

    curr_chunk_set |= default_words_as_set

    return curr_chunk_set

if __name__ == "__main__":

    celex_dict, raw_phonix_dict = load_words.load_my_celex_phonix_speechblocks_data()
    default_chunks = find_chunks(celex_dict, raw_phonix_dict)

    print(f'Default chunk number: {len(default_chunks)}')
