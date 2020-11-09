def _make_filter_test_case():
    
    """
    Returns Lists of Dicts, input and output for filter test case
        which is the example filtering.
    """
    
    chunk_struct_data_vals = [
        
        {'P1':{ #Select examples in an excess of examples
            'score': 1,
            'examples':  {'i1no': 1, 'i1yes1': 100, 'i1yes2': 1000}
            }},
        
        {'P2':{#Select entire set
              'score': 2,
              'examples': {'i2yes1': 2, 'i2yes2': 200}
              }},
        
       {'P3':{#Less examples than max to filter available.
            'score': 3,
            'examples': {'i3yes': -3000} 
            }}

        ]
    
    expected_data_vals = [
        
        {#Select examples in an excess of examples
         'P': 'P1',
         'score': 1,
         'examples':  {'i1yes1': 100, 'i1yes2': 1000}
            },
        
        {#Select entire set
         'P': 'P2',
         'score': 2,
         'examples': {'i2yes1': 2, 'i2yes2': 200},
              },
        
        {#Less examples than max to filter available.
         'P': 'P3',
         'score': 3,
         'examples': {'i3yes': -3000} 
            }

        ]
    
    return chunk_struct_data_vals, expected_data_vals
         
def _make_chunk_case(save_path = ''):
    
    #Words and the pronunications are from the original data.
    debug_dict = {
        'Unnamed': [1, 2, 3, 9, 8, 7, 4],
        'Word': ['the', 'there', 'herself', 'her', 'more', 'under', 'fer'],
        'Frequency': [1, 1.5, 2 , 0.5, 0.3, 1.1, 0.7],
        'P': ['ð>th|i1>e', 'ð>th|ɛ1>e|r>re', \
              'h>h|ɝ0>er|s>s|ɛ1>e|l>l|f>f', 'h>h|ɝ1>er', \
                  'm>m|ɔ1>o|r>re',\
                      'ʌ1>u|n>n|d>d|ɝ0>er',\
                          'f>f|ɝ1>er'],
        'P1': [math.nan]*7 #['hi'] + [math.nan]*6
        #10/4: https://stackoverflow.com/questions/43638759/python-how-to-get-nan
        }
    debug_df = pd.DataFrame.from_dict(debug_dict)
    
    if save_path:
        debug_df.to_csv(save_path)
        
    return debug_df

def _make_manual_chunk_answer():
    """
    Return value (a Dict) for use as manual_case
        in check_final_chunks_test_case.
    """
    
    return {
       
       'th':2.5, 'e':1,
       'the':1.5, 'ere':1.5, 're':1.8,
       'h':2.5,
       'hers':2, 'herse':2, 'hersel':2, 'elf':2, 'self':2, 'lf':2,
       'er':2.3,
       'm':0.3,'mo':0.3,'ore':0.3,
       'u':1.1, 'un':1.1, 'und':1.1, 'nder':1.1, 'der':1.1,
       'f':2.7
   
       }