"""
Runs bounter on bigrams from the first N wiki articles for the purpose of phrases creation.
First, counts bigrams using python dictionary (exact count). Then repeats using bounter with
different parameters.
For each run of bounter, compares the results to reference counter w.r.t. phraser collocation algorithm.
"""

import smart_open
from bounter import CountMinSketchC as CountMinSketch
# from bounter import CountMinSketch as CountMinSketch
from collections import Counter
from timeit import default_timer as timer
# from bounter import CountMinSketch as CountMinSketch
from collections import Counter
from timeit import default_timer as timer

import smart_open

from bounter import CountMinSketchC as CountMinSketch

min_count = 5
threshold = 10.0
articles = 200
wiki_file = 'C:/rare/corpus/wiki/title_tokens.txt.gz'

wiki = smart_open.smart_open(wiki_file)


class Reference(object):
    def __init__(self):
        self.counter = Counter()
        self.sum = 0
        self.card = 0

    def increment(self, key):
        self.counter[key] += 1
        self.sum += 1
        self.card = None

    def __getitem__(self, key):
        return self.counter[key]

    def cardinality(self):
        if self.card is None:
            self.card = len(self.counter)
        return self.card


def load_single(counter, unigrams=None):
    wiki.seek(0)
    loaded_articles = 0
    words = 0
    for lineno, line in enumerate(wiki):
        loaded_articles += 1
        last_word = None
        for word in line.decode().split('\t')[1].split():
            if unigrams is not None:
                unigrams[word] += 1
            if last_word:
                words += 1
                counter.increment(last_word + ' ' + word)
            last_word = word
        if loaded_articles >= articles:
            break
    return counter


def score(wc1, wc2, bc, total):
    pa = float(wc1)
    pb = float(wc2)
    pab = float(bc)
    return (pab - min_count) / pa / pb * total


def compare_single(counter, reference, unigrams):
    true_pos = 0
    true_neg = 0
    t1_error = 0
    t2_error = 0
    variance = 0
    rtotal = counter.cardinality()
    etotal = reference.cardinality()

    for bigram in reference.counter:
        [word1, word2] = bigram.split(' ')
        wc1 = unigrams[word1]
        wc2 = unigrams[word2]
        rfrequency = counter[bigram]
        efrequency = reference[bigram]

        variance += (rfrequency - efrequency) ** 2

        rscore = score(wc1, wc2, rfrequency, rtotal)
        escore = score(wc1, wc2, efrequency, etotal)

        rphrase = (rfrequency >= min_count and rscore >= threshold)
        ephrase = (efrequency >= min_count and escore >= threshold)
        if rphrase == ephrase:
            if rphrase:
                true_pos += 1
            else:
                true_neg += 1
        else:
            if rphrase:
                t1_error += 1
            else:
                t2_error += 1

    deviation = variance / rtotal
    precision = true_pos / (true_pos + t1_error)
    recall = true_pos / (true_pos + t2_error)
    f1 = 2 * precision * recall / (precision + recall)
    return (deviation, precision, recall, f1)


def test_single(counter, reference, unigrams):
    start = timer()
    load_single(counter)
    end = timer()
    (deviation, precision, recall, f1) = compare_single(counter, reference, unigrams)
    return (end - start, deviation, precision, recall, f1)


reference = Reference()
unigrams = Counter()
load_single(reference, unigrams)
print("Loaded %d bigrams (%d distinct)" % (reference.sum, reference.cardinality()))

sizes_start = int(reference.cardinality()).bit_length() - 4
# sizes = (1 << (sizes_start + i) for i in range(8))
# for width in sizes:
for width in [262144]:
    #    for algorithm in ('conservative', 'logcons1024', 'logcounter8'):
    for algorithm in ['conservative']:
        for depth in (3, 4, 5, 6, 8, 10):
            cms = CountMinSketch(width=width, depth=depth, algorithm=algorithm)
            (time, deviation, precision, recall, f1) = test_single(cms, reference, unigrams)
            print("%d\t%s\t%d\t%d\t%f\t%f\t%f\t%f\t%s" %
                  (cms.size(), algorithm, width, depth, deviation, precision, recall, f1, time))
