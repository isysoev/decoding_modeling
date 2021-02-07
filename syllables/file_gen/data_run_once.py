# These are used to generate files only once.
# Note that this is the restructured file, NOT the file originally used to generate this data.

import os
from os.path import join, exists
from syllables import load_words


########################
##### GENERATE P #######
########################

def identify_p_types(data_lines):
    all_P = [line.split()[1] for line in data_lines]
    all_pg_pairs = set()

    for this_p in all_P:
        this_pairs = this_p.split('|')
        all_pg_pairs |= set(pair.split('>')[0] for pair in this_pairs)

    all_pg_pairs = sorted(list(all_pg_pairs))

    return all_pg_pairs


def save_all_p_types(load_path, save_path=''):
    """
    Returns a sorted list (by length)
    of all P types pairs in df, a DataFrame.

    Also will save it to save_path, if specified.
    """

    phonix_path = join(load_path, join('full_data', 'phonix.txt'))

    with open(phonix_path, 'r') as f:
        all_pg_pairs = identify_p_types(f.readlines())

    all_pg_pairs = [elem + '\n' for elem in all_pg_pairs]

    with open(save_path, 'w') as s:
        s.writelines(all_pg_pairs)

if __name__ == '__main__':

    DATA_FOLDER = '/Users/nicolewong/Desktop/urop/Data'
    popular_words_order, word_dict = load_words.load_data(DATA_FOLDER)

    syllable_path = join(DATA_FOLDER, 'old_syllables')
    if not exists(syllable_path):
        os.makedirs(syllable_path)

    all_P_path = join(syllable_path, 'all_P_check.txt')