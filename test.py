from bounter import bounter

lines = [
    ['some', 'sentence'],
    ['another', 'sentence'],
    ['here', 'have', 'some', 'more'],
    ['you', 'should', 'stop', 'now'],
]

counter = bounter(size_mb=1024, need_iteration=False, log_counting=1024)

for line in lines:
    bigrams = zip(line, line[1:])
    counter.update(line)
    counter.update(' '.join(pair) for pair in bigrams)

print(counter['some'])
print('some' in counter)
print('aneesh' in counter)
