# Bounter -- Counter for large datasets in bounded memory

[![Build Status](https://travis-ci.org/RaRe-Technologies/bounter.svg?branch=master)](https://travis-ci.org/RaRe-Technologies/bounter)[![GitHub release](https://img.shields.io/github/release/rare-technologies/bounter.svg?maxAge=2592000)](https://pypi.python.org/pypi/bounter)[![Mailing List](https://img.shields.io/badge/-Mailing%20List-lightgrey.svg)](https://groups.google.com/forum/#!forum/gensim)[![Gitter](https://img.shields.io/badge/gitter-join%20chat%20%E2%86%92-09a3d5.svg)](https://gitter.im/RaRe-Technologies/gensim)[![Follow](https://img.shields.io/twitter/follow/spacy_io.svg?style=social&label=Follow)](https://twitter.com/gensim_py)

Bounter is a Python library, written in C, for extremely fast counting of item frequencies in massive datasets, using only a fixed memory footprint.

## Why Bounter?

Bounter lets you count how many times an item appears, similar to Python's built-in `dict` or `Counter`:

```python
from bounter import bounter

counts = bounter(size_mb=1024)  # use at most 1 GB of RAM
counts.update([u'a', 'few', u'words', u'a', u'few', u'times'])
print(counts[u'few'])

2
```

However, unlike `dict` or `Counter`, Bounter can process huge collections where the items would not even fit in RAM. This commonly happens in Machine Learning and NLP, with tasks like **dictionary building** or **collocation detection** that need to count billions of items (token ngrams) for their statistical scoring and filtering.

Bounter implements approximative algorithms using optimized low-level C structures, to avoid the overhead of Python objects. It lets you specify the maximum amount of RAM you want to use.

Bounter is also marginally faster than the built-in `dict` and `Counter`, so where you can represent your items as strings (both byte-strings and unicode are fine, and Bounter works in both Python2 and Python3), there's no reason not to use Bounter instead.


## Installation

Bounter has no dependencies beyond Python >= 2.7 or Python >= 3.3 and a C compiler:

```bash
pip install bounter  # install from PyPI
```

Or, if you prefer to install from the source tar.gz:

```bash
python setup.py test  # run unit tests
python setup.py install
```

## How does it work?

No magic, just some clever use of approximative algorithms and solid engineering.

In particular, Bounter implements three different algorithms under the hood, depending on what type of "counting" you need:

1. [Cardinality estimation](https://en.wikipedia.org/wiki/Count-distinct_problem): "How many unique items are there?"

  ```python
  from bounter import bounter

  counts = bounter(need_counts=False)
  counts.update(['a', 'b', 'c', 'a', 'b'])
  print(len(counts))  # cardinality estimation

  3
  ```

  FIXME what else does this support? `total()` = `sum()`?

  This is the simplest use case and needs the least amount of memory, by using the [HyperLogLog algorithm](http://algo.inria.fr/flajolet/Publications/FlFuGaMe07.pdf) (built on top of Joshua Andersen's [HLL](https://github.com/ascv/HyperLogLog) code).

2. Item frequencies: "How many times did this item appear?"

  ```python
  from bounter import bounter
  counts = bounter(need_items=False, size_mb=200)
  counts.update(['a', 'b', 'c', 'a', 'b'])
  print(len(counts))  # total cardinality still works
  print(counts['a'])  # but also supports asking for counts of individual items

  2
  ```

  This uses the [Count-min Sketch algorithm](https://en.wikipedia.org/wiki/Count%E2%80%93min_sketch) to estimate item counts efficiently, in a **fixed amount of memory**.

3. Full items iteration: "What are the items and their frequencies?"

  ```python
  from bounter import bounter
  counts = bounter(size_mb=200)  # default version, unless you specify need_items or need_counts
  counts.update(['a', 'b', 'c', 'a', 'b'])
  print(len(counts))  # total cardinality works
  print(counts['a'])  # item frequency works
  print(counts.keys())  # also support iteritems, values, etc.
  ```

  Also stores the keys (strings) themselves in addition to cardinality and item frequency. Uses the most memory, but supports the most functionality.

  This uses a custom C hash table underneath, with optimized string storage. It will remove its low-count objects when nearing the maximum alotted memory, instead of expanding the table.

----

As a further optimization, all algorithms optionally support a [logarithmic probabilistic counter](https://en.wikipedia.org/wiki/Approximate_counting_algorithm):

 - `bounter(cnt='log1024')`: an integer counter that occupies 2 bytes. Values up to 2048 are exact; larger values are off by +/- 2%. The maximum representable value is around 2^71.
 - `bounter(cnt='log8')`: a more aggressive probabilistic counter that fits into just 1 byte. Values up to 8 are exact and larger values can be off by +/- 30%. The maximum representable value is about 2^33.
 - `bounter(cnt='conservative')`: default option. Exact counter, no probabilistic counting. Occupies 4 bytes (max value 2^32).

Such memory vs. accuracy tradeoffs is sometimes desirable in NLP, where being able to handle very large collections is more important than whether an event happens exactly 55,482x or 55,519x.

For more details, see the [FIXME API docstrings](https://github.com/RaRe-Technologies/bounter/blob/master/bounter/bounter.py).

## Example on the English Wikipedia

Let's count the frequencies of all bigrams in the English Wikipedia corpus:

```python
with smart_open('wikipedia_tokens.txt.gz') as wiki:
    for line in wiki:
        words = line.decode().split()
        bigrams = zip(words, words[1:])
        counter.update(u' '.join(pair for pair in bigrams))

print(counter[u'czech republic'])

FIXME
```

The Wikipedia dataset contained 7,661,318 distinct words across 1,860,927,726 total words, and 179,413,989 distinct bigrams across 1,857,420,106 total bigrams. Storing them in a naive `dict` would consume more than 17GB RAM.

To test the accuracy of Bounter, we automatically extracted [collocations](https://en.wikipedia.org/wiki/Collocation) (common multi-word expressions, such as "New York", "network license", "Supreme Court" or "elementary school") from these bigram counts.

We compared the set of collocations extracted from Counter (exact counts, needs lots of memory) vs Bounter (approximate counts, bounded memory) and present the precision and recall:


| Algorithm                         | Time to build | Memory  | Precision | Recall | F1 score
|-----------------------------------|--------------:|--------:|----------:|-------:|---------:|
| `Counter` (built-in)              |         FIXME | 17.2 GB |      100% |   100% |     100% |
| `bounter(size_mb=1024)`           |         FIXME |   FIXME |     FIXME |  FIXME |    FIXME |
| `bounter(size_mb=1024, need_counts=False)` |         FIXME |   FIXME |    FIXME |
| `bounter(size_mb=4096, cnt='log1024')` |         FIXME |   FIXME |    FIXME |
| `bounter(size_mb=4096, need_counts=False)` |         FIXME |   FIXME |    FIXME |
| `bounter(size_mb=1024, need_counts=False, cnt='log1024`)` |         FIXME |   FIXME |    FIXME |
| `bounter(size_mb=1024, need_counts=False, cnt='log8`)` |         FIXME |   FIXME |    FIXME |


# Support

Use [Github issues](https://github.com/RaRe-Technologies/bounter/issues) to report bugs, and our [mailing list](https://groups.google.com/forum/#!forum/gensim) for general discussion and feature ideas.

----------------

`Bounter` is open source software released under the [MIT license](https://github.com/rare-technologies/bounter/blob/master/LICENSE).

Copyright (c) 2017 [RaRe Technologies](https://rare-technologies.com/)
