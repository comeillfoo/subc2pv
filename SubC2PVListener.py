#!/usr/bin/env python3
from typing import Any

from listeners.BinaryExpressionsListener import BinaryExpressionsListener


class SubC2PVListener(BinaryExpressionsListener):
    def __init__(self):
        super().__init__()

        self._if_id = -1
        self._loops_id = -1

    def _new_if(self, preceding: list[str], ctx: Any, subsequent: list[str]) -> str:
        branches = ctx.statement()

        self._if_id += 1
        if_cond = f'if_cond{self._if_id}'
        if_end = f'if_end{self._if_id}'
        cond = f'_cond{self._if_id}'
        lines = [
            f'new {if_cond}: channel;',
            f'new {if_end}: channel;',
            '(('
        ]
        lines.extend(preceding)
        cond_calc = self._tree.get(ctx.expression(), '').strip()
        if cond_calc:
            lines.append(cond_calc)

        goto_if_end = f'out({if_end}, true)'
        then_br = self._tree[branches[0]] + ' ' + goto_if_end
        else_br = (self._tree[branches[1]] + ' ' if len(branches) > 1 else '') \
            + goto_if_end
        lines.extend([
            f'out({if_cond}, {self._exprs[ctx.expression()]}))',
            f'| (in({if_cond}, {cond}: bool); if {cond} then {then_br} else {else_br})',
        ])

        tmpvar = self._tvars.next()
        lines.append(f'| (in({if_end}, {tmpvar}: bool);')
        lines.extend(subsequent)
        lines.append('))')
        return '\n'.join(lines)

    def exitIfNoSubsequentItems(self, ctx):
        self._tree[ctx] = self._new_if([self._tree[ctx.ifBlockItems()]],
                                       ctx.ifStatement(), [])
        return super().exitIfNoSubsequentItems(ctx)

    def exitIfNoPrecedingItems(self, ctx):
        self._tree[ctx] = self._new_if([], ctx.ifStatement(),
                                       [self._tree[ctx.ifBlockItems()]])
        return super().exitIfNoPrecedingItems(ctx)

    def exitIfBothItemsAround(self, ctx):
        preceding, subsequent = ctx.ifBlockItems()
        self._tree[ctx] = self._new_if([preceding], ctx.ifStatement(),
                                       [subsequent])
        return super().exitIfBothItemsAround(ctx)

    def exitIfNoItemsAround(self, ctx):
        self._tree[ctx] = self._new_if([], ctx.ifStatement(), [])
        return super().exitIfNoItemsAround(ctx)

    def exitJustIfBlockItems(self, ctx):
        block_items = [ctx.blockItem()]
        if_block_items = ctx.ifBlockItems()
        if if_block_items is not None:
            block_items.append(if_block_items)
        self._tree[ctx] = '\n'.join(map(self._tree.get,
                                        filter(self._tree.__contains__,
                                               block_items)))
        return super().exitJustIfBlockItems(ctx)

    def exitCompoundStatement(self, ctx):
        block_items = ctx.ifBlockItems()
        self._tree[ctx] = '0' if block_items is None else self._tree[block_items]
        return super().exitCompoundStatement(ctx)
