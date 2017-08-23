from collections import Counter
import os


def hash_key(i, key):
    return hash(str(i) + str(key))

algorithm_basic = 0
algorithm_conservative = 1
algorithm_logcounter = 2

class CountMinSketch(object):
    def __init__(self, width=16, depth=8, algorithm = None):
        self.width = width
        self.depth = depth
        self.hash_length = width.bit_length()
        self.hash_mask = (1 << (self.hash_length - 1)) - 1
        self.rows = dict()
        self.algorithm = algorithm_basic
        self.logshift = 0
        if algorithm and str(algorithm).lower() == 'conservative':
            self.algorithm = algorithm_conservative
        if algorithm and str(algorithm).lower() == 'logcounter8':
            self.algorithm = algorithm_logcounter
            self.logshift = 2
        if algorithm and str(algorithm).lower() == 'logcounter1024':
            self.algorithm = algorithm_logcounter
            self.logshift = 9
        self.logbase = 1 << (self.logshift + 1)
        for i in range(self.depth):
            self.rows[i] = Counter()

    def bucket(self, i, key):
        return self.hash_mask & hash_key(i, key)

    def increment(self, key):
        if self.algorithm == algorithm_basic:
            self.basic_increment(key)
        elif self.algorithm == algorithm_conservative:
            self.conservative_increment(key)
        elif self.algorithm == algorithm_logcounter:
            self.log_increment(key)
        else:
            raise AssertionError

    def basic_increment(self, key):
        for i in range(self.depth):
            self.rows[i][self.bucket(i, key)] += 1

    def conservative_increment(self, key):
        current = self[key]
        for i in range(self.depth):
            bucket = self.bucket(i, key)
            if self.rows[i][bucket] == current:
                self.rows[i][bucket] += 1

    def log_increment(self, key):
        for i in range(self.depth):
            bucket = self.bucket(i, key)
            current = self.rows[i][bucket]
            if current < 2 * self.logbase:
                self.rows[i][bucket] += 1
            else:
                mask = (1 << (int(current/self.logbase) - 1)) - 1
                r = int.from_bytes(os.urandom(4), byteorder='big', signed=False)
                if (r & mask) == 0:
                    current += 1
                    self.rows[i][bucket] = current

    def log_decode(self, log_value):
        if (log_value <= 2 * self.logbase):
            return log_value
        else:
            base = 1 << (int(log_value / self.logbase) + self.logshift)
            return int(base + (log_value % self.logbase) * (base / self.logbase))

    def __getitem__(self, key):
        minimum = None
        for i in range(self.depth):
            current = self.rows[i][self.bucket(i, key)]
            if (minimum == None):
                minimum = current
            else:
                minimum = min(minimum, current)
        if self.algorithm == algorithm_logcounter:
            return self.log_decode(minimum)
        else:
            return minimum
