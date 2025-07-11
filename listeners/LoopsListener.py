#!/usr/bin/env python3
from typing import Optional

from objects_counters import ObjectsGroupCounter
from libs.SubCParser import SubCParser
from listeners.BranchingListener import BranchingListener
from auxilaries.WhileLoopTranslator import WhileLoopTranslator
from auxilaries.DoWhileLoopTranslator import DoWhileLoopTranslator
from auxilaries.ForLoopTranslator import ForLoopTranslator


class LoopsListener(BranchingListener):
    def __init__(self):
        super().__init__()
        loops_groups = ['begin', 'end', 'cond', 'var']
        self._whiles = ObjectsGroupCounter('while', loops_groups)
        self._dowhiles = ObjectsGroupCounter('dowhile', loops_groups)
        self._fors = ObjectsGroupCounter('for', loops_groups)

    def _loop(self, preceding: list[str],
               ctx: SubCParser.LoopStatementContext,
               subsequent: list[str]) -> str:
        loop_ctx = ctx.whileStatement()
        if loop_ctx is not None:
            return WhileLoopTranslator.translate(preceding, loop_ctx,
                                                 subsequent, self)
        loop_ctx = ctx.doWhileStatement()
        if loop_ctx is not None:
            return DoWhileLoopTranslator.translate(preceding, loop_ctx,
                                                   subsequent, self)
        loop_ctx = ctx.forStatement()
        if loop_ctx is not None:
            return ForLoopTranslator.translate(preceding, loop_ctx,
                                               subsequent, self)
        raise NotImplementedError

    def exitLoopNoSubsequentItems(self,
            ctx: SubCParser.LoopNoSubsequentItemsContext):
        self._tree[ctx] = self._loop(self._tree[ctx.loopBlockItems()],
                                     ctx.loopStatement(), [])
        return super().exitLoopNoSubsequentItems(ctx)

    def exitLoopNoPrecedingItems(self,
            ctx: SubCParser.LoopNoPrecedingItemsContext):
        self._tree[ctx] = self._loop([], ctx.loopStatement(),
                                     self._tree[ctx.loopBlockItems()])
        return super().exitLoopNoPrecedingItems(ctx)

    def exitLoopBothItemsAround(self,
            ctx: SubCParser.LoopBothItemsAroundContext):
        preceding, subsequent = ctx.loopBlockItems()
        preceding, subsequent = self._tree[preceding], self._tree[subsequent]
        self._tree[ctx] = self._loop(preceding, ctx.loopStatement(), subsequent)
        return super().exitLoopBothItemsAround(ctx)

    def exitLoopNoItemsAround(self, ctx: SubCParser.LoopNoItemsAroundContext):
        self._tree[ctx] = self._loop([], ctx.loopStatement(), [])
        return super().exitLoopNoItemsAround(ctx)

    def exitJustLoopBlockItems(self,
            ctx: SubCParser.JustLoopBlockItemsContext):
        self._just_concat_items(ctx, ctx.branchingItems(), ctx.loopBlockItems())
        return super().exitJustLoopBlockItems(ctx)

    def exitNestedLoopStatement(self,
            ctx: SubCParser.NestedLoopStatementContext):
        self._tree[ctx] = self._loop([], ctx.loopStatement(), [])
        return super().exitNestedLoopStatement(ctx)
