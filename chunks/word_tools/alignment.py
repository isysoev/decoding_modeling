
from chunks.word_tools import word_funcs, identify_pieces
from collections import defaultdict

def align_celex_syllables(celex_dict, raw_phonix_dict):
    """
    Merges celex and phonix dict syllable data with alignments.
    IMPORTANT : Ignores non-alignable words, see below.

    Inputs:
        celex_dict, a Dictionary from get_celex_syllables
        raw_phonix_dict, a Dictionary from load_data's second argument
    Outputs:
        a G->P DefaultDict mapping (str -> sorted lists of pronunciations)
            of the words in the intersection of celex and phonix dict.
        a P->int DefaultDict mapping
            of a particular syllable in tuple representation to its frequency (pure word count)
        non_aligned_words, a List of all words that cannot be accurately broken down.
            This is usually because CELEX and phonix data don't always align.
                which happens when a syllable split divides a pg pair,
                    among other discontinuities between CELEX and phonix.

    If you want to build on untested code to handle these exceptions, please see
        process_alignment_exception, find_first_alignment_exception
            functions in other branches.
    """

    non_aligned_words = []

    list_words = sorted(list(set(celex_dict.keys()) & set(raw_phonix_dict.keys())))
    phonix_dict = identify_pieces.process_dict_double_consonant(raw_phonix_dict)

    syllable_dict = defaultdict(set)
    syllable_counts = defaultdict(int)

    for word in list_words:
        celex_syllables = celex_dict[word].replace('--', '-').split('-')
        #   Above: Replace the special "--" marking between joined compound words with a normal syllable break.
        #   This prevents empty tuples being created that crash the default decoding.
        word_tuple = phonix_dict[word]
        all_syllables = align_pg_and_syllables(celex_syllables, word_tuple)

        if all_syllables is None:
            non_aligned_words.append((celex_dict[word], word_funcs.mapping_to_str(word_tuple)))
            continue #See message in alignment.py for this function

        for syll in all_syllables:
            this_grapheme = word_funcs.ipa_to_grapheme_str(syll)
            syllable_dict[this_grapheme].add(syll)
            syllable_counts[syll] += 1

    return syllable_dict, syllable_counts, non_aligned_words

def align_pg_and_syllables(syll_list, word_tuple):
    """
    Note: This should no longer be as tentative as the original version,
        because approx syllabification and the try/catch has been dropped.

    Partitions pg pairs into syllables using CELEX information.
    Inputs:
        syll_list, the List of graphemes (str) representing the word
        word_tuple, the word_tuple representation of the word
    Outputs:
        all_syllable_tuples, List
            the Tuples of str pieces that represent the syllables as stretches of pg pairs
        IMPORTANT: Returns None if the CELEX and phonix data can't be aligned in a simple way.
            See align_celex_syllables docstring for explanation of when this might be the case.
    """

    pg_idx = 0; all_syllable_tuples = []

    for g_syllable in syll_list:
        max_g_to_add = len(g_syllable)  # How far to advance in g reading
        count_this_g_add = 0

        this_syll_tuple = tuple()

        while count_this_g_add < max_g_to_add:
            if (pg_idx >= len(word_tuple)):
                print(f'The index to access pairs will exceed the length of the tuple for '+''.join(syll_list))
                print('\twhich in phonix is '+ word_funcs.mapping_to_str(word_tuple))
                print('This may be because the CELEX breakdown and pg pair breakdown do not match.')
                print('Therefore, returning None.')
                return None

            this_syll_tuple += (word_tuple[pg_idx],)
            count_this_g_add += len(word_tuple[pg_idx][1])

            pg_idx += 1

        all_syllable_tuples.append(this_syll_tuple)

    return all_syllable_tuples
