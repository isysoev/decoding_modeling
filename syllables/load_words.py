from os.path import join

import re
from syllables.word_tools import word_funcs

def load_my_celex_phonix_speechblocks_data():

    """
    Function used for consistent loading across files --
        mostly for my convenience and to prevent me from accidentally loading different files.
    """

    WORDS_PATH = "/Users/nicolewong/Desktop/urop/SpeechBlocks/SpeechBlocks-ImageBank/reference-dictionary.txt"

    CELEX_PATH = "/Users/nicolewong/Desktop/urop/celex2/english/eol"
    CELEX_SYLL_PATH = join(CELEX_PATH, 'eol.cd')
    PHONIX_PATH = "/Users/nicolewong/Desktop/urop/data"

    INPUTS_FOLDER = '/Users/nicolewong/Desktop/urop/Data/Inputs'
    DEFAULT_P_PATH = join(INPUTS_FOLDER, 'grapheme_defaults.txt')

    celex_dict = get_celex_syllables(CELEX_SYLL_PATH)
    phonix_dict = load_speechblocks_phonix(WORDS_PATH, PHONIX_PATH)

    default_pg_set = create_default_pg_tuples(DEFAULT_P_PATH)

    return celex_dict, phonix_dict, default_pg_set

def clean_word_of_numbers(word):
    """
    Removes the _number or .number designations of words.
        Assumes that these two dividers should not appear together.
    """

    period_idx = word.find('.')
    underscore_idx = word.find('_')

    if period_idx != -1 and underscore_idx != -1:
        return word[:min(period_idx, underscore_idx)]
    if period_idx != -1:
        return word[:period_idx]
    if underscore_idx != -1:
        return word[:underscore_idx]

    return word


def process_word_list(word_list):

    all_words = set()
    for line in word_list:
        # 2/5 : https://www.geeksforgeeks.org/python-split-multiple-characters-from-string/
        pieces = re.split(' |,', line.strip())
        this_words = set(map(clean_word_of_numbers, pieces))
        all_words |= this_words

    return all_words

def load_words(WORDS_PATH):
    """
    Parses the contents of reference-dictionary.txt to extract all SpeechBlocks words.
    """

    with open(WORDS_PATH, 'r') as f:
        return process_word_list(f.readlines())

def get_celex_syllables(celex_syllable_path: object) -> object:

    with open(celex_syllable_path) as f:
        syllable_data = {}

        for word_line in f.readlines():
            split_word = word_line.split('\\')
            word, breakdown = split_word[1].strip(), split_word[-1].strip()
            syllable_data[word] = breakdown

        return syllable_data

def load_data_popular_n(DATA_PATH, select_popular_num=5000):
    """
    Filter doubles -> whether to replace all double consonants with single consonants.
    """

    phonix_dict, wordfreqs = _load_raw_data(DATA_PATH)
    word_dict = select_popular_n(phonix_dict, wordfreqs, select_popular_num)
    return word_dict

def load_speechblocks_phonix(WORDS_PATH, DATA_PATH):
    """
    Inputs:
        WORDS_PATH, the filename of the reference-dictionary.txt file of the SpeechBlocks data.
        DATA_PATH, the folder in which phonix data is stored.
    """

    phonix_dict, _ = _load_raw_data(DATA_PATH)
    phonix_words = set(phonix_dict.keys())
    speechblocks_words = load_words(WORDS_PATH)
    return { word : phonix_dict[word] for word in speechblocks_words if word in phonix_words}
    # Above: Prevents cases like alternate spellings of "yogurt" from causing errors.

########################
### PREP SYLLABLIFY ####
########################

def load_vowel_P(load_path):
    vowel_path = join(load_path, 'all_P_vowels.txt')
    with open(vowel_path, 'r') as v:
        all_vowels = [word_funcs.get_phonemes(line.strip()) for line in v.readlines()]

    return set(all_vowels)

###########################
#### HELPER FUNCTIONS #####
###########################


def _load_raw_data(DATA_PATH):
    # 12/12: Code below taken/adapted from Ivan's code.

    phonix = word_funcs.read_phonix(join(DATA_PATH, join('full_data', 'phonix.txt')))
    phonix_dict = dict(phonix)
    wordfreqs = word_funcs.read_freq_list(join(DATA_PATH, join('full_data', 'word-freqs.txt')))

    return phonix_dict, wordfreqs


def select_popular_n(phonix_dict, wordfreqs, select_popular_num):
    """
    Note: the most popular 5000 csv and this calculation don't match.
        I hypothesize that it may have to do with words with prepthe same frequency,
            because whether the reversal was done in the sorted
            versus a reversal after selection
            all impacted the number of words in the symmetric difference
            between the two lists.

        Test cases were written for the selection process instead
            and can be found in test_syllablify.py.
    """

    word_list = sorted(list(set(phonix_dict.keys()) & set(wordfreqs.keys() - {'null', 'nan'})))
    popular_words = sorted(word_list, reverse=True, key=lambda word: wordfreqs[word])[:select_popular_num]

    word_dict = {word: phonix_dict[word] for word in popular_words}

    return popular_words, word_dict

####### LOAD DEFAULT PRONUNCIATIONS ########

def create_default_lookup(default_p_path):
    """
    Returns a Dict of str -> str (grapheme -> pronunciation)
        for default phonemes.
    """
    default_P_dict = {}

    with open(default_p_path, 'r') as f:
        entries = f.readlines()

        for entry in entries:
            entry = entry.split()
            grapheme, phoneme = entry[0], entry[1]
            default_P_dict[grapheme] = phoneme

    return default_P_dict

def create_default_pg_tuples(default_p_path):
    default_pg = create_default_lookup(default_p_path)
    default_pg_set = set((word_funcs.get_pg_pair("{}>{}".format(p, g)),) for g, p in default_pg.items())
    return default_pg_set