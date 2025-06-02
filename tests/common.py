#!/usr/bin/env python3
IDENTIFIERS = [ 'T', 'asdfadsfsdf', '____', 'Mtypes', '_', 'A', 'asdfkljdsfn',
    '_tmp8', 'message', 'client', 'server', 'ASF', 'Q', 'WFD2', 'x', 'port',
    'addr', 'field', 'PP9', '__qwerty__' ]

TESTS_TYPES = {
    '_Bool': 'bool',
    'bool': 'bool',
    'char': 'nat',
    'short': 'nat',
    'int': 'nat',
    'long': 'nat',
    'long long': 'nat',
    '__m128': 'nat',
    '__m128d': 'nat',
    '__m128i': 'nat',
    'enum _Enum': '_Enum',
    'struct _Struct': '_Struct',
    'union _Union': '_Union',
    'void*': 'bitstring',
    'const long*': 'bitstring',
    'int const*': 'bitstring',
    '_Bool***********************': 'bitstring',
    'enum _Enum* restrict': 'bitstring',
    'const short * const': 'bitstring',
    'struct _Struct const * const': 'bitstring',
}

SOME_IDENTIFIER = 's0m4__1DENT'
