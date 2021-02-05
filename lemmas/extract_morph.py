# Python substitute for stripcls.awk from CELEX
#   Tentative methodology to split up the morphemes.

import string
import ast

from itertools import chain
all_letters = set(list(string.ascii_lowercase))

def has_letter(this_str):
    return len((set(list(this_str)) & all_letters)) > 0

def strip_class_labels(word):

    #1/19: https://www.kite.com/python/answers/how-to-print-a-backslash-in-python#:~:text=Use%20a%20raw%20string%20to,not%20as%20an%20escape%20character.
    features = word.split(r"\a"[0])
    discarded_words = []
    this_word = features[-4] #Split on backslashes. Isolate the deepest nested representation of the word.

    forward_split = filter(has_letter, this_word.split("("))

    #1/19: https://stackoverflow.com/questions/11860476/how-to-unnest-a-nested-list
    final_morph_split = list(chain.from_iterable(filter(lambda piece : has_letter(piece) and piece[0] != '[',
                                                  elem.split(')')) for elem in forward_split))
    # Above AND statement is to prevent pieces like "[N|xx.]", like in "metamorphosis", from being included.

    # 2/4 : For now, since no complex words are being considered (roots and affixes considered independently)
    #   Multiple breakdowns of a word, such as in "aesthetically", are all being included.

    if final_morph_split == [] and not this_word:
        print(f'Discarding the word {features[1]} due to empty index -4 field.')
        print(f'\t{features}')
        discarded_words.append(features)

    return final_morph_split


if __name__ == "__main__":
    CELEX_EML_PATH = '/Users/nicolewong/Desktop/urop/celex2/english/eml/eml.cd'

    with open(CELEX_EML_PATH, 'r') as f:
        # 1/19: https://stackoverflow.com/questions/11860476/how-to-unnest-a-nested-list
        this_input = f.readlines()
        all_lemmas = set(chain.from_iterable(map(strip_class_labels, this_input)))
        all_lemmas = list(all_lemmas)

    print(all_lemmas)


