#!/usr/bin/env python3
from libs.SubCParser import SubCParser
from listeners.UnaryExpressionsListener import UnaryExpressionsListener


class PostfixExpressionsListener(UnaryExpressionsListener):
    def exitFunctionCallExpression(self,
            ctx: SubCParser.FunctionCallExpressionContext):
        target = self._tvars.next()
        func = str(ctx.Identifier())
        ctxes = ctx.expression() or []
        # TODO: handle functions with definitions
        args = ', '.join([self._exprs.pop() for _ in range(len(ctxes))][::-1])
        # TODO: consider order or statements
        lines = list(filter(lambda c: not (not c),
                            map(lambda _ctx: self._tree.get(_ctx, ''), ctxes)))
        lines.append(self.LET_PAT_TMPLT.format(target, func + '(' + args + ')'))
        self._tree[ctx] = '\n'.join(lines)
        self._exprs.append(target)
        return super().exitFunctionCallExpression(ctx)
