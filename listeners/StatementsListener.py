#!/usr/bin/env python3
from typing import Any

from ObjectsCounter import ObjectsCounter
from libs.SubCParser import SubCParser
from listeners.VariablesListener import VariablesListener


ASSIGN_OPERATORS = {
    '': '',
    '*': '_mul({}, {})',
    '/': '_div({}, {})',
    '%': '_mod({}, {})',
    '+': '{} + {}',
    '-': '{} - {}',
    '<<': '_shl({}, {})',
    '>>': '_shr({}, {})',
    '&': '_and({}, {})',
    '^': '_xor({}, {})',
    '|': '_or({}, {})'
}


class StatementsListener(VariablesListener):
    LET_PAT_TMPLT: str = 'let {} = {} in '

    def __init__(self):
        super().__init__()
        self._exprs: dict[Any, str] = {}
        self._tvars = ObjectsCounter('_tmpvar')

    def exitStatement(self, ctx: SubCParser.StatementContext):
        self._tree[ctx] = self._tree[ctx.getChild(0)]
        return super().exitStatement(ctx)

    def exitBlockItem(self, ctx: SubCParser.BlockItemContext):
        child_ctx = ctx.statement()
        if child_ctx is not None:
            self._tree[ctx] = self._tree[child_ctx]
            return super().exitBlockItem(ctx)

        child_ctx = ctx.variableDeclaration()
        if child_ctx is not None:
            self._tree[ctx] = self._tree[child_ctx]
        return super().exitBlockItem(ctx)

    def exitAssignmentStatement(self,
            ctx: SubCParser.AssignmentStatementContext):
        source = self._exprs[ctx.expression()]
        target = str(ctx.Identifier())
        op = ctx.assignmentOperator().getText().rstrip('=')
        if not op:
            self._tree[ctx] = self.LET_PAT_TMPLT.format(target, source)
            return super().exitAssignmentStatement(ctx)

        tmplt = ASSIGN_OPERATORS[op]
        tmpvar = self._tvars.next()
        self.tree[ctx] = '\n'.join([
            self.LET_PAT_TMPLT.format(tmpvar, tmplt.format(target, source)),
            self.LET_PAT_TMPLT.format(target, tmpvar)
        ])
        return super().exitAssignmentStatement(ctx)
