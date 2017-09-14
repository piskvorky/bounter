import pickle

from htc import HT_Basic

htc = HT_Basic(buckets=16777216)
total_length = 0
for i in range(10000000):
    key = 'The best number is ' + str(i)
    htc[key] = i
    total_length += len(key)

print(total_length)
print(len(htc))

print("saving")
pickle.dump(htc, open("HTC_64.p", 'wb'))
print("saved")
