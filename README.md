# decoding_modeling
Modeling children's decoding skill using probabilistic programming


----

## Notes and concerns

You will have to change the CELEX path and the SpeechBlocks path to run this code.
I did not want to release this data publicly.

*Go to* load_my_celex_phonix_speechblocks_data in load_words.py to do so. Change WORDS_PATH, CELEX_PATH.

Also, the vowel and consonants were derived from the word-freqs/phonix intersection, if I remember correctly, whereas the analysis in this branch is done on CELEX/Speechblocks/phonix. It's unlikely that this will affect results, but this is a discontinuity.

## Terminology and notes on mistakes to avoid

To find the chunks in the text files given,
  use hierarchy.py, in the "chunks/main" folder.

*Common terminology:*
  - *pg pair*:
    A basic phoneme/grapheme pair.
  - *chunk*:
     A single memorized piece of grapheme -> phoneme mapping.
      In this code, a grapheme representation is usually referring to the single string that joins the grapheme parts.
  - *word tuple* or *tuple form* : a Tuple of pg pairs,
        the output of Ivan's function get_mapping,
          which is stored in word_tools -> word_funcs (in my version of the code).
          
       Please note that "word tuples" don't actually always refer to entire words.
       "Word tuple" could be more accurately described as "chunk tuple" -- it just refers to the tuple, rather than string format.
          
  - *g2p*:
    a Dict of String -> Sets of Tuples
                where the String is a grapheme,
                and the Set is a collection of word tuples
                    that represent the possible pronunciations of the grapheme.
  - *default chunk*
    The most frequent grapheme -> phoneme matching for a given chunk.
      Note that this uses pure frequencies of words in this program, NOT real-world frequencies from corpus, etc.
  - *cuts*:
    Refers to removing decodable parts of words
    
*Common mistakes:*
  (Some common errors that I solved while developing this code, may be useful.)
  - When managing single pg pairs, check whether the pg pair is properly nested.
      Often, if a single pg pair is being used as a chunk, it should be nested in another layer of "tuple parentheses"
        for the code to use it correctly.
