from os.path import join, exists
from analysis import impact
from word_tools import word_funcs

def default_irregular_remainder_forward(word_tuple, default_set):
    """
    Returns the substring that is not decodable via pg pairs.
    """

    for idx, pair in enumerate(word_tuple):
        if pair not in default_set:
            return word_tuple[idx:]

    return ''  # Decodable in its entirety.

def attempt_full_decode(old_g2p_dict, default_set):

    """
    This has been adapted from its original version.
    """
    print("Attempting full decoding")

    g2p_dict = {k : {val for val in v} for k, v in old_g2p_dict.items()}

    chunks_orig = impact.num_syllables(g2p_dict)
    count_removed = 0

    keys_to_remove = []

    for g, p_set in g2p_dict.items():
        new_p_set = set()  # With any remnants of the forward decode.
        for p in p_set:
            if not p:
                print(g == '') #
                print(f'p was empty for {g}')
                continue #Due to compound words having '--' marking.
            this_word_tuple = word_funcs.get_mapping(p)
            remains = default_irregular_remainder_forward(this_word_tuple, default_set)
            remains = default_irregular_remainder_forward(remains[::-1], default_set)[::-1]
            # Backwards cutting doesn't affect the number if forward cutting is enabled.

            if remains:
                # Is fully decodable with default pg pairs.
                new_p_set.add(p)

        g2p_dict[g] = new_p_set
        if not new_p_set:
            keys_to_remove.append(g)
        count_removed += (len(p_set) - len(new_p_set))

    for k in keys_to_remove:
        del (g2p_dict[k])

    chunks_new = impact.num_syllables(g2p_dict)
    print()
    print(f'Removed due to full decoding: {count_removed}')
    print(f'Previous number of chunks: {chunks_orig}')
    print(f'Current number of chunks: {chunks_new}')
    print(f'\tDifference: {chunks_orig - chunks_new}')

    # See if you can collapse the remainders,
    #   such that the decoded sections are still taken away.

    return g2p_dict

