import numpy as np

class CandChunkInfo():
    """
    Key: The chunk (grapheme),
        with many pronunications associated with each.
    Stores pronunciation -> score information
        for each chunk.
    """
    
    def __init__(self, num_examples):
        self.data = {}
        self.seen = set()
        self.num_examples = num_examples
        #Above:
        #   Keys (IPA pronunciation, String)
        #   Values: Dict, with the following key-values:
        #       'score': for that pronunciation
        #       'examples': List of 5 most frequent words
        #           with this chunk: (grapheme, score).
            
    def __str__(self):
        
        if not self.data: #If empty
            return {}
        
        report = ""
        for ipa in self.data:
            this_info = self.data[ipa]
            report += '\n\tFor IPA: {}\n'.format(ipa)
            report += '\t\tScore: {}\n'.format(this_info['score'])
            report += '\t\tExamples: {}\n\n'.format(this_info['examples'])
            
        return report
        
    def add(self, new_ipa, new_freq, new_orig_word):
        """
        Checks whether this pronunciation seen
            and updates state appropriately.
        Inputs:
            new_ipa, String, pronunciation of chunk rep. by CandChunkInfo
            new_freq, the float/double frequency of new_orig_word
            new_orig_word, String, the word containing chunk as pre/suffix
        Outputs: None, mutates the object to update information.
        """
        if new_ipa in self.seen:
            curr_dict = self.data[new_ipa]
            curr_dict['score'] += new_freq
                
            #If this orig word is new, append as new example
            if not new_orig_word in curr_dict['seen_examples']:
                curr_dict['examples'][new_orig_word] = new_freq
            else:
                #Otherwise, update score of old grapheme
                curr_dict['examples'][new_orig_word] += new_freq
                
        else:
            self.data[new_ipa] = {
                'score': new_freq,
                'examples': {new_orig_word: new_freq},
                'seen_examples': set()
                }
        self.seen.add(new_ipa) 
        self.data[new_ipa]['seen_examples'].add(new_orig_word)

        
    def give_argmax_score(self):
        """
        Returns the word internal Dict
            with pronunciation for max score.
        """
        
        #Filters all of the non-top-n examples
        #From each pronunciation.
        
        #Establish parallel indexing.
        poss_ipa = list(self.data.keys())
        poss_scores = [self.data[key]['score'] for key in poss_ipa]
        
        argmax_idx = np.argmax(poss_scores)
        argmax_ipa = poss_ipa[argmax_idx]
        max_score = np.max(poss_scores)
        
        raw_examples = self.data[argmax_ipa]['examples']
        
        max_ipa_info = {'P': argmax_ipa, 'score': max_score,
                        'examples': raw_examples}
        #Above: raw_examples for use with the delayed length filter. 
        #Also, should use the _format_examples function, not the select function.
        
        return max_ipa_info