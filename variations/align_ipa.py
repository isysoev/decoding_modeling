
from collections import defaultdict
from chunks import load_words

if __name__ == "__main__":

    """
    Initial code for aligning IPA
        in CMU multiple pronunciation dictionary
            and the phonix file.
    This is INCOMPLETE, but could be useful for starting.
        Please note that because it was incomplete, it is not necessarily to be considered final code!
    """

    CMU_PATH = "/Users/nicolewong/Desktop/urop/Inputs/cmudict-ipa.txt"

    ipa_dict = defaultdict(list)

    with open(CMU_PATH, 'r') as f:
        lines = set(line.strip() for line in f.readlines())
        #   Note that multiple pronunciations have a (number) appended, so above won't exclude them.
        load_words.load_data()

        for line in lines:
            this_raw_word, this_ipa = tuple(line.split('   '))
            possible_numbering_start = this_raw_word.find('(')
            #   For removing the numbered indication of multiple pronunciations.

            this_word = this_raw_word[:possible_numbering_start]\
                if possible_numbering_start else this_raw_word

            # Three spaces should separate every pronunciation from its word
            this_ipa_str = '_'.join(this_ipa)

            ipa_dict[this_word].append(this_ipa)

    print(ipa_dict)

