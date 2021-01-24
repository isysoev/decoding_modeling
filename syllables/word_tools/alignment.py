## This is for aligning pg pairs and syllables.

import word_funcs

def align_pg_and_syllables(syll_list, word_tuple):

    """

    Note: This should no longer be as tentative as the original version,
        because approx syllabification and the try/catch has been dropped.

    Inputs:
        syll_list, the List of graphemes (str) representing the word
        word_tuple, the word_tuple representation of the word
    Outputs:
        syll_tuple_dict, Dict
            keys: str, the grapheme of the syll
            values: the word tuple form of the syllable
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
