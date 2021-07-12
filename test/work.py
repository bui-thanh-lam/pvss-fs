# work.py
import ctypes
import os

# locating the 'libsample.so' file in the
# same directory as this file
_file = 'work_libsample.so'
_path = os.path.join("/home/lam-bui/Documents/Projects/ATTT/BTL/pvss-fs/test/work_libsample.so")
_mod = ctypes.cdll.LoadLibrary(_path)

# int gcd(int, int)
gcd = _mod.gcd
gcd.argtypes = (ctypes.c_int, ctypes.c_int)
gcd.restype = ctypes.c_int

# int divide(int, int, int *)
_divide = _mod.divide
_divide.argtypes = (ctypes.c_int, ctypes.c_int,
                    ctypes.POINTER(ctypes.c_int))

_divide.restype = ctypes.c_int


def divide(x, y):
    rem = ctypes.c_int()
    quot = _divide(x, y, rem)
    return quot, rem.value

# void avg(double *, int n)
# Define a special type for the 'double *' argument
class DoubleArrayType:
    def from_param(self, param):

        typename = type(param).__name__

        if hasattr(self, 'from_' + typename):
            return getattr(self, 'from_' + typename)(param)

        elif isinstance(param, ctypes.Array):
            return param

        else:
            raise TypeError("Can't convert % s" % typename)

    # Cast from array.array objects
    def from_array(self, param):
        if param.typecode != 'd':
            raise TypeError('must be an array of doubles')

        ptr, _ = param.buffer_info()
        return ctypes.cast(ptr, ctypes.POINTER(ctypes.c_double))

    # Cast from lists / tuples
    def from_list(self, param):
        val = ((ctypes.c_double) * len(param))(*param)
        return val

    from_tuple = from_list

    # Cast from a numpy array
    def from_ndarray(self, param):
        return param.ctypes.data_as(ctypes.POINTER(ctypes.c_double))


DoubleArray = DoubleArrayType()
_avg = _mod.avg
# _avg.argtypes = (DoubleArray, ctypes.c_int)
_avg.argtypes = (ctypes.POINTER(ctypes.c_double), ctypes.c_int)
_avg.restype = ctypes.c_double


def avg(values):
    return _avg(values, len(values))


# struct Point { }
class Point(ctypes.Structure):
    _fields_ = [('x', ctypes.c_double), ('y', ctypes.c_double)]


# double distance(Point *, Point *)
distance = _mod.distance
distance.argtypes = (ctypes.POINTER(Point), ctypes.POINTER(Point))
distance.restype = ctypes.c_double


# int printHello()
printHello = _mod.printHello
printHello = (ctypes.c_char_p)
printHello.restype = ctypes.c_void_p

# int funtionTestGmp()
functionTestGmp = _mod.functionTestGmp
functionTestGmp.restype = ctypes.c_void_p

# void printString(char *s)
printString = _mod.printString
printString.restype = ctypes.c_void_p

# void printStringArray(char **s, int n)
printStringArray = _mod.printStringArray
printStringArray.argtypes = (ctypes.POINTER(ctypes.c_char_p), ctypes.c_int)
printStringArray.restype = ctypes.c_void_p

print("gcd: ",gcd(35,42))
print("divide: ", divide(5,2))
# print("avg: ", avg([1, 2, 3]))
double_array = (ctypes.c_double * 4)(1,2,3,4)
print("avg: ", avg(double_array))
p1 = Point(1, 2)
p2 = Point(4, 5)
print("distance: ", distance(p1, p2))
printHello()
functionTestGmp()

printString("alô".encode("utf-8"))

stringArray = (ctypes.c_char_p * 4)("một".encode("utf-8"), "hai".encode("utf-8"), "ba".encode("utf-8"), "bốn".encode("utf-8"))
printStringArray(stringArray, 4)



