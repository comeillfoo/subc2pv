#!/usr/bin/env python3
from typing import Tuple, Iterable, Optional


Parameter = Tuple[str, str] # (type, name)


DEFAULT_COMMON_PREFIX = "u'" # u - utility


def list_pop_n(lst: list, n: int) -> list:
    ans = lst[-n:]
    del lst[-n:]
    return ans


def list_extended(acc: list, iterable: Iterable) -> list:
    acc.extend(iterable)
    return acc


def shadow_name(name: str, prefix: Optional[str] = DEFAULT_COMMON_PREFIX) -> str:
    return (prefix or DEFAULT_COMMON_PREFIX) + name
