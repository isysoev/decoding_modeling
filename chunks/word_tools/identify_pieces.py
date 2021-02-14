
from os.path import join
from chunks import load_words

#########################
### LOAD NEEDED DATA ####
#########################

VOWELS = load_words.load_vowel_P('../files')

#########################
### VOWEL/CONSONANT #####
#########################

def process_dict_double_consonant(word_dict):

    """
    For a Dictionary of grapheme -> phonemes,
        redistributes the pg pairs that are double consonants
            so that one consonant goes to the front syllable
                and the other goes to the following syllable.
    Inputs:
        word_dict, the output of load_data (phonix and word-freqs intersection)
            keys = the word (str)
            values = the tuple representation of the pronunciation
    Outputs:
        new_word_dict, a copy of the dictionary with the double consonants processed.
    """

    new_word_dict = {}
    for word, P in word_dict.items():
        replace_idxs = find_double_consonant(P)
        new_word_dict[word] = P[:] if replace_idxs is None else process_double_consonants(P, replace_idxs)

    return new_word_dict


def is_double_consonant_pg(pg):
    """
    Returns for each pg, a pg pair in Tuple form, if it is a double consonant.
    """
    p, g = pg
    if is_consonant(p):  # Defined as "not a vowel"
        return len(g) == 2 and g[0] == g[1]

def is_consonant_silent_e(pg):
    """
    Returns if a pg pair (Tuple form) is a "consonant silent e"
        Defined as a non-vowel pg pair,
            with e as the final letter in the grapheme,
                and of length 2
    """
    p, g = pg
    return is_consonant(p) and len(g) == 2 and g[1] == 'e'


def find_double_consonant(word_rep):
    """
    Finds double consonant index in a word, if there is one.
    Inputs:
        word_P, the tuple-form word representation.
    Outputs:
        the index (int) of the location of the double consonant if there is one
        None if there is no double consonant
    """

    to_process_idx = []
    for idx, pg in enumerate(word_rep):
        p, g = pg
        if is_double_consonant_pg(pg):
            # 1/27: Fixed bug here where it was only finding first instance of a double consonant, rather than all.
            to_process_idx.append(idx)

    return None if not to_process_idx else to_process_idx


def process_double_consonants(word_P, replace_idxs):
    """

    IMPORTANT : Assumes that the subject word has already been found to have a double consonant!

    Redistributes the pg pairs that are double consonants
        so that one consonant goes to the front syllable
            and the other goes to the following syllable.
    Inputs:
        word_P, the tuple-form word representation.
        replace_idxs, [ints], the locations of the double consonant.
    Outputs:
        new_word_P, the tuple-form word representation with the double consonant processed out
            to be two single consonants
    """

    # 1/27: Fixed bug here where it was only finding first instance of a double consonant, rather than all.

    assert replace_idxs is not None, 'Wrongly used process double consonant on a word without it.'

    this_new_P = tuple()
    for this_idx, this_pg in enumerate(word_P):

        if this_idx not in replace_idxs:
            this_new_P += (tuple(this_pg),)
        else: # Need to process consonants
            this_cons = word_P[this_idx][1][0]
            double_consonant_insert = (((f'{this_cons}',), f'{this_cons}'),)
            this_new_P += tuple(double_consonant_insert) + tuple(double_consonant_insert)

    return this_new_P


def is_vowel(unit):
    """
    Returns whether unit, a pg pair, in Tuple form, has a phoneme considered to be a vowel.
        Specified by the "all_P" files in the "data" folder.
    """
    assert isinstance(unit, tuple), \
        'Function expects a single (possibly compound) phoneme unit in tuple form.'

    global VOWELS
    return (unit in VOWELS)

def is_consonant(pg_pair):
    """
    Returns whether unit, a pg pair, in Tuple form, has a phoneme considered to be a consonant.
        Specified by the "all_P" files in the "data" folder.
    """
    return not is_vowel(pg_pair)

def has_vowel(poss_syllable):
    """
    Returns whether poss_syllable has a pg pair considered to be a vowel
        (note that this is not simply {a,e,i,o,u}, but dependent on the phonemes of pg pairs)
        Specified by the "all_P" files in the "data" folder.
    """
    return any(is_vowel(p) for p, _ in poss_syllable)

##############################################
##### Identify special linguistic pieces #####
##############################################

def _find_first_vowel(phonemes):

    """
    Finds the first phoneme from pg pair that is considered a vowel phoneme.
    Inputs:
        phonemes, an ordered collection of phonemes
    Outputs:
        idx, the Integer location of the first vowel phoneme.
        None, if no vowel found.
    """

    for idx, p in enumerate(phonemes):
        if is_vowel(p):
            return idx
    return None #No vowels.

def _find_first_consonant(phonemes):

    """
    Finds the first phoneme from pg pair that is considered a consonant phoneme.
    Inputs:
        phonemes, an ordered collection of phonemes
    Outputs:
        idx, the Integer location of the first consonant phoneme.
        None, if no vowel found.
    """

    for idx, p in enumerate(phonemes):
        if not is_vowel(p):
            return idx
    return None #No consonants


def is_cvc(word_tuple):
    """
    Returns bool, whether a Tuple-form word (word-tuple) is a CVC-style word.
    """
    phonemes = word_tuples_to_phonemes(word_tuple)

    if len(phonemes) != 3:
        return False
    if (is_consonant(phonemes[0])
            and is_vowel(phonemes[1])
            and is_consonant(phonemes[2])):
        return True
    return False


def is_cv(word_tuple):
    """
    Returns bool, whether a Tuple-form word (word-tuple) is a CV-style word.
    """
    phonemes = word_tuples_to_phonemes(word_tuple)

    if len(phonemes) != 2:
        return False
    if (is_consonant(phonemes[0])
            and is_vowel(phonemes[1])):
        return True
    return False


def is_vc(word_tuple):
    """
    Returns bool, whether a Tuple-form word (word-tuple) is a VC-style word.
    """
    phonemes = word_tuples_to_phonemes(word_tuple)

    if len(phonemes) != 2:
        return False
    if (is_vowel(phonemes[0])
            and is_consonant(phonemes[1])):
        return True
    return False

#######################
##### EXTRA FUNCTIONS #
#######################

def word_tuples_to_phonemes(word_tuple):
    """
    Returns a List of the phonemes in a Tuple-form word (word-tuple)
    """
    return [p for p, _ in word_tuple]