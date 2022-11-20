Changes
=======

## 1.2.0, 2022-11-20

* Add 64bit Min Sketch (__[@jponf](https://github.com/jponf)__, [#53](https://github.com/RaRe-Technologies/bounter/pull/53))

## 1.1.1, 2020-08-16

* Resolve pickle mem leak (__[@isamaru](https://github.com/isamaru)__, PR [#41](https://github.com/RaRe-Technologies/bounter/pull/41))

## 1.1.0, 2019-01-17

* Add `__contains__` to `CountMinSketch` (__[@isamaru](https://github.com/isamaru)__, [#38](https://github.com/RaRe-Technologies/bounter/pull/38))
* Use unsigned integers to address cms table (__[@tjbookreader](https://github.com/tjbookreader)__, [#35](https://github.com/RaRe-Technologies/bounter/pull/35))
* Document limitations of Bounter (__[@aneesh-joshi](https://github.com/aneesh-joshi)__, [#37](https://github.com/RaRe-Technologies/bounter/pull/37))
* Add blogpost link to `README.md` (__[@aneesh-joshi](https://github.com/aneesh-joshi)__, [#31](https://github.com/RaRe-Technologies/bounter/pull/31))
* Fix incorrect image link in `experiments.md` (__[@aneesh-joshi](https://github.com/aneesh-joshi)__, [#29](https://github.com/RaRe-Technologies/bounter/pull/29))
* Update twitter badge (__[@menshikh-iv](https://github.com/menshikh-iv)__, [c42dd6](https://github.com/RaRe-Technologies/bounter/commit/c42dd699db54e7e540c182aea74bffb2f36d09bd))
* Fix rst indents (__[@isamaru](https://github.com/isamaru)__, [#26](https://github.com/RaRe-Technologies/bounter/pull/26))
* Swap row labels for `log8` and `log1024` in documentation (__[@isamaru](https://github.com/isamaru)__, [#28](https://github.com/RaRe-Technologies/bounter/pull/28))

## 1.0.1, 2017-10-17
* single unified bounter API for easy initialization, including the new "layered" functionality approach
* simple CardinalityCounter to support Layer 1
* selecting iteration
* iteration methods for HashTable (keys, values, etc.)
* many small fixes and api tweaks
* README

## 0.2.0, 2017-09-01
* Added a fast HashTable counter implemented in C that removes low-count entries when it is running out of memory.
* Count-Min Sketch (CMS) implemented in C with no external library dependencies
* Removed weak CMS algorithms, remaining 3 are all versions with conservative update
* embedded HLL inside the project
* added merge of 2 CMS structures
* added update() to CMS
* added increment(key, x) to CMS to increase by x with one call


## 0.1.1, 2017-09-01
* Fix manifest so that bounter can be installed through pip install
* Fix a bug with determining depth based on size_MB

## 0.1.0, 2017-09-01

:star2: Initial Release:

* Count-min Sketch with 5 algorithms (unoptimized)
