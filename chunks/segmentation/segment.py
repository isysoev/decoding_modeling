#!/usr/bin/env python3
# -*- coding: utf-8 -*-

## All functions below 12/13: From Ivan's Segment-TOWRE.ipynb code.
## These were copied here for convenience of importing.

def normalize(distr):
    denominator = sum(distr.values())
    return {key: float(value) / denominator for key, value in distr.items()}

class LList:
    def __init__(self, *args):
        if 0 == len(args):
            self._tip = None
            self._prefix = None
            self._len = 0
        elif 1 == len(args):
            self._tip = args[0]
            self._prefix = LList()
            self._len = 1
        else:
            self._tip = args[1]
            self._prefix = args[0]
            self._len = 1 + len(self._prefix)

    def tip(self):
        return self._tip

    def prefix(self):
        return self._prefix

    def nil(self):
        return self._len == 0

    def __len__(self):
        return self._len

    def toPy(self):
        if self.nil(): return []
        pylist = self._prefix.toPy()
        pylist.append(self._tip)
        return pylist
    
def possibleSegmentations(sequence, cutoff_len): #This border is from Ivan's code.
    #It seems that cutoff_len to used to determine the maximal permissible substring.
    if 0 == len(sequence): return []
    segmentationColumn = [LList(LList(sequence[0]))]
    for i in range(1, len(sequence)):
        newSegmentationColumn = []
        symI = sequence[i]
        for segmentation in segmentationColumn:
            newSegmentationColumn.append(LList(segmentation, LList(symI)))
            if len(segmentation.tip()) < cutoff_len:
                newSegmentationColumn.append(LList(segmentation.prefix(), LList(segmentation.tip(), symI)))
        segmentationColumn = newSegmentationColumn
    return [[subsequence.toPy() for subsequence in segmentation.toPy()] for segmentation in segmentationColumn]

def assortSegmentations(segmentations):
    sorter = defaultdict(list)
    for segmentation in segmentations:
        sorter[len(segmentation)].append(segmentation)
    return sorter