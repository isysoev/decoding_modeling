####### GENERATE CANDIDATES #######

def _update_word_candidate_chunks(df_word, cand_chunks):
    """
    Generates the p/g prefixes and suffixes of a word.
    Inputs:
        df_word, an entry in the DataFrame
        cand_chunks, a Dict of two CandChunks objects
            keys: 'pre' or 'post'
                    Note: entire words are added to both dictionaries.
    Outputs: None, but will mutate the dictionary cand_chunks
        to reflect the p/g frequencies/scores/pairs contributed
            by the word.
    Do NOT store full words in either Dictionary.
    """
    #Verified: prefix, suffix generation.
    
    info = df_word['P'].split('|') #See assumption in check_if_all_nan.
    #   Above splits into the p/g pairs.
    
    
    #Store the entire list for future processing.
    entire_list = info
    cand_chunks['entire'].add(entire_list, df_word)
    
    #Take prefixes and update.
    for end_idx in range(1, len(info)):
        
        #Note that this stops one end idx short of the full word
        #   But that full word is covered in the suffix
        prefix_list = info[:end_idx]
        cand_chunks['pre'].add(prefix_list, df_word)
    
    for start_idx in range(1, len(info)): #Exclude full words!
            
        suffix_list = info[start_idx:]
        cand_chunks['post'].add(suffix_list, df_word)
            
def candidate_chunks(data_df):
    """
    Generates candidate chunks from information
        in the popular_words.csv as a DataFrame.
    Importantly, returns the dictionary of final word-pronunciation
        selections to maximize score.
        
    Inputs:
        data_df, a DataFrame with the words to be processed.
    Outputs:
        final_chunks, a nested Dictionary with two nested Dictionaries,
            'pre': the Candidate Chunks that are prefixes
            'post': the Candidate Chunks that are postfixes
            Each of these dictionaries contains the following:
                    Keys: the chunk grapheme (String)
                    Values: a Dict,
                        Keys:
                            'P' -> a String IPA pronunciation
                            'score' -> a number, the score of the pronunciation
                            'examples' -> a Dict,
                                Keys: a word with this chunk, a String
                                Values: the score of that word, a number 
    """
    
    cand_chunks = {'pre': CandChunks(), 'post': CandChunks()}
    for i in range(len(data_df)):
        _update_word_candidate_chunks(data_df.iloc[i], cand_chunks)
    
    
    #Selects the top pronunication to use.
    top_ipa_chunks = {cand_type: each.give_argmax_pronunications()\
                    for cand_type, each in cand_chunks.items()}
    
    #Performs length-delayed filtering.
    length_filtered_chunks = {cand_type: filtering._filter_length_chunks(each, (cand_type == 'pre'))\
                              for cand_type, each in top_ipa_chunks.items()}
    
    #Finally, select the top words.
    for cand_type, each in length_filtered_chunks.items():
        for chunk_key, chunk in each.items():
            chunk['examples'] = filtering._format_examples(chunk)
    
    final_chunks = length_filtered_chunks
    return final_chunks

####### END GENERATE CANDIDATES #######