#!/usr/bin/env python3


class ObjectsCounter:
    def __init__(self, prefix: str):
        self._counter = -1
        self._template = prefix + '%d'

    def next(self) -> str:
        self._counter += 1
        return self._template % self._counter

    def reset(self):
        self._counter = -1
