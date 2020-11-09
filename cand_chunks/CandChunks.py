from CandChunkInfo import *
from collections import defaultdict

class CandChunks():
    
    def __init__(self, num_examples=5):
        
        def _create_specific_info():
            return CandChunkInfo(num_examples)
        
        self.chunks = defaultdict(_create_specific_info)
        
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
