
from chunks.segmentation import segment
from chunks.word_tools import identify_pieces
from collections import defaultdict


def find_all_pg_pairs(word_dict):
    """
    Note that this will filter out the following:
            double consonants,
            consonant_silent_e,
                defined as a chunk with a silent e, that is not a "vowel pg pair"
                    (i.e., is not in the list of vowel pg pairs in the Github)
    Inputs:
        word_dict, a Dict of str -> word Tuples
            It is the phonix dict, but without the "set" wrapping around each IPA.
    Outputs:
        g2p_pg_pairs, a defaultdict of string -> tuple
            where the phoneme maps to the pg pair.
                Notice that the pg_as_chunk has an extra layer of nesting to function as a "chunk" properly.
        pg_counts, the defaultdict of tuple -> int
                counts the frequencies of each pronunciation tuple.
    """

    g2p_pg_pairs = defaultdict(set)
    pg_counts = defaultdict(int)

    for word, ipa in word_dict.items():
        for pg in ipa:
            if identify_pieces.is_double_consonant_pg(pg) or identify_pieces.is_consonant_silent_e(pg):
                continue
            pg_as_chunk = (pg,)
            g2p_pg_pairs[pg[1]].add(pg_as_chunk)

            # Mark the grapheme with its current tuple representation (as a complete chunk, NOT as an individual piece)
            #     The latter is important for compatibility with later filtering.
            pg_counts[pg_as_chunk] += 1

    return g2p_pg_pairs, pg_counts


def find_default_pg_pairs(word_dict, top_n = None):
    """
    Finds the most popular phoneme for each grapheme, for pg pairs.
    Inputs:
        word_dict is the phonix dict, but without the "set" wrapping around each IPA.
        top_n indicates that the top n popular pg pairs should be kept (pure, not word-freq based, frequencies)
            A specific number is used for filtering rare pg pairs.
            None indicates that top n should not be active.
    Outputs:
        popular_pg, a Dict (G->P, or str->word tuple representation),
        which represents the default (popular) chosen chunk.
    """

    all_pgs, pgs_count = find_all_pg_pairs(word_dict)
    popular_pg = filter_popular_chunks(all_pgs, pgs_count, top_n)
    return popular_pg

def filter_popular_chunks(g2p_dict, p2counts, top_n=None):
    """
    Finds the most popular pronunciations for each grapheme, for chunks.
    Inputs:
        g2p_dict, a str->Set{word tuple representation} defaultdict of grapheme -> many phonemes.
        p2counts, a Tuple->int defaultdict of phoneme -> pure word frequencies.
        top_n, if specified, indicates that the top_n popular chunks should be kept (used in default pg pair finding)
    Returns a Dict (G->P, or str->word tuple representation),
        which represents the default (popular) chosen chunk.
    """

    g2popular_chunks = {}
    g2popular_counts = {}
    for g, g_collect in g2p_dict.items():
        # 2/5: https://stackoverflow.com/questions/5098580/implementing-argmax-in-python
        # 2/7: https://stackoverflow.com/questions/54300715/python-3-list-sorting-with-a-tie-breaker
        # 2/7: After running the main algorithm several times, it seems that this solves the non-deterministic behavior.
        max_P = max(g_collect, key= lambda P: (p2counts[P], P))
        #    Tiebreaking: Note that for consistency with below, this is reverse alphabetical order!
        #    This is just for deterministic behavior of tie-breaking.
        g2popular_chunks[g] = max_P
        g2popular_counts[g] = p2counts[max_P]

    if not (top_n is None):
        sorted_popular_chunks = sorted(g2popular_chunks,
                                       # 2/7: https://stackoverflow.com/questions/54300715/python-3-list-sorting-with-a-tie-breaker
                                       key = lambda P : (g2popular_counts[P], P), # Sort on counts, the alphabetical order.
                                       #    Note that for consistency with below, this is reverse alphabetical order!
                                       #    This is just for deterministic behavior of tie-breaking.
                                       reverse = True)
        selected_popular_chunks = sorted_popular_chunks[:min(len(g2popular_chunks), top_n)]
        g2popular_chunks = { g : g2popular_chunks[g] for g in selected_popular_chunks}

    return g2popular_chunks


def find_irregular_chunks(to_decode_dict, all_chunk_set):
    """
    Finds non-decodable chunk.
    A non-decodable chunk is any chunk that can't be composed of pre-existing chunks.
    Inputs:
        to_decode_dict, grapheme (str) -> Set of word tuples
            all_chunk_set, a Set of word tuple-formatted chunks of the pre-existing chunks.
    Outputs:
        A Dict, of the form
            grapheme (str) -> Set of word tuples
             of the non-decodable chunks.
    """

    def _can_decode_segmentation(segs_tuple_list):
        return all(tuple(seg) in all_chunk_set for seg in segs_tuple_list)

    def _can_decode_word_P(word_tuple):
        # Segment the word tuple then use set comparison to see if it's decodable.

        all_poss_segs = segment.possibleSegmentations(word_tuple, len(word_tuple))
        return any(_can_decode_segmentation(seg_select) for seg_select in all_poss_segs)

    new_undecodable_dict = defaultdict(set)
    cannot_decode_word_P = lambda poss_P : not _can_decode_word_P(poss_P)

    for g, g_collect in to_decode_dict.items():
        result = set(filter(cannot_decode_word_P, g_collect))
        if result:
            new_undecodable_dict[g] |= result

    return new_undecodable_dict

