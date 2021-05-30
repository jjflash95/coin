import hashlib
import bitarray
import base64


ASCII0 = 48
TIMES = 2
MAXSIZE = 1371072


class BloomFilter:
    """
    HASHES GUID TO BLOOM INDEX, AT CURRENT 3 ITERATIONS,
    MAX INDEX IS 1371072 AND SO IS THE LENGTH OF THE
    FILTER
    """

    def __init__(self, guid):
        bid, index = BloomFilter.makebloomid(guid)
        self.filter = BloomFilter.initfilter()
        self.id = bid
        self.index = index
        self.addindex(index)

    def mergefilter(self, newfilter):
        self.filter |= newfilter

    def addindex(self, index):
        self.filter[index - 1] = 1
        return self

    def removeguid(self, guid):
        _, index = BloomFilter.makebloomid(guid)
        self.removeindex(index)

    def tostring(self):
        return base64.b64encode(self.filter.tobytes())

    def addfilter(self, filter):
        filter = base64.b64decode(filter)
        newfilter = bitarray.bitarray(endian='little')
        newfilter.frombytes(filter)
        self.mergefilter(newfilter)


    @staticmethod
    def initfilter():
        plus = MAXSIZE % 8
        filter = bitarray.bitarray(MAXSIZE + plus, endian='little')
        filter.setall(0)
        return filter

    @staticmethod
    def sha256(string):
        return hashlib.sha256(string.encode('utf-8')).hexdigest()

    @staticmethod
    def makebloomid(guid):
        bloomid = BloomFilter.sha256(guid)
        for i in range(TIMES):
            bloomid += BloomFilter.sha256(bloomid)
        
        bloomidx = 0
        for i, char in enumerate(bloomid, 1):
            bloomidx += (ord(char) - ASCII0) * i

        return bloomid, bloomidx

