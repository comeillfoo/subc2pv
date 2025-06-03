#!/usr/bin/env python3
from libs.SubCParser import SubCParser
from listeners.UnaryExpressionsListener import UnaryExpressionsListener


class PostfixExpressionsListener(UnaryExpressionsListener):
    def exitFunctionCallExpression(self,
            ctx: SubCParser.FunctionCallExpressionContext):
        target = self._tvars.next()
        func = str(ctx.Identifier())
        ctxes = ctx.expression() or []
        args = ', '.join(map(self._exprs.get, ctxes)) # TODO: handle functions with definitions
        lines = list(map(self._tree.get, ctxes)) # TODO: consider order or statements
        lines.append(self.LET_PAT_TMPLT.format(target, func + '(' + args + ')'))
        self._tree[ctx] = '\n'.join(lines)
        self._exprs[ctx] = target
        return super().exitFunctionCallExpression(ctx)
