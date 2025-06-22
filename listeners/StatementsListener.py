#!/usr/bin/env python3
from helpers import shadow_name
from objects_counters import ObjectsCounter
from libs.SubCParser import SubCParser
from listeners.VariablesListener import VariablesListener


def call_binop(name: str) -> str:
    return shadow_name(name) + '({}, {})'


ASSIGN_OPERATORS = {
    '*':  call_binop('mul'),
    '/':  call_binop('div'),
    '%':  call_binop('mod'),
    '+':  '{} + {}',
    '-':  '{} - {}',
    '<<': call_binop('shl'),
    '>>': call_binop('shr'),
    '&':  call_binop('and'),
    '|':  call_binop('or'),
    '^':  call_binop('xor'),
}


class StatementsListener(VariablesListener):
    def __init__(self):
        super().__init__()
        self._tvars = ObjectsCounter('tvar')

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
        source = self._exprs.pop()
        target = str(ctx.Identifier())
        op = ctx.assignmentOperator().getText().rstrip('=')

        lines = self._tree.get(ectx, [])
        if not op:
            lines.append(self.LET_PAT_TMPLT.format(target, source))
        else:
            tmplt = ASSIGN_OPERATORS[op]
            tmpvar = self._tvars.next()
            lines.extend([
                self.LET_PAT_TMPLT.format(tmpvar, tmplt.format(target, source)),
                self.LET_PAT_TMPLT.format(target, tmpvar)
            ])
        self._tree[ctx] = lines
        self._exprs.append(target)
        return super().exitAssignmentExpression(ctx)

    def exitAssignmentStatement(self,
            ctx: SubCParser.AssignmentStatementContext):
        self._exprs.pop()
        self._tree[ctx] = self._tree[ctx.assignmentExpression()]
        return super().exitAssignmentStatement(ctx)

    def exitCompoundStatement(self, ctx: SubCParser.CompoundStatementContext):
        self._tree[ctx] = self._tree.get(ctx.loopBlockItems(), ['0'])
        return super().exitCompoundStatement(ctx)
