#!/usr/bin/env python3
from helpers import shadow_name


def const(name: str, type: str) -> str:
    return 'const ' + name + ': ' + type + '.'

def fun(name: str, args: list[str], ret: str,
        body: str = '') -> str:
    funcname = shadow_name(name)
    return 'fun {}({}): {}{}.'.format(funcname, ', '.join(args), ret,
                                      body.format(func=funcname))


GLOBALS = [
    const('NULL', 'bitstring'), # NULL
    fun('addressof', ('any_type'), 'bitstring'), # &a
    fun('deref', ('bitstring'), 'bitstring',
        '\n\treduc {func}(NULL) = fail'),        # *a
    fun('sizeof', ('any_type'), 'nat'),          # sizeof(a)
    fun('mul', ('nat', 'nat'), 'nat'),           # a * b
    fun('div', ('nat', 'nat'), 'nat'),           # a / b
    fun('mod', ('nat', 'nat'), 'nat'),           # a % b
    fun('shl', ('nat', 'nat'), 'nat'),           # a << b
    fun('shr', ('nat', 'nat'), 'nat'),           # a >> b
    fun('and', ('nat', 'nat'), 'nat'),           # a & b
    fun('xor', ('nat', 'nat'), 'nat'),           # a ^ b
    fun('or', ('nat', 'nat'), 'nat'),            # a | b
    fun('not', ('nat', 'nat'), 'nat'),           # ~a
    fun('ternary', ('bool', 'any_type', 'any_type'), 'any_type',
        '\n\treduc forall a: any_type, b: any_type; {func}(true, a, b) = a' + \
        '\n\totherwise forall a: any_type, b: any_type; {func}(false, a, b) = b')
]
