#!/usr/bin/env python3
from typing import Any

from libs.SubCParser import SubCParser
from listeners.UnaryExpressionsListener import UnaryExpressionsListener


class BinaryExpressionsListener(UnaryExpressionsListener):
    def exitBaseMultiplicativeExpression(self,
            ctx: SubCParser.BaseMultiplicativeExpressionContext):
        self._pass_state_to_parent(ctx.castExpression(), ctx)
        return super().exitBaseMultiplicativeExpression(ctx)

    def _binary_expr(self, parent: Any, left: Any, right: Any, rtype: str,
                     tmplt: str):
        rarg, prer = self._exprs.pop(), self._tree.get(right, [])
        larg, prel = self._exprs.pop(), self._tree.get(left, [])
        # TODO: consider order of prepends
        lines = prer
        lines.extend(prel)

        target = self._tvars.next()
        lines.append(self.LET_PAT_TMPLT.format(
            self.TYPED_VAR_TMPLT.format(target, rtype),
            tmplt.format(larg, rarg)))
        self._tree[parent] = lines
        self._exprs.append(target)

    def exitModuloExpression(self, ctx: SubCParser.ModuloExpressionContext):
        self._binary_expr(ctx, ctx.castExpression(),
                          ctx.multiplicativeExpression(), 'nat', "u'mod({}, {})")
        return super().exitModuloExpression(ctx)

    def exitDivisionExpression(self, ctx: SubCParser.DivisionExpressionContext):
        self._binary_expr(ctx, ctx.castExpression(),
                          ctx.multiplicativeExpression(), 'nat', "u'div({}, {})")
        return super().exitDivisionExpression(ctx)

    def exitMultiplyExpression(self, ctx: SubCParser.MultiplyExpressionContext):
        self._binary_expr(ctx, ctx.castExpression(),
                          ctx.multiplicativeExpression(), 'nat', "u'mul({}, {})")
        return super().exitMultiplyExpression(ctx)

    def exitBaseAdditiveExpression(self,
            ctx: SubCParser.BaseAdditiveExpressionContext):
        self._pass_state_to_parent(ctx.multiplicativeExpression(), ctx)
        return super().exitBaseAdditiveExpression(ctx)

    def exitSubtractionExpression(self,
            ctx: SubCParser.SubtractionExpressionContext):
        self._binary_expr(ctx, ctx.multiplicativeExpression(),
                          ctx.additiveExpression(), 'nat', '{} - {}')
        return super().exitSubtractionExpression(ctx)

    def exitAdditionExpression(self, ctx: SubCParser.AdditionExpressionContext):
        self._binary_expr(ctx, ctx.multiplicativeExpression(),
                          ctx.additiveExpression(), 'nat', '{} + {}')
        return super().exitAdditionExpression(ctx)

    def exitBaseShiftExpression(self,
            ctx: SubCParser.BaseShiftExpressionContext):
        self._pass_state_to_parent(ctx.additiveExpression(), ctx)
        return super().exitBaseShiftExpression(ctx)

    def exitRightShiftExpression(self,
            ctx: SubCParser.RightShiftExpressionContext):
        self._binary_expr(ctx, ctx.additiveExpression(), ctx.shiftExpression(),
                          'nat', "u'shr({}, {})")
        return super().exitRightShiftExpression(ctx)

    def exitLeftShiftExpression(self,
            ctx: SubCParser.LeftShiftExpressionContext):
        self._binary_expr(ctx, ctx.additiveExpression(), ctx.shiftExpression(),
                          'nat', "u'shl({}, {})")
        return super().exitLeftShiftExpression(ctx)

    def exitBaseRelationalExpression(self,
            ctx: SubCParser.BaseRelationalExpressionContext):
        self._pass_state_to_parent(ctx.shiftExpression(), ctx)
        return super().exitBaseRelationalExpression(ctx)

    def exitGreaterOrEqualsExpression(self,
            ctx: SubCParser.GreaterOrEqualsExpressionContext):
        self._binary_expr(ctx, ctx.shiftExpression(),
                          ctx.relationalExpression(), 'bool', '{} >= {}')
        return super().exitGreaterOrEqualsExpression(ctx)

    def exitLessOrEqualsExpression(self,
            ctx: SubCParser.LessOrEqualsExpressionContext):
        self._binary_expr(ctx, ctx.shiftExpression(),
                          ctx.relationalExpression(), 'bool', '{} <= {}')
        return super().exitLessOrEqualsExpression(ctx)

    def exitGreaterThanExpression(self,
            ctx: SubCParser.GreaterThanExpressionContext):
        self._binary_expr(ctx, ctx.shiftExpression(),
                          ctx.relationalExpression(), 'bool', '{} > {}')
        return super().exitGreaterThanExpression(ctx)

    def exitLessThanExpression(self, ctx: SubCParser.LessThanExpressionContext):
        self._binary_expr(ctx, ctx.shiftExpression(),
                          ctx.relationalExpression(), 'bool', '{} < {}')
        return super().exitLessThanExpression(ctx)

    def exitBaseEqualityExpression(self,
            ctx: SubCParser.BaseEqualityExpressionContext):
        self._pass_state_to_parent(ctx.relationalExpression(), ctx)
        return super().exitBaseEqualityExpression(ctx)

    def exitUnequalExpression(self, ctx: SubCParser.UnequalExpressionContext):
        self._binary_expr(ctx, ctx.relationalExpression(),
                          ctx.equalityExpression(), 'bool', '{} <> {}')
        return super().exitUnequalExpression(ctx)

    def exitEqualExpression(self, ctx: SubCParser.EqualExpressionContext):
        self._binary_expr(ctx, ctx.relationalExpression(),
                          ctx.equalityExpression(), 'bool', '{} = {}')
        return super().exitEqualExpression(ctx)

    def exitBaseBitwiseExpression(self,
            ctx: SubCParser.BaseBitwiseExpressionContext):
        self._pass_state_to_parent(ctx.equalityExpression(), ctx)
        return super().exitBaseBitwiseExpression(ctx)

    def exitAndExpression(self, ctx: SubCParser.AndExpressionContext):
        self._binary_expr(ctx, ctx.equalityExpression(),
                          ctx.bitwiseExpression(), 'nat', "u'and({}, {})")
        return super().exitAndExpression(ctx)

    def exitExclusiveOrExpression(self,
            ctx: SubCParser.ExclusiveOrExpressionContext):
        self._binary_expr(ctx, ctx.equalityExpression(),
                          ctx.bitwiseExpression(), 'nat', "u'xor({}, {})")
        return super().exitExclusiveOrExpression(ctx)

    def exitInclusiveOrExpression(self,
            ctx: SubCParser.InclusiveOrExpressionContext):
        self._binary_expr(ctx, ctx.equalityExpression(),
                          ctx.bitwiseExpression(), 'nat', "u'or({}, {})")
        return super().exitInclusiveOrExpression(ctx)

    def exitBaseLogicalAndExpression(self,
            ctx: SubCParser.BaseLogicalAndExpressionContext):
        self._pass_state_to_parent(ctx.bitwiseExpression(), ctx)
        return super().exitBaseLogicalAndExpression(ctx)

    def exitConjuctionExpression(self,
            ctx: SubCParser.ConjuctionExpressionContext):
        self._binary_expr(ctx, ctx.bitwiseExpression(),
                          ctx.logicalAndExpression(), 'bool', '{} && {}')
        return super().exitConjuctionExpression(ctx)

    def exitBaseLogicalOrExpression(self,
            ctx: SubCParser.BaseLogicalOrExpressionContext):
        self._pass_state_to_parent(ctx.logicalAndExpression(), ctx)
        return super().exitBaseLogicalOrExpression(ctx)

    def exitDisjunctionExpression(self,
            ctx: SubCParser.DisjunctionExpressionContext):
        self._binary_expr(ctx, ctx.logicalAndExpression(),
                          ctx.logicalOrExpression(), 'bool', '{} || {}')
        return super().exitDisjunctionExpression(ctx)

    def exitBaseConditionalExpression(self,
            ctx: SubCParser.BaseConditionalExpressionContext):
        self._pass_state_to_parent(ctx.logicalOrExpression(), ctx)
        return super().exitBaseConditionalExpression(ctx)

    def exitTernaryExpression(self, ctx):
        cond = ctx.logicalOrExpression()
        left = ctx.expression()
        right = ctx.conditionalExpression()
        rarg, prer = self._exprs.pop(), self._tree.get(right, [])
        larg, prel = self._exprs.pop(), self._tree.get(left, [])
        carg, prec = self._exprs.pop(), self._tree.get(cond, [])

        # TODO: consider order of prepends
        lines = prec
        lines.extend(prel)
        lines.extend(prer)
        target = self._tvars.next()

        lines.append(self.LET_PAT_TMPLT.format(
            target, f"u'ternary({carg}, {larg}, {rarg})"))
        self._tree[ctx] = lines
        self._exprs.append(target)
        return super().exitTernaryExpression(ctx)

    def exitExpression(self, ctx):
        self._pass_state_to_parent(ctx.getChild(0), ctx)
        return super().exitExpression(ctx)
