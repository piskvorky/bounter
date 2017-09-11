Changes
===========

## 0.2.0, 2017-09-01
* Count-min Sketch implemented in C with no external library dependencies 
* Removed weak algorithms, remaining 3 are all versions with conservative update
* embedded HLL inside the project
* added merge of 2 Count-min Sketch structures
* added update()
* added increment(key, x) to increase by x with one call


## 0.1.1, 2017-09-01
* Fix manifest so that bounter can be installed through pip install
* Fix a bug with determining depth based on size_MB 

## 0.1.0, 2017-09-01

:star2: Initial Release:

* Count-min Sketch with 5 algorithms (unoptimized)