import os
import numpy


def hash_key(i, key):
    return hash(str(i) + str(key))

algorithm_basic = 0
algorithm_conservative = 1
algorithm_logcounter = 2

class CountMinSketch(object):
    def __init__(self, width=16, depth=8, algorithm = None):
        self.logshift = 0
        array_type = numpy.uint32
        self.algorithm = algorithm_basic
        self.inc_method = self.basic_increment
        if algorithm and str(algorithm).lower() == 'conservative':
            self.algorithm = algorithm_conservative
            self.inc_method = self.conservative_increment
        if algorithm and str(algorithm).lower() == 'logcounter8':
            array_type = numpy.uint8
            self.algorithm = algorithm_logcounter
            self.logshift = 2
            self.inc_method = self.log_increment
        if algorithm and str(algorithm).lower() == 'logcounter1024':
            array_type = numpy.uint16
            self.algorithm = algorithm_logcounter
            self.logshift = 9
            self.inc_method = self.log_increment

        self.width = width
        self.depth = depth
        self.hash_length = width.bit_length()
        self.hash_mask = (1 << (self.hash_length - 1)) - 1
        self.logbase = 1 << (self.logshift + 1)
        self.table = numpy.zeros((depth, width), array_type)


    def bucket(self, i, key):
        return self.hash_mask & hash_key(i, key)

    def increment(self, key):
        self.inc_method(key)

    def basic_increment(self, key):
        for i in range(self.depth):
            self.table[i][self.bucket(i, key)] += 1

    def conservative_increment(self, key):
        current = self[key]
        for i in range(self.depth):
            bucket = self.bucket(i, key)
            if self.table[i, bucket] == current:
                self.table[i, bucket] += 1

    def log_increment(self, key):
        for i in range(self.depth):
            bucket = self.bucket(i, key)
            current = int(self.table[i, bucket])
            if current < 2 * self.logbase:
                self.table[i, bucket] += 1
            else:
                mask = (1 << (current//self.logbase - 1)) - 1
                r = int.from_bytes(os.urandom(4), byteorder='big', signed=False)
                if (r & mask) == 0:
                    current += 1
                    self.table[i, bucket] = current

    def log_decode(self, log_value):
        if (log_value <= 2 * self.logbase):
            return log_value
        else:
            base = 1 << ((log_value >> (self.logshift + 1)) + self.logshift)
            return int(base + (log_value % self.logbase) * (base / self.logbase))

    def log_encode(self, input):
        value = int(input)
        if (value <= 2 * self.logbase):
            return value
        base_bits = value.bit_length() - 1
        log_value_base = (base_bits - self.logshift) * self.logbase

        remainder = (value >> (base_bits - self.logshift - 1)) - self.logbase
        return log_value_base + remainder

    def __getitem__(self, key):
        minimum = None
        for i in range(self.depth):
            current = self.table[i, self.bucket(i, key)]
            if (minimum == None):
                minimum = current
            else:
                minimum = min(minimum, current)
        if self.algorithm == algorithm_logcounter:
            return self.log_decode(minimum)
        else:
            return minimum
