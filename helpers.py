#!/usr/bin/env python3
from typing import Tuple, Iterable

Parameter = Tuple[str, str] # (type, name)

def list_pop_n(lst: list, n: int) -> list:
    ans = lst[-n:]
    del lst[-n:]
    return ans


def list_extended(acc: list, iterable: Iterable) -> list:
    acc.extend(iterable)
    return acc
