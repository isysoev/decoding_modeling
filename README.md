# decoding_modeling
Modeling children's decoding skill using probabilistic programming

Discontinued code. Please avoid using.

If I remember correctly, this length filtering branch does not perform that well, nor does it lead to intuitive pieces.

Length filtering refers to the following procedure (hypothetical example):
  - Say there exists the chunks (with the same phonemes):
  - at, atmospher, atmo
  - Assume that "at" has two example words ("atom", "atmosphere"), that is, "at" occured as a candidate chunk in two different words.
  - Assume that "atmo" and "atmospher" are only found in "atmosphere".
    - Note that all prefixes and postfixes of a word (considering pg pairs, not direct letters) form the candidate chunks for a word.
  - Then, atmo would be filtered from the candidates and would not be considered.
    - This is because all example words corresponding to "atmo" can be found in the *longer* chunk, "atmospher".
  - However, "at" remains, because even though the "at" of "atmosphere" is expressed via the longer "atmospher", "at" still must be kept to correspond to the "at" in "atom". 
