
from os.path import exists, join
import load_words

#########################
### LOAD NEEDED DATA ####
#########################

DATA_FOLDER = '/Users/nicolewong/Desktop/urop/Data'
syllable_path = join(DATA_FOLDER, 'syllables')
VOWELS = load_words.load_vowel_P(syllable_path)

#########################
### VOWEL/CONSONANT #####
#########################

def process_dict_double_consonant(word_dict):

    """
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

def find_double_consonant(word_rep):
    """
    Inputs:
        word_P, the tuple-form word representation.
    Outputs:
        the index (int) of the location of the double consonant if there is one
        None if there is no double consonant
    """

    to_process_idx = []
    for idx, pg in enumerate(word_rep):
        p, g = pg
        if is_consonant(p): #Defined as "not a vowel"
            if len(g) == 2 and g[0] == g[1]:
                # 1/27: Fixed bug here where it was only finding first instance of a double consonant, rather than all.
                to_process_idx.append(idx)

    return None if not to_process_idx else to_process_idx


def process_double_consonants(word_P, replace_idxs):
    """
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
    assert isinstance(unit, tuple), \
        'Function expects a single (possibly compound) phoneme unit in tuple form.'

    global VOWELS
    return (unit in VOWELS)


def is_consonant(pg_pair):
    return not is_vowel(pg_pair)


def has_vowel(poss_syllable):
    return any(is_vowel(p) for p, _ in poss_syllable)

##############################################
##### Identify special linguistic pieces #####
##############################################

def _find_first_vowel(phonemes):

    for idx, p in enumerate(phonemes):
        if is_vowel(p):
            return idx
    return None #No vowels.

def find_c_any_v_c_any(word_tuple):

    """
    Allows CVC-style breaking,
        where the "onset" is any string of consonants,
        and the "rime" is the rest of the word,
            where a vowel and at least one consonant must follow the onset immediately.
    """

    if len(word_tuple) < 3:
        return None

    phonemes = word_tuples_to_phonemes(word_tuple)
    first_vowel_idx = _find_first_vowel(phonemes)

    if first_vowel_idx is None or first_vowel_idx == 0: #Don't accept words without an onset.
        return None

    consonant_streak = word_tuple[:first_vowel_idx]
    extended_rime = word_tuple[first_vowel_idx:]

    return consonant_streak, extended_rime

def is_cvc_any(word_tuple):
    """
    Allows extended CVC___ breaking, where the CVC can be followed by anything.
    """

    if len(word_tuple) < 3:
        return False

    phonemes = word_tuples_to_phonemes(word_tuple)

    if (is_consonant(phonemes[0])
            and is_vowel(phonemes[1])
            and is_consonant(phonemes[2])):
        return True
    return False


def is_cvc(word_tuple):
    phonemes = word_tuples_to_phonemes(word_tuple)

    if len(phonemes) != 3:
        return False
    if (is_consonant(phonemes[0])
            and is_vowel(phonemes[1])
            and is_consonant(phonemes[2])):
        return True
    return False


def is_cv(word_tuple):
    phonemes = word_tuples_to_phonemes(word_tuple)

    if len(phonemes) != 2:
        return False
    if (is_consonant(phonemes[0])
            and is_vowel(phonemes[1])):
        return True
    return False


def is_vc(word_tuple):
    phonemes = word_tuples_to_phonemes(word_tuple)

    if len(phonemes) != 2:
        return False
    if (is_vowel(phonemes[0])
            and is_consonant(phonemes[1])):
        return True
    return False


def is_mono(word_tuple):
    count_vowels = 0

    for p in word_tuples_to_phonemes(word_tuple):
        if is_vowel(p):
            count_vowels += 1

    return count_vowels == 1

#######################
##### DIRECT FINDS ####
#######################


def word_tuples_to_phonemes(word_tuple):
    return [p for p, _ in word_tuple]

def find_type(words, filter_func):
    type_words = {word: value
                  for word, value in words.items()
                  if filter_func(value)}
    return type_words


def find_cvc_any(words):
    return find_type(words, is_cvc_any)


def find_cvc(words):
    return find_type(words, is_cvc)


def find_vc(words):
    return find_type(words, is_vc)


def find_cv(words):
    return find_type(words, is_cv)


def find_mono(words):
    return find_type(words, is_mono)