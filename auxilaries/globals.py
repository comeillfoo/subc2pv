#!/usr/bin/env python3
from typing import Iterable

from helpers import shadow_name


def const(name: str, type: str) -> str:
    return 'const ' + name + ': ' + type + '.'

def fun(name: str, args: Iterable[str], ret: str,
        body: str = '') -> str:
    funcname = shadow_name(name)
    if ret == 'nat' and not body:
        raise Exception(f'The function {funcname} cannot be declared with' + \
                        f' \'{ret}\' as a return type')
    return 'fun {}({}): {}{}.'.format(funcname, ', '.join(args), ret,
                                      body.format(func=funcname))

def fun_binstub(name: str) -> str:
    return fun(name, ('nat', 'nat'), 'nat',
               '\n\treduc forall a, b: nat; {func}(a, b) = 0')

def fun_unostub(name: str, arg: str) -> str:
    return fun(name, (arg), 'nat',
               '\n\treduc forall a: ' + arg + '; {func}(a) = 0')

GLOBALS = [
    const('NULL', 'bitstring'), # NULL
    fun('addressof', ('any_type'), 'bitstring'), # &a
    fun('deref', ('bitstring'), 'bitstring',
        '\n\treduc {func}(NULL) = fail'),        # *a
    fun_unostub('sizeof', 'any_type'),           # sizeof(a)
    fun_binstub('mul'),                          # a * b
    fun_binstub('div'),                          # a / b
    fun_binstub('mod'),                          # a % b
    fun_binstub('shl'),                          # a << b
    fun_binstub('shr'),                          # a >> b
    fun_binstub('and'),                          # a & b
    fun_binstub('xor'),                          # a ^ b
    fun_binstub('or'),                           # a | b
    fun_unostub('not', 'nat'),                   # ~a
    fun('ternary', ('bool', 'any_type', 'any_type'), 'any_type',
        '\n\treduc forall a: any_type, b: any_type; {func}(true, a, b) = a' + \
        '\n\totherwise forall a: any_type, b: any_type; {func}(false, a, b) = b')
]
