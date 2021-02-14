# decoding_modeling
Modeling children's decoding skill using probabilistic programming

This was code to break down words into syllables with the EM-like algorithm. If I remember correctly, some changes were still being made when this branch was discontinued (note that I extracted a commit and then cloned this branch for ease of editing).

The motivation here was to prevent the misalignment between pre-existing syllablification algorithms and the phonix pg pairs. However, this was later solved when moving to CELEX and doing the alignments for most (but not all, see the final_wong_code branch for details) words in the intersection of the two.

## Concerns

If you want to use this branch, please note that the iterative test was disabled in "tests" because of the addition of CVC behavior. The test there will probably have to be re-calculated in order to use this test.

If I recall correctly, this code uses CVC_any pattern in the onset/rime breaking for the EM iterations, which is defined as any piece with a prefix of CVC, followed by anything.

There is a TODO marked, noting strange behavior if one sets the parameter to generating all possible segmentations as 0, if I remember correctly. I think it accompanies the assert that shortly follows. That may have to be investigated in the future if this code is to be reused elsewhere.
