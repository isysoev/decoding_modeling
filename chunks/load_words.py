from os.path import join

import re
from chunks.word_tools import word_funcs

def load_my_celex_phonix_speechblocks_data():

    """
    Function used for consistent loading across files --
    This uses hardcoded versions of paths,
        to prevent me from accidentally loading different files
            across different programs.

    Inputs: None
    Outputs:
        celex_dict, a Dict of str (words) -> List of str (syllables, str)
        phonix_dict, a Dict of str (words) -> Tuple form of word pronunciation
        IMPORTANT : the phonix_dict only includes words in the intersection of phonix and speechblocks!
    """

    # Data from the DropBox of SpeechBlocks
    WORDS_PATH = "/Users/nicolewong/Desktop/urop/SpeechBlocks/SpeechBlocks-ImageBank/reference-dictionary.txt"

    # Data from CELEX
    CELEX_PATH = "/Users/nicolewong/Desktop/urop/celex2/english/eol"
    CELEX_SYLL_PATH = join(CELEX_PATH, 'eol.cd')
    PHONIX_PATH = "/Users/nicolewong/Desktop/urop/code/chunks/files"

    celex_dict = get_celex_syllables(CELEX_SYLL_PATH)
    phonix_dict = load_speechblocks_phonix(WORDS_PATH, PHONIX_PATH)

    return celex_dict, phonix_dict

def clean_word_of_numbers(word):
    """
    Used for IPA processing with CMU dictionary.
    Removes the _number or .number designations of words.

    Inputs: word, a word from the SpeechBlocks list of words
    Outputs: word, but with all of additional information in speechblocks removed (like the version of the word)
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
    """
    Finds and cleans the words in the SpeechBlocks file (ask Ivan for the text file)
        word_list, the result of readlines on the SpeechBlock file, reference-dictionary.txt
        all_words, a Set of all of the cleaned words in that file.
    """

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
    Input:
        WORDS_PATH, a str, the absolute location of reference-dictionary.txt.
    Outputs:
        a Set of all of the cleaned words in that file.
    """

    with open(WORDS_PATH, 'r') as f:
        return process_word_list(f.readlines())

def get_celex_syllables(celex_syllable_path):

    with open(celex_syllable_path) as f:
        syllable_data = {}

        for word_line in f.readlines():
            split_word = word_line.split('\\')
            word, breakdown = split_word[1].strip(), split_word[-1].strip()
            syllable_data[word] = breakdown

        return syllable_data

def load_speechblocks_phonix(WORDS_PATH, DATA_PATH):
    """
    Gives the phonix information for the intersection of speechblocks and phonix.
    Inputs:
        WORDS_PATH, the filename of the reference-dictionary.txt file of the SpeechBlocks data.
        DATA_PATH, the folder in which phonix data is stored.
    Outputs:
        a Dict, str (word) -> word tuple version.
    """

    phonix_dict = _load_raw_phonix(DATA_PATH)
    phonix_words = set(phonix_dict.keys())
    speechblocks_words = load_words(WORDS_PATH)
    return { word : phonix_dict[word] for word in speechblocks_words if word in phonix_words}
    # Above: Prevents cases like alternate spellings of "yogurt" from causing errors.

###########################
#### HELPER FUNCTIONS #####
###########################

def _load_raw_phonix(DATA_PATH):

    """
    Gives the phonix information for all words in phonix.
    Inputs:
        WORDS_PATH, the filename of the reference-dictionary.txt file of the SpeechBlocks data.
        DATA_PATH, the folder in which phonix data is stored.
    Outputs:
        a Dict, str (word) -> word tuple version.
    """
    # 12/12: Code below taken/adapted from Ivan's code.

    phonix = word_funcs.read_phonix(join(DATA_PATH, 'phonix.txt'))
    phonix_dict = dict(phonix)

    return phonix_dict

####### LOAD PG PAIR INFORMATION ########

def load_vowel_P(load_path):

    """
    Returns the Set of str representing vowel-type phonemes,
        found at load_path, str, the parent folder of all_P_vowels.txt
    """

    vowel_path = join(load_path, 'all_P_vowels.txt')
    with open(vowel_path, 'r') as v:
        all_vowels = [word_funcs.get_phonemes(line.strip()) for line in v.readlines()]

    return set(all_vowels)

def create_default_lookup(default_p_path):
    """
    This will load the set of default pg pairs defined by the pg pair defaults txt file.
    Please note that this file was not created based on SpeechBlocks.
    Inputs:
        default_p_path, str, the filename of the
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

    """
    Load the pg pair defaults
    Inputs:
        default_p_path, the filename of the pg pair defaults txt file.
    Outputs:
        default_pg_set, the Set of str Tuples that represent the default pg pairs.
    """
    default_pg = create_default_lookup(default_p_path)
    default_pg_set = set((word_funcs.get_pg_pair("{}>{}".format(p, g)),) for g, p in default_pg.items())
    return default_pg_set