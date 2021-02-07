
from syllables.word_tools import word_funcs, identify_pieces
from collections import defaultdict

def align_celex_syllables(celex_dict, raw_phonix_dict):
    """
    Merges celex and phonix dict syllable data with alignments.
    Inputs:
        raw_celex_dict, a Dictionary from get_celex_syllables
        phonix_dict, a Dictionary from load_data's second argument
    Outputs:
        a G->P DefaultDict mapping (str -> sorted lists of pronunciations)
            of the words in the intersection of celex and phonix dict.
        a P->int DefaultDict mapping
            of a particular syllable in tuple representation to its frequency (pure word count)
        non_aligned_words, a List of all words that cannot be accurately broken down.
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


def process_alignment_exception(celex_idx, phonix_idx, celex_syll_list, word_tuple):
    """
    Hand-chosen rules for how to process CELEX and phonix words that can't linearly align.
    Inputs:
        celex_idx, phonix_idx, int
            Respectively the first problematic syllable and pg pair's locations.
        celex_syll_list, word_tuple, List and Tuple of str
    Outputs:
        new_celex_syll_list, new_word_tuple,
            postprocessed versions of these for regular syllable alignment.
    """

    except_pg = word_tuple[phonix_idx]
    except_syll = celex_syll_list[celex_idx]

    #   Rule 1: Duplicate ɝ if they are split across syllable boundaries. Keep syllables the same.
    #       examples: arrival, admiration.
    if except_pg[0] == 'ɝ':
        first_grapheme = except_pg[1][:-1] #Allocate the last r to the other syllable.
        second_grapheme = except_pg[1][-1]

        assert second_grapheme == 'r', 'Incorrect assumption about exception handling, Rule 1'
        new_word_tuple = word_tuple[:phonix_idx]\
                         + tuple((('ɝ',), first_grapheme))\
                         + tuple((('ɝ',), second_grapheme))\
                         + (word_tuple[phonix_idx+1] if phonix_idx + 1 < len(word_tuple) else "")

        return celex_syll_list[:], new_word_tuple

    #   Rule 2, manually duplicate "wagon" to have two "g" pg pairs.
    if ''.join(celex_syll_list) == 'waggon': #  CELEX writes wagon as wag-gon.
        return celex_syll_list[:], word_tuple[:3] + word_tuple[2:] #Duplicate the g pg pair.

    #   Rule 3, if the 2nd grapheme is a silent e, then shift the silent e to the next pg pair.
    #       example: beloved
    if 'e' in except_pg[1] and identify_pieces.is_consonant(except_pg[0]):
        next_pg = word_tuple[phonix_idx+1]
        grapheme_remove_e = except_pg[1][:-1]
        grapheme_add_e = "e" + next_pg[1]

        pg_remove_e = (except_pg[0], grapheme_remove_e)
        pg_add_e = (next_pg, grapheme_add_e)

        new_word_tuple = word_tuple[:phonix_idx] + tuple(pg_remove_e) + tuple(pg_add_e) + word_tuple[phonix_idx+1:]
        return celex_syll_list[:], new_word_tuple

    #   Rule 4, If there is a silent i

    #   Rule 4a, if the silent i is [s] > ssi, then split that pg pair into s>s, and s>si.
    #       ex. expression
    if 's>ssi' in word_funcs.mapping_to_str(word_tuple):
        assert except_pg[1] == 'ssi' and except_pg[0] == 's',\
            'Incorrect assumption, the exception pg pair found was not ssi>s'
        new_word_tuple = word_tuple[:phonix_idx] + tuple(('s',), 's') + tuple(('s',), 'ssi') + word_tuple[phonix_idx+1:]
        return celex_syll_list[:], new_word_tuple

    #   Rule 4b, if ʃ>shi is present, then move the "shi" to the next syllable.
    #       ex. fashion
    if 'ʃ>shi' in word_funcs.mapping_to_str(word_tuple):
        assert except_syll.endswith('sh'), 'Incorrect assumption, "sh" does not end the exception syllable.'
        assert next_syll.startswith('ion'), "Incorrect assumption, the syllable after exception doesn't start with ion."
        next_syll = celex_syll_list[celex_idx+1]
        new_syll_list = celex_syll_list[:celex_idx] + ["sh" + next_syll]
        if celex_idx + 2 < len(celex_syll_list):
            new_syll_list += celex_syll_list[celex_idx+2:]

        return new_syll_list, word_tuple[:]

    #   Rule 4c, change the phonix spelling from "granny" to "grannie".
    if ''.join(celex_syll_list) == 'granny':
        assert word_funcs.mapping_to_str(word_tuple).endswith('i>y'), 'Unexpected last pg pair in "granny" exception'
        new_word_tuple = word_tuple[:-1] + tuple(('i',), 'ie')
        return celex_syll_list[:], new_word_tuple

    #   Rule 4d TODO: consider the division of "business"

    #   Rule 5: if "real" is present, then just merge the syllables together.
    #   1/24: The string mapping below is from phonix.
    if 'r>r|i>ea|l>l' in word_funcs.mapping_to_str(word_tuple):
        new_syll_list = '-'.join(celex_syll_list).replace('re-al', 'real').split('-')
        return new_syll_list, word_tuple[:]

    #   Rule 6: If "s>st" is a pg pair, then move the s to the "tle" to make "stle"
    if 's>st' in word_funcs.mapping_to_str(word_tuple):
        this_word = '-'.join(celex_syll_list)
        assert this_word.endswith('tle'), "Rule 6 word does not end with 'tle'"
        new_syll_list = this_word.replace('s-tle', '-stle').split('-')
        return new_syll_list, word_tuple[:]

    #   Rule 7: If "temptation"
    if ''.join(celex_syll_list) == 'temptation':
        new_syll_list = 'tempt-a-tion'.split('-') #Not perfect linguistically, but unsure if it is better to do "tempt-ta-tion"
        return new_syll_list, word_tuple[:]

    #   Rule 8: TODO Break down "anxious", possibly by splitting the k;s pair, but unsure if this is sound.

    assert False, f'Attempted to process an unhandled exception word: {"-".join(celex_syll_list)},' \
                  f' {word_funcs.mapping_to_str(word_tuple)}'

def find_first_alignment_exception(celex_syll_list, word_tuple):

    """
    NOTE: This assumes (too broadly) that only one fix is needed per word! It was also developed in response to manual observations
                on exceptions in the top 5000 words only.
            It is very possible that a word would require two fixes, and therefore would still cause
                a crash in the alignment process.
            This is an initial exploration for intermediate results.
    Inputs:
        celex_syll_list, a List of syllables for this word (str)
        word_tuple, the phonix data for this word
    Outputs:
        celex_phonix_idxs, a Tuple of ints, the location in the List/tuple of the first problematic syllable and pg pair.
        None, if the word is not an alignment exception.
    """
    pg_idx = 0
    for syll_idx, syll in enumerate(celex_syll_list):

        recreated_syll = ''

        #   Try to recreate the syllables with the pg pair graphemes.
        while pg_idx < len(word_tuple):
            recreated_syll += pg_idx[1]
            if recreated_syll >= len(syll) and recreated_syll != syll:
                return syll_idx, pg_idx
                #   The problematic syllable, and the last pg pair added.
                #   These and their immediate successors are of interest.

    return None

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
