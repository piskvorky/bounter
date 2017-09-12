import pickle

from HTC import HT_Basic as HashTable

expected = {
    'foo': 17,
    'bar': 81,
    'goo': 77,
    'lorem ipsum dolor': 1234
}

htc = HashTable(buckets=64)

for key, value in expected.items():
    htc[key] = value

expected["+=item"] = 5
htc["+=item"] += 5

for key, value in expected.items():
    print("%s: %d (expected %d)" % (key, htc[key], value))

print("saving")
pickle.dump(htc, open("HTC.p", 'wb'))
print("saved")

htc2 = pickle.load(open("HTC.p", 'rb'))
print("loaded")

expected['new'] = 13
htc2.increment('new', 13)

for key, value in expected.items():
    print("%s: %d (expected %d)" % (key, htc2[key], value))

print("total %d (expected %d)" % (htc2.total(), 1422))
print("length %d (expected %d)" % (len(htc2), 5))

del htc2["foo"]
expected["foo"] = 0
print("deleted")

print("saving")
pickle.dump(htc2, open("HTC.p", 'wb'))
print("saved")

htc3 = pickle.load(open("HTC.p", 'rb'))
print("loaded")

for key, value in expected.items():
    print("%s: %d (expected %d)" % (key, htc3[key], value))
print("total %d (expected %d)" % (htc3.total(), 1405))
print("length %d (expected %d)" % (len(htc3), 4))

print("iterating!")
for (key, value) in htc3.items():
    print(key, value)

print("iteration finished!")

print("iterating DIRECTLY!")
for key in htc3:
    print(key)

print("iteration finished!")
