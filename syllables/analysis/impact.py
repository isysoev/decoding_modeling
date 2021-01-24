import matplotlib.pyplot as plt
import numpy as np

def num_syllables(g2p):
    return sum(len(g_collection) for _, g_collection in g2p.items())

def g2p_to_counts(g2p):

    print(g2p)
    list_counts = [len(g_dict) for g, g_dict in g2p.items()]
    plt.hist(list_counts); plt.show()
    stability_counts = np.bincount(list_counts)

    return stability_counts





