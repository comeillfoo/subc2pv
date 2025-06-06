#!/usr/bin/env python3
from typing import Tuple, Optional

from ObjectsCounter import ObjectsCounter
from libs.SubCParser import SubCParser
from listeners.BinaryExpressionsListener import BinaryExpressionsListener


IF_TMPLTS = ('_if_cond', '_if_end', '_if_var')


def if_counters(counter: str) -> Tuple[str, str, str]:
    return tuple(map(lambda tmplt: tmplt + counter, IF_TMPLTS))


class BranchingListener(BinaryExpressionsListener):
    GOTO_TMPLT: str = 'out({}, true)'

    def __init__(self):
        super().__init__()
        self._ifs = ObjectsCounter('')

    def _if(self, preceding: Optional[str], ctx: SubCParser.IfStatementContext,
            subsequent: Optional[str]) -> str:
        if_cond, if_end, cond = if_counters(self._ifs.next())
        expr = ctx.expression()
        lines = [
            self.NEW_VAR_TMPLT.format(if_cond, 'channel'),
            self.NEW_VAR_TMPLT.format(if_end, 'channel'),
            '(('
        ]
        if preceding is not None:
            lines.append(preceding)
        pre_statements = self._tree.get(expr, '').strip()
        if pre_statements:
            lines.append(pre_statements)

        goto_if_end = self.GOTO_TMPLT.format(if_end)
        branches = ctx.statement()
        then_br = self._tree[branches[0]] + ' ' + goto_if_end
        else_br = (self._tree[branches[1]] + ' ' if len(branches) > 1 else '') \
            + goto_if_end
        lines.extend([
            f'out({if_cond}, {self._exprs.pop()}))',
            f'| (in({if_cond}, {cond}: bool); if {cond} then {then_br} else {else_br})',
        ])

        tmpvar = self._tvars.next()
        lines.append(f'| (in({if_end}, {tmpvar}: bool);')
        if subsequent is not None:
            lines.append(subsequent)
        lines.append('))')
        return '\n'.join(lines)

    def exitIfNoSubsequentItems(self,
            ctx: SubCParser.IfNoSubsequentItemsContext):
        self._tree[ctx] = self._if(self._tree[ctx.ifBlockItems()],
                                   ctx.ifStatement(), None)
        return super().exitIfNoSubsequentItems(ctx)

    def exitIfNoPrecedingItems(self, ctx: SubCParser.IfNoPrecedingItemsContext):
        self._tree[ctx] = self._if(None, ctx.ifStatement(),
                                   self._tree[ctx.ifBlockItems()])
        return super().exitIfNoPrecedingItems(ctx)

    def exitIfBothItemsAround(self, ctx: SubCParser.IfBothItemsAroundContext):
        preceding, subsequent = ctx.ifBlockItems()
        preceding, subsequent = self._tree[preceding], self._tree[subsequent]
        self._tree[ctx] = self._if(preceding, ctx.ifStatement(), subsequent)
        return super().exitIfBothItemsAround(ctx)

    def exitIfNoItemsAround(self, ctx: SubCParser.IfNoItemsAroundContext):
        self._tree[ctx] = self._if(None, ctx.ifStatement(), None)
        return super().exitIfNoItemsAround(ctx)

    def exitJustIfBlockItems(self, ctx: SubCParser.JustIfBlockItemsContext):
        block_items = [ctx.blockItem()]
        if_block_items = ctx.ifBlockItems()
        if if_block_items is not None:
            block_items.append(if_block_items)
        self._tree[ctx] = '\n'.join(map(self._tree.get,
                                        filter(self._tree.__contains__,
                                               block_items)))
        return super().exitJustIfBlockItems(ctx)
