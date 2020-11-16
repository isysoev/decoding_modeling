from CandChunkInfo import *
from collections import defaultdict
import os

from os.path import join


####### LOAD DEFAULT PRONUNCIATIONS ########

def create_default_lookup():
    """
    Returns a Dict of str -> str (grapheme -> pronunciation)
        for default phonemes.
    """
    default_P_dict = {}
    with open(DEFAULT_P_PATH, 'r') as f:
        
        entries = f.readlines()

        for entry in entries:
            entry = entry.split()
            grapheme, phoneme = entry[0], entry[1]
            default_P_dict[grapheme] = phoneme
        
    return default_P_dict

INPUTS_FOLDER = '/Users/nicolewong/Desktop/urop/Data/Inputs'
DEFAULT_P_PATH = join(INPUTS_FOLDER, 'grapheme_defaults.txt')

DEFAULT_P_DICT = create_default_lookup()

class CandChunks():
    
    def __init__(self, num_examples=5, should_init_default = True):
        """
        should_init_default = Should initialize default pronunciations?
        False if CandChunks stores entire words.
        """
        
        def _create_specific_info():
            return CandChunkInfo(num_examples)
        
        self.chunks = defaultdict(_create_specific_info)
        
        #Need to initialize default
        if should_init_default:
            for this_word, this_p in DEFAULT_P_DICT.items():
                self.chunks[this_word].add(this_p, float('inf'), this_word)
                self.chunks[this_word].data[this_p]['examples'] =\
                    {'Not given, default chunk.': float('inf')}
                    #Above: Avoid storing self as an example
            #By the frequency, this will always be the pronunciation used.


    def __len__(self):
        return len(self.chunks)
        
    def create_default_lookup():
        
        return create_default_lookup()
        #The definition outside of the class.
        #Used to make verifications easier to run.

    def __str__(self):
        report = ""
        for key in self.chunks:
            report += 'For {}'.format(key)
            report += str(self.chunks[key]) + '\n'
            
        return report
    
    def clean_ipa(self, this_ipa):
        """
        Removes 0, 1, 2 characters from phoneme transcription.
            0, 1, 2 were the digits that I found in the phonix text
                by find function.
        """
        #10/4: Use of replace from: https://www.journaldev.com/23674/python-remove-character-from-string
        for this_digit in [0, 1, 2]:
            this_ipa = this_ipa.replace(str(this_digit), '')
            
        return this_ipa
    
    def add(self, this_chunk_list, df_word):
        """
        Inputs:
            this_chunk_list, a list of p/g pairs (prefix or suffix)
                This will be a list version of the pronunciation
                    in the dataset, split on |.
            df_word, the DataFrame entry for this chunk_list
        """
        
        this_freq = df_word['Frequency']
        this_orig_word = df_word['Word']
        
        gp_separate = [elem.split('>') for elem in this_chunk_list]

        this_phoneme = ''.join([gp_pair[0]\
                                 for gp_pair in gp_separate])
        this_grapheme = ''.join([gp_pair[1]\
                                for gp_pair in gp_separate])
        
        this_phoneme = self.clean_ipa(this_phoneme)
        

        #Either add or update information.
        self.chunks[this_grapheme].add(this_phoneme,\
                                       this_freq, this_orig_word)
        
    def give_argmax_pronunications(self):
        """
        Returns the Dict: grapheme -> dict {pronunciation, score}
            for max-scoring pronunications.
        """
        
        final_chunks = {}
        for this_word in self.chunks:
            this_word_info = self.chunks[this_word]
            final_chunks[this_word] = this_word_info.give_argmax_score()
    
        return final_chunks
