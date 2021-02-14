from syllables.word_tools import word_funcs

from os.path import join

def load_data(DATA_PATH, select_popular_num=5000):
    """
    Loads word data.
    Inputs:
        DATA_PATH, the parent folder of the phonix and word-freqs data.
        select_popular_num, the top-n popular words to select from the intersection of the two pieces of data
    Outputs:
        word_dict, the the top-n popular words to select from the intersection of phonix and word_freqs
            Dict, str (word) -> Tuple (word's tuple form)
    """

    phonix_dict, wordfreqs = _load_raw_data(DATA_PATH)
    word_dict = select_popular_n(phonix_dict, wordfreqs, select_popular_num)
    return word_dict

########################
### PREP SYLLABLIFY ####
########################

def load_vowel_P(load_path):
    """
    Loads all "vowel pg pairs"
    Inputs:
        load_path, the parent folder of the all_P_vowels.txt file
    Outputs:
        a Set of str, with the phonemes considered to be "vowels"
    """
    vowel_path = join(load_path, 'all_P_vowels.txt')
    with open(vowel_path, 'r') as v:
        all_vowels = [word_funcs.get_phonemes(line.strip()) for line in v.readlines()]

    return set(all_vowels)

###########################
#### HELPER FUNCTIONS #####
###########################

def _load_raw_data(DATA_PATH):

    """
    Gives the phonix and word-freqs data.
    Inputs:
        DATA_PATH, the folder in which phonix and word-freqs data is stored.
    Outputs:
        phonix_dict, a Dict, str (word) -> word tuple version.
        wordfreqs, a Dict, str (word) -> frequency (float)
    """

    # 12/12: Code below taken/adapted from Ivan's code.

    phonix = word_funcs.read_phonix(join(DATA_PATH, 'phonix.txt'))
    phonix_dict = dict(phonix)
    wordfreqs = word_funcs.read_freq_list(join(DATA_PATH, 'word-freqs.txt'))

    return phonix_dict, wordfreqs


def select_popular_n(phonix_dict, wordfreqs, select_popular_num):
    """
    Extract the most popular words from the intersection of word-freqs and phonix dict.
    Inputs:
        phonix_dict, a Dict, str (word) -> word tuple version.
        wordfreqs, a Dict, str (word) -> frequency (float)
        select_popular_num, the top-n popular words to select from the intersection of the two pieces of data
    Outputs:
        popular_words, a List of str of the most popular words, EXCLUDING null and nan
            If I remember correctly, it's because if one tries to save things in a CSV file later, there is strange auto-conversion.
        word_dict, the popular words from the intersection, a Dict, str (word) -> word tuple version.

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