Bounded Counter – Count-min Sketch frequency estimation for large sets
======================================================================

**Work in progress!**

Count frequencies in massive data sets using fixed memory footprint with a smart
[Count-min Sketch](https://en.wikipedia.org/wiki/Count%E2%80%93min_sketch) implementation.

Contains implementation of Count-min Sketch table with conservative update, as well as our own implementation
using logarithmic probabilistic counter for reducing the space requirement (*log1024*).

A [hyperloglog](https://github.com/ascv/HyperLogLog) counter is used to estimate the cardinality of the set of elements (how many distinct elements are tracked).

```python
cms = CountMinSketch(size_mb=512) # Use 512 MB
print(cms.width)  # 16 777 216
print(cms.depth)   # 8
print(cms.size)  # 536 870 912 (512 MB in bytes)

cms.increment("foo")
cms.increment("bar")
cms.increment("foo")

print(cms["foo"]) # 2
print(cms["bar"]) # 1
print(cms.cardinality()) # 2
print(cms.total()) # 3
```

Parameters
----------

-   **size_mb** Maximum size of the structure in memory in megabytes.
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
    -   *conservative* Count-min Sketch as described on as described on [Wikipedia](https://en.wikipedia.org/wiki/Count%E2%80%93min_sketch).
        Uses 4 bytes per cell, storing values up to 2^32 - 1
    -   *log1024* is a conservative-update probabilistic counter with a value that fits into 2 bytes. Values of this counter
        up to 2048 are precise and larger values are off by +/- 2%. The maximum value is larger than 2^71
    -   *log8* is a conservative-update probabilistic counter that fits into just 1 byte. Values of this counter
        up to 8 are precise and larger values can be off by +/- 30%. The maximum value is larger than 2^33        

Memory
------
To calculate memory footprint:
    ( width * depth * cell_size ) + HLL size

Cell size is
   - 4B for conservative algorithm
   - 2B for log1024
   - 1B for log8
   
HLL size is 64 KB

Example:
    width 2^25 (33 554 432), depth 8, logcons1024 (2B) has 2^(25 + 3 + 1) + 64 KB = 536.9 MB
    Can be pickled to disk with this exact size.
