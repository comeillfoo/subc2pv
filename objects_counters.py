#!/usr/bin/env python3
from typing import Optional

from helpers import shadow_name


class ObjectsCounter:
    def __init__(self, prefix: str, common_prefix: Optional[str] = None):
        self._counter = -1
        self._template = shadow_name(prefix + '%d', common_prefix)

    def next(self) -> str:
        self._counter += 1
        return self._template % self._counter

    def reset(self):
        self._counter = -1


class ObjectsGroupCounter:
    def __init__(self, group_prefix: str, groups: list[str],
                 common_prefix: Optional[str] = None):
        self._counter = -1
        self._groups = groups
        self._template = shadow_name(group_prefix + '_%s%d', common_prefix)

    def _format_group(self, group: str) -> str:
        return self._template % (group, self._counter)

    def next(self) -> list[str]:
        self._counter += 1
        return list(map(self._format_group, self._groups))

    def reset(self):
        self._counter = -1
