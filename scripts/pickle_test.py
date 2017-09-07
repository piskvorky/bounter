import pickle

from bounter import CountMinSketch as CMS

filename = 'cms.p';

counter = CMS(width=1048576, depth=16, algorithm="log8")

counter.increment("foo")
counter.increment("bar")
counter.increment("bar")
counter.increment("lorem")
print(counter["foo"], counter["bar"], counter.cardinality(), counter.total())

print("pickling")
pickle.dump(counter, open(filename, "wb"))
print("pickled!")
rcounter = pickle.load(open(filename, "rb"))
print("unpickled")

print(rcounter["foo"], rcounter["bar"], rcounter.cardinality(), rcounter.total())
