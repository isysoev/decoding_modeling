import os
import pandas as pd


def resave_first_num(num_select, data_path, full_path):
    """
    Resaves the num_select most frequent words under the given filename.
    """
    
    words_df = pd.read_csv(data_path)
    #10/4: https://stackoverflow.com/questions/11346283/renaming-columns-in-pandas
    words_df.columns = ['Word', 'Frequency', 'P', 'P1']
    
    #Re-accessed 10/11 (and re-ran this code)
    #   https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.sort_values.html
    new_df = words_df.sort_values('Frequency', ascending = False)
    new_df = new_df[:5000]
    
    new_df.to_csv(full_path)
    print('New csv saved to', full_path)
    
    return new_df
    
    
#10/4: Reminder on syntax:
#   https://stackoverflow.com/questions/419163/what-does-if-name-main-do 
  
if __name__ == '__main__':
    
    DATA_PATH = '../Data/phonix_shift_word_freqs.csv'
    cut_path = '../Data/popular_words_shift.csv'

    num_select= 5000
    resave_first_num(num_select, DATA_PATH, cut_path)
    
    
    