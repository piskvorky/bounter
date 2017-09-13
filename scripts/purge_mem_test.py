import time

import smart_open
from HTC import HT_Basic as HashTable


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


maxarticles = 100000000

counter = HashTable(1048576)
print(counter.mem())

time.sleep(30)
print("starting!")
print(loadWiki(counter, maxarticles))
print("done!")
time.sleep(30)
print(counter.mem())
