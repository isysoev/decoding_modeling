# decoding_modeling
Modeling children's decoding skill using probabilistic programming

Discontinued code. Please avoid using this code.

This was an in-progress branch that was eventually abandoned. It uses "pre/post/alt" decoding, which is how I referred to decoding of the following type (if I remember correctly):

For every word,
- Make candidate chunks
  - Propose all prefixes and postfixes (using pg pairs, not letters) as possible chunks, excluding the entire word
  - At one point, I think I did accept entire words separately if they were undecodable, at the end. However, I'm not sure.
- Attempt to decode these chunks in increasing length order. 
  - Cut the largest prefix possible repeatedly (forward decode)
  - Cut the largest postfix possible repeatedly (postfix decode)
  - Cut the remaining piece in alternating fashion (largest prefix, largest postfix, etc)
- Chunks that can't be decoded in the following format are memorized as new chunks.

Note that the latest commit has some special behaviors where double consonants are processed out of the words, if I remember correctly.

I think this was the last iteration of the prefix/postfix based approaches.

If I remember correctly, I don't think this yielded chunks that were very intuitive, which is why we transitioned to the onset/rime and syllable-based approaches.
