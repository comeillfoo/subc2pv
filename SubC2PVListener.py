#!/usr/bin/env python3
from typing import Any

from libs.SubCParser import SubCParser
from listeners.ArraysListener import ArraysListener


class SubC2PVListener(ArraysListener):
    def __init__(self):
        super().__init__()
        self._loops_id = -1

    def exitCompoundStatement(self, ctx: SubCParser.CompoundStatementContext):
        block_items = ctx.loopBlockItems()
        self._tree[ctx] = '0' if block_items is None else self._tree[block_items]
        return super().exitCompoundStatement(ctx)
