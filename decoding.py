import os
import pandas as pd

import math
import numpy as np

from collections import defaultdict

#My own debugging import
import decoding_test

####### GENERATE CANDIDATES #######

class CandChunkInfo():
    """
    Key: The chunk (grapheme),
        with many pronunications associated with each.
    Stores pronunication -> score information
        for each chunk.
    """
    
    def __init__(self, num_examples):
        self.data = {}
        self.seen = set()
        self.num_examples = num_examples
        #Above:
        #   Keys (IPA pronunication, String)
        #   Values: Dict, with the following key-values:
        #       'score': for that pronunication
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
        Checks whether this pronunication seen
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
        #From each pronunication.
        
        #Establish parallel indexing.
        poss_ipa = list(self.data.keys())
        poss_scores = [self.data[key]['score'] for key in poss_ipa]
        
        argmax_idx = np.argmax(poss_scores)
        argmax_ipa = poss_ipa[argmax_idx]
        max_score = np.max(poss_scores)
        
        raw_examples = self.data[argmax_ipa]['examples']
        filtered_examples = self.select_max_score_examples(raw_examples)
        
        max_ipa_info = {'P': argmax_ipa, 'score': max_score,
                        'examples': filtered_examples}
        
        self.data = None #Clear memory, as this will no longer be used.
        return max_ipa_info
     
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
                This will be a list version of the pronunication
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
        Returns the Dict: grapheme -> dict {pronunication, score}
            for max-scoring pronunications.
        """
        
        final_chunks = {}
        for this_word in self.chunks:
            this_word_info = self.chunks[this_word]
            final_chunks[this_word] = this_word_info.give_argmax_score()
    
        return final_chunks
    
def _update_word_candidate_chunks(df_word, cand_chunks):
    """
    Generates the p/g prefixes and suffixes of a word.
    Inputs:
        df_word, an entry in the DataFrame
        cand_chunks, CandChunks object
    Outputs: None, but will mutate the dictionary cand_chunks
        to reflect the p/g frequencies/scores/pairs contributed
            by the word.
    """
    #Verified: prefix, suffix generation.
    
    info = df_word['P'].split('|') #See assumption in check_if_all_nan.
    #   Above splits into the p/g pairs.
    
    #Take prefixes and update.
    for end_idx in range(1, len(info)):
        
        #Note that this stops one end idx short of the full word
        #   But that full word is covered in the suffix
        prefix_list = info[:end_idx]
        cand_chunks.add(prefix_list, df_word)
    
    for start_idx in range(len(info)):
            
        suffix_list = info[start_idx:]
        cand_chunks.add(suffix_list, df_word)

def candidate_chunks(data_df):
    """
    Generates candidate chunks from information
        in the popular_words.csv as a DataFrame.
    Importantly, returns the dictionary of final word-pronunication
        selections to maximize score.
        
    Inputs:
        data_df, a DataFrame with the words to be processed.
    Outputs:
        final_chunks, a nested Dictionary:
            Keys: the chunk grapheme (String)
            Values: a Dict,
                Keys:
                    'P' -> a String IPA pronunication
                    'score' -> a number, the score of the pronunication
                    'examples' -> a Dict,
                        Keys: a word with this chunk, a String
                        Values: the score of that word, a number 
    """
    
    cand_chunks = CandChunks()
    for i in range(len(data_df)):
        _update_word_candidate_chunks(data_df.iloc[i], cand_chunks)
    
    final_chunks = cand_chunks.give_argmax_pronunications()
    return final_chunks


####### END GENERATE CANDIDATES #######


####### DECODING AND CHUNK SELECTION #######


def _find_prefix_chunk(start_idx, cand_chunk, curr_chunk_set, curr_chunk_dict):
    """
    Inputs:
        start_idx, the start index (inclusive) of the substring
            to decode here.
        cand_chunk, String, the entire grapheme being decoded.
    Returns the length and pronunication of the prefix.
    """
    
    #Find the largest prefixes first.
    #   Starting from non-assigned portions of the grapheme.
        
    #Run on single-letter case (due to start_idx+1 to avoid empty string checks)
    if len(cand_chunk) == 1:
        if cand_chunk in curr_chunk_set:
            return (1, curr_chunk_dict[cand_chunk]['P'])
    
    #Run on multiple letter case
    for end_idx in range(len(cand_chunk), start_idx, -1):
        prefix = cand_chunk[start_idx:end_idx]
            
        if prefix in curr_chunk_set:
            return (end_idx, curr_chunk_dict[prefix]['P'])
    
    
    
def is_regular(cand_graph, cand_ipa, true_chunk_set, true_chunk_dict):
    """
    Inputs: cand_graph, the grapheme to be considered (String)
            cand_ipa, the pronunication of above.
            true_chunk_set, the Set of currently chosen sight chunks
            true_chunk_dict, the dictionary of the current
                list of sight chunks.
    Outputs: a Boolean, whether the sight chunk is
        explainable by current chunks.
    """
    
    #While word not completely decoded
    decoded_ipa_list = []
    curr_start_idx = 0 #Where to start decoding at.
    
    while curr_start_idx != len(cand_graph):
            
        this_ipa = ""
        result = _find_prefix_chunk(curr_start_idx, \
                                    cand_graph, true_chunk_set,\
                                        true_chunk_dict)
            
        if result is None:
            return False #Contains no prefix that can be found in the set
            #   Therefore can't be decoded.
        
        curr_start_idx, this_ipa = result
        decoded_ipa_list.append(this_ipa)
    
    decoded_ipa = ''.join(decoded_ipa_list)
    
    return decoded_ipa == cand_ipa
    
def find_sight_chunks(cand_chunks):
    """
    Inputs:
        cand_chunks, the Dictionary output
            of give_argmax_pronunications
    Outputs:    
        sight_chunks Dict:
            Key: grapheme sight chunk
            Value: a Dict
                'examples': List of [words with this sight chunk]
                'score': Given by the candidate chunk info.
    """
    true_chunks_dict = {}
    true_chunks_set = set()
    
    #Sort the candidate chunks by size.
    order_cand_chunks = list(cand_chunks.keys())
    #Below sorting from 10/9: https://developers.google.com/edu/python/sorting
    order_cand_chunks.sort(key=len)

    #Run candidate chunks through the is_regular function.
    for this_chunk_graph in order_cand_chunks:
        
        this_chunk = cand_chunks[this_chunk_graph]
        
        this_ipa = this_chunk['P']
        this_score = this_chunk['score']
        
        if not is_regular(this_chunk_graph, this_ipa,\
                   true_chunks_set, true_chunks_dict):
            
            true_chunks_set.add(this_chunk_graph)
            true_chunks_dict[this_chunk_graph] = {
                'P': this_ipa,
                'score': this_score,
                'examples': this_chunk['examples']
                }
            
    return true_chunks_dict #Convert ordering later.

####### END DECODING AND CHUNK SELECTION #######


def _format_examples(this_chunk_dict):
    
    """
    Format the exampels into one String,
       with words with high scores appearing first.
    Inputs:
        an element (nested Dict) of the output of find_sight_chunks,
            representing a single chunk. 
    Output:
        a String, such that value of 'example' is converted to String
            where different word pairs are joined by |
                word and its score is separated by >,
                    where score follows the word.
    """
    
    orig_example_dict = this_chunk_dict['examples']
    #10/11: https://docs.python.org/3/howto/sorting.html
    order_words = sorted(list(orig_example_dict.keys()), reverse = True)
    
    new_example_list = []
    for this_word in order_words:
        this_word_score = orig_example_dict[this_word]
        this_example_str = '{}>{}'.format(this_word, this_word_score)
        new_example_list.append(this_example_str)
    
    new_example_str = '|'.join(new_example_list)
    return new_example_str

####### CSV WRITING AND SAVING #######
    
def create_chunks_df(final_chunks_dict, save_path = ''):
    """
    Converts the output of find_sight_chunks, a nested Dict,
        to the dataframe.
    Inputs: 
        final_chunks_dict, the nested Dict output of sight_chunks
        save_path, a String path to save the resultant DataFrame at
            (default signifies that no save is desired).
    Outputs:
        final_chunks_df, the DataFrame version of the input Dict
            also written to save_path (if save_path specified)
        wrote_success, if DataFrame was successfully written.
    """
    
    #10/11: DataFrame strategy:
    #   https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.from_dict.html
    #10/11: Advice on speed:
    #   https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.append.html
    
    list_keys = ['G', 'P', 'score', 'examples']
    list_cols = { key: [] for key in list_keys}
    
    def _update_list_one_chunk(grapheme, this_chunk_dict):
        """
        Updates the appropriate list with the information of Dict.
        Inputs:
            grapheme, String,
                the key value corresponding to this_chunk_dict
            this_chunk_dict, an element (Dict) of the output
                of the find_sight_chunks function.
        Outputs:
            None, but will append the information from the Dict
                to appropriate list.
        """
        this_chunk_dict['G'] = grapheme
        this_chunk_dict['examples'] = _format_examples(this_chunk_dict)
        
        for key in list_keys:
            elem_dict_val = this_chunk_dict[key]
            list_cols[key].append(elem_dict_val)
        
    for this_grapheme, this_val in final_chunks_dict.items(): 
        _update_list_one_chunk(this_grapheme, this_val)
        
    #Write the lists. 
    final_chunk_df = pd.DataFrame.from_dict(list_cols)
    #10/11: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.sort_values.html
    final_chunk_df = final_chunk_df.sort_values('score', ascending = False)
    
    wrote_success = False

    if save_path:
        #10/11: https://stackoverflow.com/questions/5137497/find-current-directory-and-files-directory
        this_dir = os.path.dirname(save_path)
        if os.path.exists(this_dir):
            final_chunk_df.to_csv(save_path)
            wrote_success = True
    if not wrote_success:
        print('The path {} did not exist.'.format(save_path))
        print('The function will return the DataFrame '+\
                  'and save to current directory.') 
        
    return final_chunk_df, wrote_success

####### END CSV WRITING AND SAVING #######

####### ASSUMPTION CHECK #######

def check_if_all_nan(data_df):  
    """
    Checks to ensure that P1 is really full of all NaNs.
    Returns bool, with answer to above.
    """
    
    #Because I discard the P1 for the first 5000 common words
    #   as it is all nan for these words.
    
    give = []
    for i in range(len(data_df)):
        word = data_df['P1'].iloc[i]
        if not isinstance(word, str) and math.isnan(word):
            #10/4: https://stackoverflow.com/questions/944700/how-can-i-check-for-nan-values
            continue
        give.append(word)
        
    return give == []


####### END ASSUMPTION CHECK #######

def gen_save_chunks(data_path, save_path):
    """
    The function to call to generate and save the final chunks.
    Inputs:
        data_path, the location of the DataFrame
            (popular_words.csv) with word information
        save_path, where to save the DataFrame
    Outputs:
        chunk_df, the resultant DataFrame with the following columns:
            'G', the grapheme chunk (String),
            'P', the IPA pronunication (String),
            'score', the score for this chunk (number),
            'examples', a list of the highest frequency words
                with this chunk (String),
                    Formatted according to _gen_example_string.
    """
    
    data_df = pd.read_csv(data_path)
        
    assert check_if_all_nan(data_df), \
        'Has some multiple pronunications available. Assumption fails.'
        
    this_cand_chunks = candidate_chunks(data_df)
    
    print('Candidate chunks length', len(this_cand_chunks))
    
    final_chunks = find_sight_chunks(this_cand_chunks)
    chunk_df, successfully_wrote = create_chunks_df(final_chunks, save_path)
    
    print('Final chunks length', len(chunk_df))
    
    #Backup if file not saved correctly first time -- 
    #   just save the output somewhere to avoid rerunning entire program.
    
    if not successfully_wrote and save_path:
        save_path = './popular_words_chunks.csv'
        if os.path.exists(save_path):
            print('Overwriting the file at this location.')
        chunk_df.to_csv(save_path)
        print('DataFrame saved to {}'.format(save_path))
    
    
    return chunk_df

if __name__ == '__generate-main__':
    #I broke the 'main' name above to prevent accidental re-runs
    
    DATA_PATH = '../Data/popular_words.csv'
    RESULT_PATH = '../Data/popular_words_chunks.csv'
    result_chunks_df = gen_save_chunks(DATA_PATH, RESULT_PATH)
    
    print('Chunks generated and saved. Complete.')
    
if __name__ == '__main__':
    pass
    
    
    
    
    
        
    
        
     