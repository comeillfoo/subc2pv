#!/usr/bin/env python3
from typing import Any

from listeners.BranchingListener import BranchingListener


class SubC2PVListener(BranchingListener):
    def __init__(self):
        super().__init__()
        self._loops_id = -1

    def exitCompoundStatement(self, ctx):
        block_items = ctx.ifBlockItems()
        self._tree[ctx] = '0' if block_items is None else self._tree[block_items]
        return super().exitCompoundStatement(ctx)
