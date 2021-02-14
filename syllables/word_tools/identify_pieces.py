

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