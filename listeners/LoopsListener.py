#!/usr/bin/env python3
from typing import Tuple, Optional

from ObjectsCounter import ObjectsCounter
from libs.SubCParser import SubCParser
from listeners.BranchingListener import BranchingListener


WHILE_TMPLTS = ('_while_begin', '_while_end', '_while_cond', '_while_var')
DOWHILE_TMPLTS = ('_dowhile_begin', '_dowhile_end', '_dowhile_cond',
                  '_dowhile_var')


def while_counters(counter: str) -> Tuple[str, str, str, str]:
    return tuple(map(lambda tmplt: tmplt + counter, WHILE_TMPLTS))

def dowhile_counters(counter: str) -> Tuple[str, str, str, str]:
    return tuple(map(lambda tmplt: tmplt + counter, DOWHILE_TMPLTS))


class LoopsListener(BranchingListener):
    def __init__(self):
        super().__init__()
        self._whiles = ObjectsCounter('')
        self._dowhiles = ObjectsCounter('')

    def _while(self, preceding: Optional[str],
               ctx: SubCParser.WhileStatementContext,
               subsequent: Optional[str]) -> str:
        begin, end, cond, var = while_counters(self._whiles.next())
        update_cond = 'out({}, {})'.format(cond, self._exprs.pop())
        enter_loop = self.GOTO_TMPLT.format(begin)
        exit_loop = self.GOTO_TMPLT.format(end)
        tvar0 = self._tvars.next()
        tvar1 = self._tvars.next()

        lines = [
            self.NEW_VAR_TMPLT.format(begin, 'channel'),
            self.NEW_VAR_TMPLT.format(end, 'channel'),
            self.NEW_VAR_TMPLT.format(cond, 'channel'),
            '(('
        ]
        if preceding is not None:
            lines.append(preceding)
        pre_statements = self._tree.get(ctx.expression(), '').strip()
        if pre_statements:
            lines.append(pre_statements)
        lines.extend([
            update_cond + ')',
            f'| !(in({cond}, {var}: bool); if {var} then {enter_loop} else {exit_loop})',
            f'| !(in({begin}, {tvar0}: bool); {self._tree[ctx.statement()]} {update_cond})',
            f'| (in({end}, {tvar1}: bool);'
        ])
        if subsequent is not None:
            lines.append(subsequent)
        lines.append('))')
        return '\n'.join(lines)

    def _dowhile(self, preceding: Optional[str],
               ctx: SubCParser.DoWhileStatementContext,
               subsequent: Optional[str]) -> str:
        begin, end, cond, var = dowhile_counters(self._dowhiles.next())
        update_cond = 'out({}, {})'.format(cond, self._exprs.pop())
        enter_loop = self.GOTO_TMPLT.format(begin)
        exit_loop = self.GOTO_TMPLT.format(end)
        tvar0 = self._tvars.next()
        tvar1 = self._tvars.next()

        lines = [
            self.NEW_VAR_TMPLT.format(begin, 'channel'),
            self.NEW_VAR_TMPLT.format(end, 'channel'),
            self.NEW_VAR_TMPLT.format(cond, 'channel'),
            '(('
        ]
        if preceding is not None:
            lines.append(preceding)
        pre_statements = self._tree.get(ctx.expression(), '').strip()
        if pre_statements:
            lines.append(pre_statements)
        lines.extend([
            f'out({cond}, true))',
            f'| !(in({cond}, {var}: bool); if {var} then {enter_loop} else {exit_loop})',
            f'| !(in({begin}, {tvar0}: bool); {self._tree[ctx.statement()]} {update_cond})',
            f'| (in({end}, {tvar1}: bool);'
        ])
        if subsequent is not None:
            lines.append(subsequent)
        lines.append('))')
        return '\n'.join(lines)

    def _loop(self, preceding: Optional[str],
               ctx: SubCParser.LoopStatementContext,
               subsequent: Optional[str]) -> str:
        loop_ctx = ctx.whileStatement()
        if loop_ctx is not None:
            return self._while(preceding, loop_ctx, subsequent)
        loop_ctx = ctx.doWhileStatement()
        if loop_ctx is not None:
            return self._dowhile(preceding, loop_ctx, subsequent)
        raise NotImplementedError

    def exitLoopNoSubsequentItems(self,
            ctx: SubCParser.LoopNoSubsequentItemsContext):
        self._tree[ctx] = self._loop(self._tree[ctx.loopBlockItems()],
                                     ctx.loopStatement(), None)
        return super().exitLoopNoSubsequentItems(ctx)

    def exitLoopNoPrecedingItems(self,
            ctx: SubCParser.LoopNoPrecedingItemsContext):
        self._tree[ctx] = self._loop(None, ctx.loopStatement(),
                                     self._tree[ctx.loopBlockItems()])
        return super().exitLoopNoPrecedingItems(ctx)

    def exitLoopBothItemsAround(self,
            ctx: SubCParser.LoopBothItemsAroundContext):
        preceding, subsequent = ctx.loopBlockItems()
        preceding, subsequent = self._tree[preceding], self._tree[subsequent]
        self._tree[ctx] = self._loop(preceding, ctx.loopStatement(), subsequent)
        return super().exitLoopBothItemsAround(ctx)

    def exitLoopNoItemsAround(self, ctx: SubCParser.LoopNoItemsAroundContext):
        self._tree[ctx] = self._loop(None, ctx.loopStatement(), None)
        return super().exitLoopNoItemsAround(ctx)

    def exitJustLoopBlockItems(self,
            ctx: SubCParser.JustLoopBlockItemsContext):
        items = [ctx.ifBlockItems()]
        loop_items = ctx.loopBlockItems()
        if loop_items is not None:
            items.append(loop_items)
        self._tree[ctx] = '\n'.join(map(self._tree.get,
                                        filter(self._tree.__contains__,
                                               items)))
        return super().exitJustLoopBlockItems(ctx)
