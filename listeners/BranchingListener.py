#!/usr/bin/env python3
from typing import Optional, Tuple

from ObjectsCounter import ObjectsCounter
from libs.SubCParser import SubCParser
from listeners.BinaryExpressionsListener import BinaryExpressionsListener


class BranchingListener(BinaryExpressionsListener):
    GOTO_TMPLT: str = 'out({}, true)'
    CASE_TMPLT: str = '| (in({}, {}: bool); {} ' + GOTO_TMPLT + ')'

    def __init__(self):
        super().__init__()
        self._ifs = ObjectsCounter('_if_end')
        self._switches = ObjectsCounter('_sw')
        self._cases = ObjectsCounter('_case')

    def _if(self, preceding: Optional[str], ctx: SubCParser.IfStatementContext,
            subsequent: Optional[str]) -> str:
        end = self._ifs.next()
        goto_if_end = self.GOTO_TMPLT.format(end)
        branches = ctx.statement()
        then_br = self._tree[branches[0]] + ' ' + goto_if_end
        else_br = (self._tree[branches[1]] + ' ' if len(branches) > 1 else '') \
            + goto_if_end
        tvar = self._tvars.next()
        pre_statements = self._tree.get(ctx.expression(), '').strip()

        lines = [
            self.NEW_VAR_TMPLT.format(end, 'channel'),
            '(('
        ]
        if preceding is not None:
            lines.append(preceding)
        if pre_statements:
            lines.append(pre_statements)
        lines.extend([
            f'if {self._exprs.pop()} then {then_br} else {else_br})',
            f'| (in({end}, {tvar}: bool);',
        ])
        if subsequent is not None:
            lines.append(subsequent)
        lines.append('))')
        return '\n'.join(lines)

    def _case(self, ctx: SubCParser.CaseStatementContext, switch: str,
              next: str) -> Tuple[str, str, str, str]:
        expr_ctx = ctx.primaryExpression()
        is_default = expr_ctx is None
        label = switch + ('_default' if is_default else self._cases.next())

        selector = 'else ' \
            + ('' if is_default else 'if {expr} = ' + self._exprs.pop() + ' then ')
        selector += self.GOTO_TMPLT.format(label)

        return (label,
                selector,
                self.CASE_TMPLT.format(label, self._tvars.next(),
                                       self._tree[ctx.statement()], next),
                label)

    def _switch(self, preceding: Optional[str],
                ctx: SubCParser.SwitchStatementContext,
                subsequent: Optional[str]) -> str:
        self._cases.reset()
        sw = self._switches.next()
        end = sw + '_end'
        lines = [self.NEW_VAR_TMPLT.format(end, 'channel')]

        next = end
        selectors: list[str] = []
        cases: list[str] = []
        for case in reversed(ctx.caseStatement()):
            label, selector, body, next = self._case(case, sw, next)
            lines.append(self.NEW_VAR_TMPLT.format(label, 'channel'))
            cases.append(body)
            selectors.append(selector)

        lines.append('((')
        if preceding is not None:
            lines.append(preceding)
        pre_statements = self._tree.get(ctx.expression(), '').strip()
        if pre_statements:
            lines.append(pre_statements)

        selectors[-1] = selectors[-1].removeprefix('else ')
        # has default branch?
        if not selectors[0].endswith(self.GOTO_TMPLT.format(sw + '_default')):
            selectors[0] += ' else ' + self.GOTO_TMPLT.format(end)
        selectors[0] += ')'
        lines.extend(selectors[::-1])
        lines.extend(cases[::-1])

        lines.append(f'| (in({end}, {self._tvars.next()}: bool);')
        if subsequent is not None:
            lines.append(subsequent)
        lines.append('))')
        return '\n'.join(lines).format(expr=self._exprs.pop())

    def _branching(self, preceding: Optional[str],
                   ctx: SubCParser.BranchingStatementContext,
                   subsequent: Optional[str]) -> str:
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
                                   ctx.branchingStatement(), None)
        return super().exitBranchingNoSubsequentItems(ctx)

    def exitBranchingNoPrecedingItems(self,
            ctx: SubCParser.BranchingNoPrecedingItemsContext):
        self._tree[ctx] = self._branching(None, ctx.branchingStatement(),
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
        self._tree[ctx] = self._branching(None, ctx.branchingStatement(), None)
        return super().exitBranchingNoItemsAround(ctx)

    def exitJustBranchingItems(self, ctx: SubCParser.JustBranchingItemsContext):
        self._just_concat_items(ctx, ctx.funCallItems(), ctx.branchingItems())
        return super().exitJustBranchingItems(ctx)

    def exitNestedBranchingStatement(self,
            ctx: SubCParser.NestedBranchingStatementContext):
        self._tree[ctx] = self._branching(None, ctx.branchingStatement(), None)
        return super().exitNestedBranchingStatement(ctx)
