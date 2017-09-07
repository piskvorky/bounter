import CMSC

class CountMinSketch(object):
    def __init__(self, size_mb=64, width=None, depth=None, algorithm='conservative'):

        cell_size = 4
        if algorithm and str(algorithm).lower() == 'log8':
            cell_size = 1
        elif algorithm and str(algorithm).lower() == 'log1024':
            cell_size = 2
        self.cell_size = cell_size

        if width is None and depth is None:
            self.width = 1 << (size_mb * 65536 // cell_size).bit_length()
            self.depth = (size_mb * 1048576) // (self.width * cell_size)
        elif width is None:
            self.depth = depth
            avail_width = (size_mb * 1048576) // (depth * cell_size)
            self.width = 1 << (avail_width.bit_length() - 1)
            if not self.width:
                raise ValueError("Requested depth is too large for maximum memory size!")
        elif depth is None:
            if width != 1 << (width.bit_length() - 1):
                raise ValueError("Requested width must be a power of 2!")
            self.width = width
            self.depth = (size_mb * 1048576) // (width * cell_size)
            if not self.depth:
                raise ValueError("Requested width is too large for maximum memory size!")
        else:
            if width != 1 << (width.bit_length() - 1):
                raise ValueError("Requested width must be a power of 2!")
            self.width = width
            self.depth = depth

        if algorithm and str(algorithm).lower() == 'log8':
            self.cms = CMSC.CMS_Log8(width=self.width, depth=self.depth)
        elif algorithm and str(algorithm).lower() == 'log1024':
            self.cms = CMSC.CMS_Log1024(width=self.width, depth=self.depth)
        else:
            self.cms = CMSC.CMS_Conservative(width=self.width, depth=self.depth)

    def increment(self, key):
        self.cms.increment(str(key))

    def __getitem__(self, key):
        return self.cms.get(str(key))

    def cardinality(self):
        """
        Returns an estimate for the number of distinct keys counted by the structure. The estimate should be within 1%.
        """
        return self.cms.cardinality()

    def total(self):
        return self.cms.total()

    def size(self):
        """
        Returns current size of the Count-min Sketch table in bytes.
        Does *not* include additional constant overhead used by parameter variables and HLL table, totalling less than 33KB.
        """
        return self.width * self.depth * self.cell_size
