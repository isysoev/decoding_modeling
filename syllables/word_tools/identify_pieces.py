

# 11/8: managing the imports
# https://stackoverflow.com/questions/4383571/importing-files-from-different-folder
# 11/8: For directory help:
# https://superuser.com/questions/717105/how-to-show-full-path-of-a-file-including-the-full-filename-in-mac-osx-terminal/1533160

import sys

code_path = '../../decoding_modeling'
sys.path.insert(1, code_path)

from os.path import join
from syllables import load_words

#########################
### LOAD NEEDED DATA ####
#########################


#TODO: You will need to change this line to match your file organization.
VOWELS = load_words.load_vowel_P('/Users/nicolewong/Desktop/urop/decoding_modeling/files')

#########################
### VOWEL/CONSONANT #####
#########################

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


def is_cvc_any(word_tuple):
    """
    Allows extended CVC___ breaking, where the CVC prefix can be followed by anything.
    Inputs:
        word_tuple, to be broken (word in word tuple form)
    Outputs:
        boolean, if the word is of CVC_any form.
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


def is_mono(word_tuple):
    """
    Returns bool, whether a word (the input word_tuple, in tuple form)
        has precisely one vowel-type pg pair.
    """

    count_vowels = 0

    for p in word_tuples_to_phonemes(word_tuple):
        if is_vowel(p):
            count_vowels += 1

    return count_vowels == 1

#######################
##### DIRECT FINDS ####
#######################


def word_tuples_to_phonemes(word_tuple):

    """
    Returns a List of the phonemes in a Tuple-form word (word-tuple)
    """

    return [p for p, _ in word_tuple]

def find_type(words, filter_func):

    """
    Finds words of a class of interest (e.g. CVC_any, CVC, etc.)
    Input:
        words, a Dict str -> Tuple of word -> tuple form
        filter_func, the function that corresponds to class of interest
    """

    type_words = {word: value
                  for word, value in words.items()
                  if filter_func(value)}
    return type_words


def find_cvc_any(words):
    """
    Finds CVC_any words,
         words with a CVC prefix followed by anything.
    Input:
        words, a Dict str -> Tuple of word -> tuple form
    Output:
        boolean, if word is of this class
    """
    return find_type(words, is_cvc_any)


def find_cvc(words):

    """
    Finds CVC words
    Input:
        words, a Dict str -> Tuple of word -> tuple form
    Output:
        boolean, if word is of this class
    """

    return find_type(words, is_cvc)


def find_vc(words):

    """
    Finds VC words
    Input:
        words, a Dict str -> Tuple of word -> tuple form
    Output:
        boolean, if word is of this class
    """

    return find_type(words, is_vc)


def find_cv(words):

    """
    Finds CV words
    Input:
        words, a Dict str -> Tuple of word -> tuple form
    Output:
        boolean, if word is of this class
    """

    return find_type(words, is_cv)

def find_mono(words):

    """
    Finds monosyllabic words (words with exactly one pg pair that is considered a vowel)
    Input:
        words, a Dict str -> Tuple of word -> tuple form
    Output:
        boolean, if word is of this class
    """

    return find_type(words, is_mono)