#!/usr/bin/env python3


class ObjectsGroupCounter:
    def __init__(self, group_prefix: str, groups: list[str]):
        self._counter = -1
        self._groups = groups
        self._template = group_prefix + '_%s%d'

    def _format_group(self, group: str) -> str:
        return self._template % (group, self._counter)

    def next(self) -> list[str]:
        self._counter += 1
        return list(map(self._format_group, self._groups))

    def reset(self):
        self._counter = -1
