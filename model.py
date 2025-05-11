#!/usr/bin/env python3
from typing import Tuple
from dataclasses import dataclass, field


FunctionModel = Tuple[str, str]

@dataclass
class Model:
    preamble: str = ''
    functions: list[FunctionModel] = field(default_factory=list)
