"""
Simple functions to count the number of chunks.
"""

import numpy as np

def num_syllables(g2p):
    """
    Counts the total number of chunks in g2p
    Inputs:
        g2p, a Dict of a String -> some kind of Collection.
            (it will be a Set of word tuples.)
    Outputs:
        an Integer, the total number of chunks in g2p.
    """
    return sum(len(g_collection) for _, g_collection in g2p.items())

def g2p_to_counts(g2p):

    """
    Returns an array for use in plt histogram
        of certain instabilities.
    Inputs:
        g2p, a Dict of a String -> some kind of Collection.
            (it will be a Set of word tuples.)
    Outputs:
        stability_counts, a Numpy Integer array,
            where each index is the number of collisions,
                and each value is the number of graphemes that exhibit that number of collisions.
    """
    list_counts = [len(g_dict) for g, g_dict in g2p.items()]
    stability_counts = np.bincount(list_counts)

    return stability_counts





