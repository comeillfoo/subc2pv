#!/usr/bin/env python3
from typing import Any, NamedTuple

from objects_counters import ObjectsCounter
from libs.SubCParser import SubCParser
from listeners.FunctionsListener import FunctionsListener


STRING_LIT_TMPLT: str = 'free {}: bitstring [private]. (* "{}" *)'
CASTER_NAME_TMPLT: str = '_cast2{}'
CASTER_TMPLT: str = 'fun {}(any_type): {}.'


def lit2str(literal: Any) -> str:
    return literal.getText().removeprefix('u8').removeprefix('u') \
        .removeprefix('U').removeprefix('L').removeprefix('"').removesuffix('"')


StringLiterals = NamedTuple('StringLiterals', strings=dict[str, str],
                            names=ObjectsCounter)


class UnaryExpressionsListener(FunctionsListener):
    TYPED_VAR_TMPLT: str = '{}: {}'

    def __init__(self):
        super().__init__()
        self._strlits = StringLiterals({}, ObjectsCounter('strlit'))
        self._casters: set[str] = set()

    def _declare_single_strlit(self, strlit: str) -> str:
        if strlit not in self._strlits.strings:
            global_name = self._strlits.names.next()
            self._strlits.strings[strlit] = global_name
            self._globals.append(STRING_LIT_TMPLT.format(global_name, strlit))
            return global_name
        return self._strlits.strings[strlit]

    def exitPrimaryExprStringLits(self,
            ctx: SubCParser.PrimaryExprStringLitsContext):
        # track string literals
        merged_strlits = ''
        for strlit in map(lit2str, ctx.StringLiteral()):
            _ = self._declare_single_strlit(strlit)
            merged_strlits += strlit
        self._exprs.append(self._declare_single_strlit(merged_strlits))
        return super().exitPrimaryExprStringLits(ctx)

    def exitPrimaryExprIdentifier(self,
            ctx: SubCParser.PrimaryExprIdentifierContext):
        self._exprs.append(str(ctx.Identifier()))
        return super().exitPrimaryExprIdentifier(ctx)

    def exitPrimaryExprConstant(self,
            ctx: SubCParser.PrimaryExprConstantContext):
        # TODO: handle chars
        self._exprs.append(str(ctx.Constant()))
        return super().exitPrimaryExprConstant(ctx)

    def _pass_state_to_parent(self, child: Any, parent: Any):
        self._tree[parent] = self._tree.get(child, [])

    def exitParenthesisExpression(self,
            ctx: SubCParser.ParenthesisExpressionContext):
        child_ctx = ctx.primaryExpression() or ctx.expression()
        if child_ctx is not None:
            self._pass_state_to_parent(child_ctx, ctx)
        return super().exitParenthesisExpression(ctx)

    def exitBasePostfixExpression(self,
            ctx: SubCParser.BasePostfixExpressionContext):
        self._pass_state_to_parent(ctx.parenthesisExpression(), ctx)
        return super().exitBasePostfixExpression(ctx)

    def _unary_expr(self, parent: Any, child: Any, rtype: str, tmplt: str):
        tvar = self._tvars.next()
        expr = self._exprs.pop()

        lines = self._tree.get(child, [])
        lines.append(self.LET_PAT_TMPLT.format(
            self.TYPED_VAR_TMPLT.format(tvar, rtype), tmplt.format(expr)))
        self._tree[parent] = lines
        self._exprs.append(tvar)

    def exitPostIncrementExpression(self,
            ctx: SubCParser.PostIncrementExpressionContext):
        self._unary_expr(ctx, ctx.postfixExpression(), 'nat', '{} + 1')
        return super().exitPostIncrementExpression(ctx)

    def exitPostDecrementExpression(self,
            ctx: SubCParser.PostDecrementExpressionContext):
        self._unary_expr(ctx, ctx.postfixExpression(), 'nat', '{} - 1')
        return super().exitPostDecrementExpression(ctx)

    def exitBaseUnaryExpression(self,
            ctx: SubCParser.BaseUnaryExpressionContext):
        self._pass_state_to_parent(ctx.postfixExpression(), ctx)
        return super().exitBaseUnaryExpression(ctx)

    def exitSizeofExpression(self, ctx: SubCParser.SizeofExpressionContext):
        self._unary_expr(ctx, ctx.unaryExpression(), 'nat', '_sizeof({})')
        return super().exitSizeofExpression(ctx)

    def exitLogicalNotExpression(self,
            ctx: SubCParser.LogicalNotExpressionContext):
        self._unary_expr(ctx, ctx.unaryExpression(), 'bool', 'not({})')
        return super().exitLogicalNotExpression(ctx)

    def exitBitwiseNotExpression(self,
            ctx: SubCParser.BitwiseNotExpressionContext):
        self._unary_expr(ctx, ctx.unaryExpression(), 'nat', '_not({})')
        return super().exitBitwiseNotExpression(ctx)

    def exitUnaryMinusExpression(self,
            ctx: SubCParser.UnaryMinusExpressionContext):
        self._unary_expr(ctx, ctx.unaryExpression(), 'nat', '0 - {}')
        return super().exitUnaryMinusExpression(ctx)

    def exitUnaryPlusExpression(self,
            ctx: SubCParser.UnaryPlusExpressionContext):
        self._unary_expr(ctx, ctx.unaryExpression(), 'nat', '0 + {}')
        return super().exitUnaryPlusExpression(ctx)

    def exitDereferenceExpression(self,
            ctx: SubCParser.DereferenceExpressionContext):
        self._unary_expr(ctx, ctx.unaryExpression(), 'bitstring', '_deref({})')
        return super().exitDereferenceExpression(ctx)

    def exitAddressOfExpression(self,
            ctx: SubCParser.AddressOfExpressionContext):
        self._unary_expr(ctx, ctx.unaryExpression(), 'bitstring',
                         '_addressof({})')
        return super().exitAddressOfExpression(ctx)

    def exitBaseCastExpression(self,
            ctx: SubCParser.BaseCastExpressionContext):
        self._pass_state_to_parent(ctx.unaryExpression(), ctx)
        return super().exitBaseCastExpression(ctx)

    def exitCast2TypeExpression(self,
            ctx: SubCParser.Cast2TypeExpressionContext):
        _type = self._tree[ctx.typeSpecifier()]
        caster = CASTER_NAME_TMPLT.format(_type)
        if caster not in self._casters:
            self._casters.add(caster)
            self._globals.append(CASTER_TMPLT.format(caster, _type))
        self._unary_expr(ctx, ctx.castExpression(), _type, caster + '({})')
        return super().exitCast2TypeExpression(ctx)
