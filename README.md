Bounded Counter – Count-min Sketch frequency estimation for large sets
======================================================================

Library implementing [Count-min Sketch](https://en.wikipedia.org/wiki/Count%E2%80%93min_sketch)
data structure used to estimate frequencies of elements in massive data sets with fixed memory footprint.

Contains implementation of the basic and conservative-update Count-min Sketch table, as well as our own implementation
using logarithmic probabilistic counter for reducing the space requirement (*logcons1024*).

A [hyperloglog](https://github.com/ascv/HyperLogLog) counter is used to estimate the cardinality of the set of elements (how many distinct elements are tracked).

Parameters
----------

-   **Width**: The number of columns (hash buckets) in a single row of the table. Must be a power of 2.
    Significantly affects precision and memory footprint. For precise results, this should be no smaller than one
    order of magnitude away from the cardinality of the set.
    For significantly smaller widths, deterioration will occur.
    For instance, to store all bigrams in English Wikipedia (1 857 420 106 bigrams, 179 413 989 unique),
    good results can be achieved with a width of 67 108 864 (2^26) (37%).
-   **Depth**: Number of rows, significant for the reliability of the result. Linearly affects speed of the
    algorithm as well as its memory footprint. For best results, use a small number such as 5.
    Using more than 8 is wasteful, better put that memory
    in width instead or use 'basic' or 'conservative' algorithms instead.
-   **Algorithm**: There are several algorithms available:
    -   *basic* straightforward implementation of the Count-Min Sketch as described on
        [Wikipedia](https://en.wikipedia.org/wiki/Count%E2%80%93min_sketch) with a cell size of 4 bytes.
    -   *conservative* variant of the algorithm using a simple optimization which is also described on Wikipedia. Also
        uses 4 bytes per cell.
    -   *logcounter8* is a probabilistic counter with a value that fits into 1 byte. Values of this counter are usually
        off by +/- 30%. This can be used for rough estimations for extremely large sets.
    -   *logcounter1024* is a probabilistic counter with a value that fits into 2 bytes. Values of this counter are usually
        off by +/- 2%.
    -   *logcons1024* is a conservative-update upgrade of 'logcounter1024' which offers substantially better precision of
        the structure.

Memory
------
To calculate memory footprint:
    ( width * depth * cell_size ) + HLL size

Cell size is
   - 4B for basic / conservative algorithm
   - 1B for logcounter8
   - 2B for logcounter1024 / logcons1024
HLL size is 32 KB

Example:
    width 2^26 (67 108 864), depth 4, logcons1024 (2B) has 2^(26 + 2 + 1) + 32 768 = 536.9 MB
    Can be pickled to disk with this exact size.