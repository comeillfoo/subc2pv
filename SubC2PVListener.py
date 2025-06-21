#!/usr/bin/env python3
from typing import Any

from libs.SubCParser import SubCParser
from listeners.ArraysListener import ArraysListener


class SubC2PVListener(ArraysListener):
    def __init__(self):
        super().__init__()

    def exitCompoundStatement(self, ctx: SubCParser.CompoundStatementContext):
        self._tree[ctx] = self._tree.get(ctx.loopBlockItems(), ['0'])
        return super().exitCompoundStatement(ctx)
