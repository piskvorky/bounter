Changes
===========

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