from word_tools import word_funcs
from os.path import join

def load_data(DATA_PATH, select_popular_num=5000):
    """
    Filter doubles -> whether to replace all double consonants with single consonants.
    """

    phonix_dict, wordfreqs = _load_raw_data(DATA_PATH)
    word_dict = select_popular_n(phonix_dict, wordfreqs, select_popular_num)
    return word_dict

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