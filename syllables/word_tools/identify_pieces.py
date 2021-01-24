
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
        replace_idx = find_double_consonant(P)
        new_word_dict[word] = P[:] if replace_idx is None else process_double_consonant(P, replace_idx)

    return new_word_dict

def find_double_consonant(word_rep):
    """
    Inputs:
        word_P, the tuple-form word representation.
    Outputs:
        the index (int) of the location of the double consonant if there is one
        None if there is no double consonant
    """
    for idx, pg in enumerate(word_rep):
        p, g = pg
        if is_consonant(p): #Defined as "not a vowel"
            if len(g) == 2 and g[0] == g[1]:
                return idx

    return None


def process_double_consonant(word_P, double_cons_idx):
    """
    Inputs:
        word_P, the tuple-form word representation.
        double_cons_idx, int, the location of the double consonant.
    Outputs:
        new_word_P, the tuple-form word representation with the double consonant processed out
            to be two single consonants
    """

    assert double_cons_idx is not None, 'Wrongly used process double consonant on a word without it.'

    this_cons = word_P[double_cons_idx][1][0]
    double_consonant_insert = (((f'{this_cons}',), f'{this_cons}'),)

    #Insert the processed double consonant instead of the double consonant itself.
    new_word_P = word_P[:double_cons_idx] + double_consonant_insert[:] + double_consonant_insert[:]
    new_word_P += word_P[double_cons_idx+1:] if (double_cons_idx + 1) < len(word_P) else tuple()

    return new_word_P


def is_vowel(unit):
    assert isinstance(unit, tuple), \
        'Function expects a single (possibly compound) phoneme unit in tuple form.'

    global VOWELS
    return (unit in VOWELS)


def is_consonant(pg_pair):
    return not is_vowel(pg_pair)


def has_vowel(poss_syllable):
    return any(is_vowel(p) for p, _ in poss_syllable)

def _split_ipa_rep(word_ipa_str):

    #TODO -- replace all of these with functions in word_tools.

    g2p = [tuple(pair.split('>'))
               for pair in word_ipa_str.split('|')]
    return g2p

##############################################
##### Identify special linguistic pieces #####
##############################################

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