
# 11/8: managing the imports
# https://stackoverflow.com/questions/4383571/importing-files-from-different-folder
# 11/8: For directory help:
# https://superuser.com/questions/717105/how-to-show-full-path-of-a-file-including-the-full-filename-in-mac-osx-terminal/1533160

import sys

code_path = '../../decoding_modeling'
sys.path.insert(1, code_path)

from syllables import prep_syllablify as prep
import os
from os.path import join, exists

from syllables.segmentation import select_segs, process_segs, count_segs

from syllables import load_words

####################
####### MAIN #######
####################

def gen_syllable_divisions(word_order, word_dict,
                           save_path,
                           num_epochs=2,
                           asserts=False):
    """
    Note: Adding onsets and rimes breakdown is going to break the old tests for this function.
    """

    init_seg2freqs = prep.gen_unit_counts(word_dict)
    this_counts = init_seg2freqs

    # Note that below will not support multiple pronunciations.
    valid_segs = {word: process_segs.gen_valid_segmentations(ipa_str)
                  for word, ipa_str in word_dict.items()}

    # For each of these segmentations, need to break the old_syllables into onsets and rimes
    valid_segs = process_segs.apply_segs_onsets_rimes(valid_segs)

    for epoch_idx in range(num_epochs):

        # Step 1: Select the old_syllables seen at this point.
        syllables = select_segs.select_max_probs(word_dict, this_counts, valid_segs)

        # Step 2: Recalculate probabilities of old_syllables.
        this_counts = count_segs.calc_piece_freqs(syllables)

        if asserts:
            print('Attempting to pass asserts.')
            assert asserts[epoch_idx]['old_syllables'] == syllables
            assert asserts[epoch_idx]['this_counts'] == this_counts

    if save_path:
        with open(save_path, 'w') as f:
            f.writelines([f"{word} {syllables[word]}\n" for word in word_order])
        print(f'Written to {save_path}')
    else:
        print('Did not write old_syllables to path.')

    return syllables

if __name__ == '__main__':

    DATA_FOLDER = '../files'

    popular_words_order, word_dict = load_words.load_data(DATA_FOLDER)
    save_split_path = join(DATA_FOLDER, 'old_syllables')

    algorithm_type = 'em'
    save_split_path = join(save_split_path, join(algorithm_type, 'popular_split_em_tentative_refactored.txt'))

    this_dir = os.path.dirname(save_split_path)
    if not exists(this_dir):
        os.makedirs(this_dir)

    should_run = True
    if should_run:
        syllables = gen_syllable_divisions(popular_words_order, word_dict,
                                           save_split_path,
                                           num_epochs=25)