#!/usr/bin/env python3
from typing import Tuple

Parameter = Tuple[str, str] # (type, name)

def list_pop_n(lst: list, n: int) -> list:
    ans = lst[-n:]
    del lst[-n:]
    return ans
