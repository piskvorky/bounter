from htc import HT_Basic as HashTable

expected = {
    'foo': 17,
    'bar': 81,
    'goo': 77,
    'lorem ipsum dolor': 1234
}

htc = HashTable(buckets=64)

htc.update(expected)

for pair in htc.items():
    print(pair)

print("Tuple!")

expected = ('lorem', 'ipsum', 'dolor')
htc.update(expected)

for pair in htc.items():
    print(pair)

print("List!")

expected = ('lorem', 'ipsum', 'dolor')
htc.update(expected)

for pair in htc.items():
    print(pair)
