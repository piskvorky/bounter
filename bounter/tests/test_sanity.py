import unittest
from bounter import CountMinSketch


class TestSanityCheck(unittest.TestCase):
	def test_sanity(self):
		cms = CountMinSketch(size_mb=10)

		cms.increment(1)
		cms.increment(1)
		cms.increment(1)
		cms.increment("string")

		self.assertEqual(cms[1], 3)
		self.assertEqual(cms["string"], 1)
		self.assertEqual(cms.cardinality(), 2)
		self.assertEqual(cms.sum, 4)


if __name__ == '__main__':
	unittest.main()