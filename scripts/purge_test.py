import math

import smart_open
from HTC import HT_Basic as HashTable

from bounter import CountMinSketch


def loadWiki(counter, articles=1):
    loaded_articles = 0
    words = 0
    wiki = smart_open.smart_open('C:/rare/corpus/wiki/title_tokens.txt.gz')
    for lineno, line in enumerate(wiki):
        loaded_articles += 1
        for word in line.decode().split('\t')[1].split():
            counter.increment(word)
            words += 1
        if loaded_articles >= articles:
            break
        if loaded_articles % 100000 == 0:
            print('Loaded %d articles' % loaded_articles)
    return (loaded_articles, words)


maxarticles = 10000

counter = HashTable(1048576)
print(loadWiki(counter, maxarticles))
print(len(counter))

counter2 = HashTable(262144)
print(loadWiki(counter2, maxarticles))
print(len(counter2))
print(counter2.total())

cms = CountMinSketch(width=262144, depth=8, algorithm="conservative")
print(loadWiki(cms, maxarticles))

variance = 0
errors = 0
for key, value in counter.items():
    if counter2[key] != value:
        variance += (value - counter2[key]) ** 2
        errors += 1

print(variance, errors)
print(math.sqrt(variance / len(counter)))

print("Memory large: ", counter.mem())
print("Memory small:", counter2.mem())

variance = 0
errors = 0
for key, value in counter.items():
    if cms[key] != value:
        variance += (value - cms[key]) ** 2
        errors += 1

print(variance, errors)
print(math.sqrt(variance / len(counter)))
print(cms.size())
