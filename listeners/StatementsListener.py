#!/usr/bin/env python3
from typing import Any

from ObjectsCounter import ObjectsCounter
from libs.SubCParser import SubCParser
from listeners.VariablesListener import VariablesListener


ASSIGN_OPERATORS = {
    '*': '_mul({}, {})',
    '/': '_div({}, {})',
    '%': '_mod({}, {})',
    '+': '{} + {}',
    '-': '{} - {}',
    '<<': '_shl({}, {})',
    '>>': '_shr({}, {})',
    '&': '_and({}, {})',
    '^': '_xor({}, {})',
    '|': '_or({}, {})',
}


class StatementsListener(VariablesListener):
    def __init__(self):
        super().__init__()
        self._tvars = ObjectsCounter('_tvar')

    def exitStatement(self, ctx: SubCParser.StatementContext):
        self._tree[ctx] = self._tree[ctx.getChild(0)]
        return super().exitStatement(ctx)

    def exitBlockItem(self, ctx: SubCParser.BlockItemContext):
        child_ctx = ctx.statement() or ctx.variableDeclaration()
        if child_ctx is not None:
            self._tree[ctx] = self._tree[child_ctx]
        return super().exitBlockItem(ctx)

    def exitAssignmentExpression(self,
            ctx: SubCParser.AssignmentExpressionContext):
        ectx = ctx.expression()
        pre_statements = self._tree[ectx]
        source = self._exprs.pop()
        target = str(ctx.Identifier())
        op = ctx.assignmentOperator().getText().rstrip('=')

        lines = [] if not pre_statements else [pre_statements]
        if not op:
            lines.append(self.LET_PAT_TMPLT.format(target, source))
        else:
            tmplt = ASSIGN_OPERATORS[op]
            tmpvar = self._tvars.next()
            lines.extend([
                self.LET_PAT_TMPLT.format(tmpvar, tmplt.format(target, source)),
                self.LET_PAT_TMPLT.format(target, tmpvar)
            ])
        self._tree[ctx] = '\n'.join(lines)
        self._exprs.append(target)
        return super().exitAssignmentExpression(ctx)

    def exitAssignmentStatement(self,
            ctx: SubCParser.AssignmentStatementContext):
        self._exprs.pop()
        self._tree[ctx] = self._tree[ctx.assignmentExpression()]
        return super().exitAssignmentStatement(ctx)
