#!/usr/bin/env python3
from typing import Tuple

from objects_counters import ObjectsCounter
from libs.SubCParser import SubCParser
from listeners.BinaryExpressionsListener import BinaryExpressionsListener


class BranchingListener(BinaryExpressionsListener):
    def __init__(self):
        super().__init__()
        self._ifs = ObjectsCounter('if_end')
        self._switches = ObjectsCounter('sw')
        self._cases = ObjectsCounter('case', '_')

    def _if(self, preceding: list[str], ctx: SubCParser.IfStatementContext,
            subsequent: list[str]) -> str:
        end = self._ifs.next()
        goto_if_end = self.GOTO_TMPLT.format(end)
        branches = ctx.statement()
        then_br = self._tree.get(branches[0], [])
        then_br.append(goto_if_end)
        else_br = self._tree.get(branches[1], []) if len(branches) > 1 else []
        else_br.append(goto_if_end)
        tvar = self._tvars.next()

        lines = [
            self.NEW_VAR_TMPLT.format(end, 'channel'),
            '(('
        ]
        lines.extend(preceding)
        lines.extend(self._tree.get(ctx.expression(), []))

        lines.extend([
            f'if {self._exprs.pop()} then'])
        lines.extend(then_br)
        lines.append('else')
        lines.extend(else_br)
        lines.extend([')', f'| (in({end}, {tvar}: bool);'])
        lines.extend(subsequent)
        lines.append('))')
        return lines

    def _case(self, ctx: SubCParser.CaseStatementContext, switch: str,
              next: str) -> Tuple[str, str, list[str], str]:
        expr_ctx = ctx.primaryExpression()
        is_default = expr_ctx is None
        label = switch + ('_default' if is_default else self._cases.next())

        selector = 'else ' \
            + ('' if is_default else 'if {expr} = ' + self._exprs.pop() + ' then ')
        selector += self.GOTO_TMPLT.format(label)

        body = ['| (in({}, {}: bool);'.format(label, self._tvars.next())]
        body.extend(self._tree.get(ctx.statement(), []))
        body.append(self.GOTO_TMPLT.format(next) + ')')
        return (label, selector, body, label)

    def _switch(self, preceding: list[str],
                ctx: SubCParser.SwitchStatementContext,
                subsequent: list[str]) -> str:
        self._cases.reset()
        sw = self._switches.next()
        end = sw + '_end'
        lines = [self.NEW_VAR_TMPLT.format(end, 'channel')]

        next = end
        selectors: list[str] = []
        cases: list[list[str]] = []
        for case in reversed(ctx.caseStatement()):
            label, selector, body, next = self._case(case, sw, next)
            lines.append(self.NEW_VAR_TMPLT.format(label, 'channel'))
            cases.append(body)
            selectors.append(selector)

        lines.append('((')
        lines.extend(preceding)
        lines.extend(self._tree.get(ctx.expression(), []))

        selectors[-1] = selectors[-1].removeprefix('else ')
        # has default branch?
        if not selectors[0].endswith(self.GOTO_TMPLT.format(sw + '_default')):
            selectors[0] += ' else ' + self.GOTO_TMPLT.format(end)
        selectors[0] += ')'
        lines.extend(selectors[::-1])
        for case in cases[::-1]:
            lines.extend(case)

        lines.append(f'| (in({end}, {self._tvars.next()}: bool);')
        lines.extend(subsequent)
        lines.append('))')
        return ('\n'.join(lines).format(expr=self._exprs.pop())).split('\n')

    def _branching(self, preceding: list[str],
                   ctx: SubCParser.BranchingStatementContext,
                   subsequent: list[str]) -> str:
        branching_ctx = ctx.ifStatement()
        if branching_ctx is not None:
            return self._if(preceding, branching_ctx, subsequent)
        branching_ctx = ctx.switchStatement()
        if branching_ctx is not None:
            return self._switch(preceding, branching_ctx, subsequent)
        raise NotImplementedError

    def exitBranchingNoSubsequentItems(self,
            ctx: SubCParser.BranchingNoSubsequentItemsContext):
        self._tree[ctx] = self._branching(self._tree[ctx.branchingItems()],
                                   ctx.branchingStatement(), [])
        return super().exitBranchingNoSubsequentItems(ctx)

    def exitBranchingNoPrecedingItems(self,
            ctx: SubCParser.BranchingNoPrecedingItemsContext):
        self._tree[ctx] = self._branching([], ctx.branchingStatement(),
                                   self._tree[ctx.branchingItems()])
        return super().exitBranchingNoPrecedingItems(ctx)

    def exitBranchingBothItemsAround(self,
            ctx: SubCParser.BranchingBothItemsAroundContext):
        preceding, subsequent = ctx.branchingItems()
        preceding, subsequent = self._tree[preceding], self._tree[subsequent]
        self._tree[ctx] = self._branching(preceding, ctx.branchingStatement(),
                                          subsequent)
        return super().exitBranchingBothItemsAround(ctx)

    def exitBranchingNoItemsAround(self,
            ctx: SubCParser.BranchingNoItemsAroundContext):
        self._tree[ctx] = self._branching([], ctx.branchingStatement(), [])
        return super().exitBranchingNoItemsAround(ctx)

    def exitJustBranchingItems(self, ctx: SubCParser.JustBranchingItemsContext):
        self._just_concat_items(ctx, ctx.funCallItems(), ctx.branchingItems())
        return super().exitJustBranchingItems(ctx)

    def exitNestedBranchingStatement(self,
            ctx: SubCParser.NestedBranchingStatementContext):
        self._tree[ctx] = self._branching([], ctx.branchingStatement(), [])
        return super().exitNestedBranchingStatement(ctx)
