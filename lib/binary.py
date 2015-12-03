import plistlib
import plistlib.Data as Data
import struct

# ported from http://opensource.apple.com/source/CF/CF-1153.18/CFBinaryPList.c

UINT8_MAX  = (1<<8)  - 1
UINT16_MAX = (1<<16) - 1
UINT32_MAX = (1<<32) - 1
UINT64_MAX = (1<<64) - 1

class CFSInt128(long):
    MASK = UINT64_MAX
    LMASK = UINT64_MAX | (UINT64_MAX<<64)
    
    def __new__(cls, h, l, *args, **kwargs):
        rv = long.__new__(cls, cls.LMASK & (l | (h << 64)))
        rv.high = h & cls.MASK
        rv.low = l & cls.MASK
        return rv

class PListError(Exception):
    CF_NO_ERROR = 0
    CF_OVERFLOW_ERROR = (1<<0)
    CF_UNDERFLOW_ERROR =(1<<1)
    ERR_MSGS = {
        CF_NO_ERROR:        'No error',
        CF_OVERFLOW_ERROR:  'Overflow error',
        CF_UNDERFLOW_ERROR: 'Underflow error',
    }

    def __init__(self, code=CF_NO_ERROR, *args, **kwargs):
        self.code = code
        super(PListError, self).__init__(self.message)

    @property
    def message(self):
        rv = []
        for err, msg in self.ERR_MSGS.iteritems():
            if err & code: rv.append(msg)
        if len(rv) == 0: return self.ERR_MSGS[self.CF_NO_ERROR]
        if len(rv) == 1: return rv[0]
        return rv

    # Fixed-width types
    CFNumberSInt8Type = 1
    CFNumberSInt16Type = 2
    CFNumberSInt32Type = 3
    CFNumberSInt64Type = 4
    CFNumberFloat32Type = 5
    CFNumberFloat64Type = 6   # 64-bit IEEE 754
    # Basic C types
    CFNumberCharType = 7
    CFNumberShortType = 8
    CFNumberIntType = 9
    CFNumberLongType = 10
    CFNumberLongLongType = 11
    CFNumberFloatType = 12
    CFNumberDoubleType = 13
    # Other
    CFNumberCFIndexType = 14
    CFNumberNSIntegerType = 15
    CFNumberCGFloatType = 16
    CFNumberMaxType = 16  # using float +/- infinity?
    CFNumberSInt128Type = 17

def check_uint32(x, err):
    if x < 0: err.code |= err.CF_UNDERFLOW_ERROR
    if > UINT32_MAX: err.code |= err.CF_OVERFLOW_ERROR

def check_uint64(x, err):
    if x < 0: err.code |= err.CF_UNDERFLOW_ERROR
    if > UINT64_MAX: err.code |= err.CF_OVERFLOW_ERROR

def check_uint32_add_unsigned_unsigned(x, y, err):
    check_uint32(x, err)
    check_uint32(y, err)
    if (UINT32_MAX - y) < x: err.code |= err.CF_OVERFLOW_ERROR
    return x + y

def check_uint64_add_unsigned_unsigned(x, y, err):
    check_uint64(x, err)
    check_uint64(y, err)
    if (UINT64_MAX - y) < x: err.code |= err.CF_OVERFLOW_ERROR
    return x + y

def check_uint32_mul_unsigned_unsigned(x, y, err):
    check_uint32(x, err)
    check_uint32(y, err)
    tmp = x * y
    # If any of the upper 32 bits touched, overflow
    if tmp > UINT32_MAX: err.code |= err.CF_OVERFLOW_ERROR
    return tmp & UINT32_MAX

