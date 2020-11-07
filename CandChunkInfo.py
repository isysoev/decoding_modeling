import numpy as np

class CandChunkInfo():
    """
    Key: The chunk (grapheme),
        with many pronunications associated with each.
    Stores pronunciation -> score information
        for each chunk.
    """
    
    prefix_opts = {'pre', 'post', 'full'}
    
    def __init__(self, num_examples):
        
        #print('In give_argmax_score for CandChunkInfo.')
        #print('Please note that example filtering (assumed in main decoding.py)')
        #print('was disabled to allow for experimenting with length filtering.')
        
        self.data = {}
        self.seen = set()
        self.num_examples = num_examples
        self.is_prefix = False
        self.is_postfix = False
        
        #Above:
        #   Keys (IPA pronunciation, String)
        #   Values: Dict, with the following key-values:
        #       'score': for that pronunciation
        #       'examples': List of 5 most frequent words
        #           with this chunk: (grapheme, score).
            
    def set_is_prefix(self):
        """
        Either this or set_is_postfix must be used
            if length-based filtering is being used.
        For entire words, is_prefix and is_postfix is True.
        """
        
        self.is_prefix = True
    
    def set_is_postfix(self):
        """
        See comment on set_is_prefix
        """
        self.is_postfix = True
        
    def get_is_prefix(self):
        return self.is_prefix 
    
    def get_is_postfix(self):
        return self.is_postfix
    
        
    def __str__(self):
        
        if not self.data: #If empty
            return {}
        
        report = "\n\tDescribes: "
        if self.is_prefix:
            report += 'prefix'
            if self.is_postfix:
                report += ', '
        if self.is_postfix:
            report += 'postfix'
            
        for ipa in self.data:
            this_info = self.data[ipa]
            report += '\tFor IPA: {}\n'.format(ipa)
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
            
        
    def select_max_score_examples(self, this_example_dict):
        
        """
        Same as parent, but takes in one Example Dict, the value
            of Dict with IPA key
            and performs actual transformation.
        Does NOT perform mutation yet.
        Returns the updated example Dict.
        """
        
        actual_num_ex = min(self.num_examples, len(this_example_dict))
        ordered_keys = list(this_example_dict.keys())
        ordered_keys.sort(reverse=True)
        
        which_examples = ordered_keys[:actual_num_ex]
        
        #Transfer example and its score to new Dictionary.
        new_dict = {this_word: this_example_dict[this_word] \
                    for this_word in which_examples}
        
        return new_dict

        
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
        #filtered_examples = self.select_max_score_examples(raw_examples)
        
        max_ipa_info = {'P': argmax_ipa, 'score': max_score,
                        'examples': raw_examples,
                        'is_prefix': self.is_prefix, 'is_postfix': self.is_postfix}
                        #'examples': filtered_examples}
        
        return max_ipa_info