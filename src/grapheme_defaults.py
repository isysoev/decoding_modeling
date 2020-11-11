from collections import defaultdict
from phonix import *

def read_word_freqs(freq_file_name):
	wordfreq = {}
	with open(freq_file_name) as freqfile:
		for line in freqfile:
			word, freq = line.strip().split(' ')
			wordfreq[word] = float(freq)
	return wordfreq

def read_phonix_and_freqs(infilename, freq_file_name):
	wordfreq = read_word_freqs(freq_file_name)
	phx = read_phonix(infilename)
	phx = list(filter(lambda wm: wm[0] in wordfreq, phx))
	phxwords = set([word for (word, mapping) in phx])
	wordfreq = {word : freq for (word, freq) in wordfreq.items() if word in phxwords}
	return (phx, wordfreq)
 
def compute_grapheme_defaults(infilename, freq_file_name, outfilename):
	counter = defaultdict(lambda : defaultdict(float))
	phx, wordfreq = read_phonix_and_freqs(infilename, freq_file_name)
	for (word, mapping) in phx:
		freq = wordfreq[word]
		for (p, g) in mapping:
			counter[g][p] += freq
	grapheme_order = sorted(counter.keys(), key = lambda g: sum(counter[g].values()), reverse=True)
	with open(outfilename, 'w') as outfile:
		for g in grapheme_order:
			maxp = max(counter[g].keys(), key = lambda p: counter[g][p])
			maxp = ''.join(maxp)
			print(f'{g} {maxp}', file = outfile)

if '__main__' == __name__:
	compute_grapheme_defaults('../data/phonix.txt', '../data/word-freqs.txt', '../data/grapheme_defaults.txt')