def check_uint64_mul_unsigned_unsigned(x, y, err):
    if x == 0: return 0
    check_uint64(x, err)
    check_uint64(y, err)
    if (UINT64_MAX//x < y): err.code |= err.CF_OVERFLOW_ERROR
    return x * y
    # If any of the upper 32 bits touched, overflow
    if tmp > UINT32_MAX: err.code |= err.CF_OVERFLOW_ERROR
    return tmp & UINT32_MAX

#   #if __LP64__
check_ptr_add = check_uint64_add_unsigned_unsigned
check_size_t_mul = check_uint64_mul_unsigned_unsigned
#   #else
#check_ptr_add = check_uint32_add_unsigned_unsigned
#check_size_t_mul = check_uint32_mul_unsigned_unsigned
#   #end

class CFKeyedArchiverUID(object):
    def __init__(self, value):  #, base):
        # self.base = base
        self.value = value

    def copy_description(self):
        return "<CFKeyedArchiverUID {0:#x} [{1:#x}]>{value = {2}}".format(
            id(self),
            0,  # CFGetAllocator(self)
            self.value
        )

    def copy_formatting_description(self, format_options):
        return "@{0}@".format(self.value)

    CFKeyedArchiverUIDClass = [
        0,
        "CFKeyedArchiverUID",
        None,  # init
        None,  # copy
        None,  # finalize
        None,  # equal -- pointer equality only
        None,  # hash -- pointer hashing only
        copy_formatting_description,
        copy_description,
    ]

    # CFTypeID -- use type(obj) instead

# class CFBinaryPlistWriteBuffer(object):  # replaced with Python stream

# HEADER
#   magic number ("bplist")
#   file format version

# OBJECT TABLE
#   variable-sized objects

#   Object Formats (marker byte followed by additional info in some cases)
#   null  0000 0000
#   bool  0000 1000     // false
#   bool  0000 1001     // true
#   fill  0000 1111     // fill byte
#   int 0001 nnnn ...   // # of bytes is 2^nnnn, big-endian bytes
#   real  0010 nnnn ...   // # of bytes is 2^nnnn, big-endian bytes
#   date  0011 0011 ...   // 8 byte float follows, big-endian bytes
#   data  0100 nnnn [int] ... // nnnn is number of bytes unless 1111 then int count follows, followed by bytes
#   string  0101 nnnn [int] ... // ASCII string, nnnn is # of chars, else 1111 then int count, then bytes
#   string  0110 nnnn [int] ... // Unicode string, nnnn is # of chars, else 1111 then int count, then big-endian 2-byte uint16_t
#     0111 xxxx     // unused
#   uid 1000 nnnn ...   // nnnn+1 is # of bytes
#     1001 xxxx     // unused
#   array 1010 nnnn [int] objref* // nnnn is count, unless '1111', then int count follows
#     1011 xxxx     // unused
#   set 1100 nnnn [int] objref* // nnnn is count, unless '1111', then int count follows
#   dict  1101 nnnn [int] keyref* objref* // nnnn is count, unless '1111', then int count follows
#     1110 xxxx     // unused
#     1111 xxxx     // unused

# OFFSET TABLE
#   list of ints, byte size of which is given in trailer
#   -- these are the byte offsets into the file
#   -- number of these is in the trailer

# TRAILER
#   byte size of offset ints in offset table
#   byte size of object refs in arrays and dicts
#   number of offsets in offset table (also is number of objects)
#   element # in offset table which is top level object
#   offset table offset

class BinaryPlistWriter(object):

    # http://opensource.apple.com/source/CF/CF-1153.18/ForFoundationOnly.h
    MarkerNull = 0x00
    MarkerFalse = 0x08
    MarkerTrue = 0x09
    MarkerFill = 0x0F
    MarkerInt = 0x10
    MarkerReal = 0x20
    MarkerDate = 0x33
    MarkerData = 0x40
    MarkerASCIIString = 0x50
    MarkerUnicode16String = 0x60
    MarkerUID = 0x80
    MarkerArray = 0xA0
    MarkerSet = 0xC0
    MarkerDict = 0xD0

    def __init__(self, plist, buffer):
        self.buffer = buffer
        self.plist = plist

    def append_int(self, i):
        if i <= UINT8_MAX:
            itype = 'B'
            marker = self.MarkerInt | 0
        else if i <= UINT16_MAX:
            itype = 'H'
            marker = self.MarkerInt | 1
        else if i <= UINT32_MAX:
            itype = 'I'
            marker = self.MarkerInt | 2
        else:
            itype = 'Q'
            marker = self.MarkerInt | 3
        self.buffer.write(struct.pack('<B' + itype, marker & UINT8_MAX, i))
        
    def append_uid(self, uid):
        i = uid.value
        if i <= UINT8_MAX:
            itype = 'B'
            marker = self.MarkerUID | 0
        else if i <= UINT16_MAX:
            itype = 'H'
            marker = self.MarkerUID | 1
        else if i <= UINT32_MAX:
            itype = 'I'
            marker = self.MarkerUID | 3
        else:
            itype = 'Q'
            marker = self.MarkerUID | 7
        self.buffer.write(struct.pack('<B' + itype, marker & UINT8_MAX, i))

    def append_string(self, s):
        ascii = s.encode('ascii', 'ignore')
        if len(s) == len(ascii):
            marker = self.MarkerASCIIString | (len(ascii)<15 ? len(ascii) : 0xf)
            bytes = struct.pack('<B' + str(len(ascii)) + 's', marker, s)
        else:
            utf = s.encode('utf16')
            marker = self.MarkerUnicode16String | (len(s)<15 ? len(s) : 0xf)
            bytes = struct.pack('<B' + str(len(s)))
