#!/usr/bin/env python3
from typing import Optional

from ObjectsGroupCounter import ObjectsGroupCounter
from libs.SubCParser import SubCParser
from listeners.BinaryExpressionsListener import BinaryExpressionsListener


class BranchingListener(BinaryExpressionsListener):
    GOTO_TMPLT: str = 'out({}, true)'

    def __init__(self):
        super().__init__()
        self._ifs = ObjectsGroupCounter('_if', ['cond', 'end', 'var'])

    def _if(self, preceding: Optional[str], ctx: SubCParser.IfStatementContext,
            subsequent: Optional[str]) -> str:
        cond, end, var = self._ifs.next()
        goto_if_end = self.GOTO_TMPLT.format(end)
        branches = ctx.statement()
        then_br = self._tree[branches[0]] + ' ' + goto_if_end
        else_br = (self._tree[branches[1]] + ' ' if len(branches) > 1 else '') \
            + goto_if_end
        tvar = self._tvars.next()
        pre_statements = self._tree.get(ctx.expression(), '').strip()

        lines = [
            self.NEW_VAR_TMPLT.format(cond, 'channel'),
            self.NEW_VAR_TMPLT.format(end, 'channel'),
            '(('
        ]
        if preceding is not None:
            lines.append(preceding)
        if pre_statements:
            lines.append(pre_statements)
        lines.extend([
            f'out({cond}, {self._exprs.pop()}))',
            f'| (in({cond}, {var}: bool); if {var} then {then_br} else {else_br})',
            f'| (in({end}, {tvar}: bool);',
        ])
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
        self._just_concat_items(ctx, ctx.funCallItems(), ctx.ifBlockItems())
        return super().exitJustIfBlockItems(ctx)

    def exitNestedIfStatement(self, ctx: SubCParser.NestedIfStatementContext):
        self._tree[ctx] = self._if(None, ctx.ifStatement(), None)
        return super().exitNestedIfStatement(ctx)
