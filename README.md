# Bounter -- Counter for large datasets

[![License](https://img.shields.io/pypi/l/bounter.svg)](https://github.com/RaRe-Technologies/bounter/blob/master/LICENSE)
[![Build Status](https://travis-ci.org/RaRe-Technologies/bounter.svg?branch=master)](https://travis-ci.org/RaRe-Technologies/bounter)
[![GitHub release](https://img.shields.io/github/release/rare-technologies/bounter.svg?maxAge=3600)](https://github.com/RaRe-Technologies/bounter/releases)
[![Downloads](https://pepy.tech/badge/bounter/week)](https://pepy.tech/project/bounter/week)

Bounter is a Python library, written in C, for extremely fast probabilistic counting of item frequencies in massive datasets. Unlike `Counter`, it uses only a small fixed memory footprint.

## Why Bounter?

Bounter lets you count how many times an item appears, similar to Python's built-in `dict` or `Counter`:

```python
from bounter import bounter

counts = bounter(size_mb=1024)  # use at most 1 GB of RAM
counts.update([u'a', 'few', u'words', u'a', u'few', u'times'])  # count item frequencies

print(counts[u'few'])  # query the counts
2
```

However, unlike `dict` or `Counter`, Bounter can process huge collections where the items would not even fit in RAM. This commonly happens in Machine Learning and NLP, with tasks like **dictionary building** or **collocation detection** that need to estimate counts of billions of items (token ngrams) for their statistical scoring and subsequent filtering.

Bounter implements approximative algorithms using optimized low-level C structures, to avoid the overhead of Python objects. It lets you specify the maximum amount of RAM you want to use. In the Wikipedia example below, Bounter uses 31x less memory compared to `Counter`.

Bounter is also marginally faster than the built-in `dict` and `Counter`, so wherever you can represent your **items as strings** (both byte-strings and unicode are fine, and Bounter works in both Python2 and Python3), there's no reason not to use Bounter instead except:


## When not to use Bounter?
Beware, Bounter is only a probabilistic frequency counter and cannot be relied on for exact counting. (You can't expect a data structure with finite size to hold infinite data.)
Example of Bounter failing:

```python
from bounter import bounter
bounts = bounter(size_mb=1)
bounts.update(str(i) for i in range(10000000))
bounts['100']
0
```

Please use `Counter` or `dict` when such exact counts matter. When they don't matter, like in most NLP and ML applications with huge datasets, Bounter is a very good alternative.

## Installation

Bounter has no dependencies beyond Python >= 2.7 or Python >= 3.3 and a C compiler:

```bash
pip install bounter  # install from PyPI
```

Or, if you prefer to install from the [source tar.gz](https://pypi.python.org/pypi/bounter):

```bash
python setup.py test  # run unit tests
python setup.py install
```

## How does it work?

No magic, just some clever use of approximative algorithms and solid engineering.

In particular, Bounter implements three different algorithms under the hood, depending on what type of "counting" you need:

1. **[Cardinality estimation](https://en.wikipedia.org/wiki/Count-distinct_problem): "How many unique items are there?"**

```python
from bounter import bounter

counts = bounter(need_counts=False)
counts.update(['a', 'b', 'c', 'a', 'b'])

print(counts.cardinality())  # cardinality estimation
3
print(counts.total())  # efficiently accumulates counts across all items
5
```

  This is the simplest use case and needs the least amount of memory, by using the [HyperLogLog algorithm](http://algo.inria.fr/flajolet/Publications/FlFuGaMe07.pdf) (built on top of Joshua Andersen's [HLL](https://github.com/ascv/HyperLogLog) code).

2. **Item frequencies: "How many times did this item appear?"**

```python
from bounter import bounter

counts = bounter(need_iteration=False, size_mb=200)
counts.update(['a', 'b', 'c', 'a', 'b'])
print(counts.total(), counts.cardinality())  # total and cardinality still work
(5L, 3L)

print(counts['a'])  # supports asking for counts of individual items
2
```

  This uses the [Count-min Sketch algorithm](https://en.wikipedia.org/wiki/Count%E2%80%93min_sketch) to estimate item counts efficiently, in a **fixed amount of memory**. See the [API docs](https://github.com/RaRe-Technologies/bounter/blob/master/bounter/bounter.py) for full details and parameters.

As a further optimization, Count-min Sketch optionally support a [logarithmic probabilistic counter](https://en.wikipedia.org/wiki/Approximate_counting_algorithm):

 - `bounter(need_iteration=False)`: default option. Exact counter, no probabilistic counting. Occupies 4 bytes (max value 2^32) per bucket.
 - `bounter(need_iteration=False, log_counting=1024)`: an integer counter that occupies 2 bytes. Values up to 2048 are exact; larger values are off by +/- 2%. The maximum representable value is around 2^71.
 - `bounter(need_iteration=False, log_counting=8)`: a more aggressive probabilistic counter that fits into just 1 byte. Values up to 8 are exact and larger values can be off by +/- 30%. The maximum representable value is about 2^33.

Such memory vs. accuracy tradeoffs are sometimes desirable in NLP, where being able to handle very large collections is more important than whether an event occurs exactly 55,482x or 55,519x.

3. **Full item iteration: "What are the items and their frequencies?"**

```python
from bounter import bounter

counts = bounter(size_mb=200)  # default version, unless you specify need_items or need_counts
counts.update(['a', 'b', 'c', 'a', 'b'])
print(counts.total(), counts.cardinality())  # total and cardinality still work
(5L, 3)
print(counts['a'])  # individual item frequency still works
2

print(list(counts))  # iterator returns keys, just like Counter
[u'b', u'a', u'c']
print(list(counts.iteritems()))  # supports iterating over key-count pairs, etc.
[(u'b', 2L), (u'a', 2L), (u'c', 1L)]
```

  Stores the keys (strings) themselves in addition to the total cardinality and individual item frequency (8 bytes). Uses the most memory, but supports the widest range of functionality.

  This option uses a custom C hash table underneath, with optimized string storage. It will remove its low-count objects when nearing the maximum alotted memory, instead of expanding the table.

----

For more details, see the [API docstrings](https://github.com/RaRe-Technologies/bounter/blob/master/bounter/bounter.py) or read the [blog](https://rare-technologies.com/counting-efficiently-with-bounter-pt-1-hashtable/).

## Example on the English Wikipedia

Let's count the frequencies of all bigrams in the English Wikipedia corpus:

```python
with smart_open('wikipedia_tokens.txt.gz') as wiki:
    for line in wiki:
        words = line.decode().split()
        bigrams = zip(words, words[1:])
        counter.update(u' '.join(pair) for pair in bigrams)

print(counter[u'czech republic'])
42099
```

The Wikipedia dataset contained 7,661,318 distinct words across 1,860,927,726 total words, and 179,413,989 distinct bigrams across 1,857,420,106 total bigrams. Storing them in a naive built-in `dict` would consume over 31 GB RAM.

To test the accuracy of Bounter, we automatically extracted [collocations](https://en.wikipedia.org/wiki/Collocation) (common multi-word expressions, such as "New York", "network license", "Supreme Court" or "elementary school") from these bigram counts.

We compared the set of collocations extracted from Counter (exact counts, needs lots of memory) vs Bounter (approximate counts, bounded memory) and present the precision and recall here:

| Algorithm                                                        | Time to build |    Memory  | Precision |   Recall | F1 score |
|------------------------------------------------------------------|--------------:|-----------:|----------:|---------:|---------:|
| `Counter` (built-in)                                             |       32m 26s |      31 GB |      100% |     100% |     100% |
| `bounter(size_mb=128, need_iteration=False, log_counting=8)`     |       19m 53s | **128 MB** |    95.02% |   97.10% |   96.04% |
| `bounter(size_mb=1024)`                                          |       17m 54s |       1 GB |      100% |   99.27% |   99.64% |
| `bounter(size_mb=1024, need_iteration=False)`                    |       19m 58s |       1 GB |    99.64% |     100% |   99.82% |
| `bounter(size_mb=1024, need_iteration=False, log_counting=1024)` |       20m 05s |       1 GB |  **100%** | **100%** | **100%** |
| `bounter(size_mb=1024, need_iteration=False, log_counting=8)`    |       19m 59s |       1 GB |    97.45% |   97.45% |   97.45% |
| `bounter(size_mb=4096)`                                          |   **16m 21s** |       4 GB |      100% |     100% |     100% |
| `bounter(size_mb=4096, need_iteration=False)`                    |      20m 14s  |       4 GB |      100% |     100% |     100% |
| `bounter(size_mb=4096, need_iteration=False, log_counting=1024)` |       20m 14s |       4 GB |      100% |   99.64% |   99.82% |

Bounter achieves a perfect F1 score of 100% at 31x less memory (1GB vs 31GB), compared to a built-in `Counter` or `dict`. It is also 61% faster.

Even with just 128 MB (250x less memory), its F1 score is still 96.04%.

# Support

Use [Github issues](https://github.com/RaRe-Technologies/bounter/issues) to report bugs, and our [mailing list](https://groups.google.com/forum/#!forum/gensim) for general discussion and feature ideas.

----------------

`Bounter` is open source software released under the [MIT license](https://github.com/rare-technologies/bounter/blob/master/LICENSE).

Copyright (c) 2017 [RaRe Technologies](https://rare-technologies.com/)
