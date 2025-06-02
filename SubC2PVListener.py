#!/usr/bin/env python3
from typing import Any
import functools

from listeners.StatementsListener import StatementsListener


def prepend_non_empty(line: str, cur: str) -> str:
    return ('' if not line else (line + '\n')) + cur


class ExpressionNode:
    def __init__(self, ctx, tracker):
        self.ctx = ctx
        self.expr = tracker._exprs[ctx]
        self.tree = tracker._tree.get(ctx, '')

class SubC2PVListener(StatementsListener):
    def __init__(self):
        super().__init__()
        self._exprs: dict[Any, str] = {}

        self._string_lits: dict[str, str] = {}
        self._string_lits_id = -1

        self._if_id = -1
        self._loops_id = -1

    def _new_string_literal(self, string: str) -> str:
        if string not in self._string_lits:
            self._string_lits_id += 1
            _global_name = f'_strlit{self._string_lits_id}'
            self._string_lits[string] = _global_name
            self._globals.append('free %s: bitstring [private]. (* "%s" *)' %
                                 (_global_name, string))
        return self._string_lits[string]

    def exitPrimaryExprStringLits(self, ctx):
        # track string literals
        def _to_string(node: Any) -> str:
            return str(node).removeprefix('u8').removeprefix('u').removeprefix('U') \
                .removeprefix('L').removeprefix('"').removesuffix('"')
        string_lits = list(map(_to_string, ctx.StringLiteral()))
        for string_lit in string_lits:
            self._new_string_literal(string_lit)
        self._exprs[ctx] = self._new_string_literal(''.join(string_lits))
        return super().exitPrimaryExprStringLits(ctx)

    def exitPrimaryExprIdentifier(self, ctx):
        self._exprs[ctx] = str(ctx.Identifier())
        return super().exitPrimaryExprIdentifier(ctx)

    def exitPrimaryExprConstant(self, ctx):
        # TODO: handle chars
        self._exprs[ctx] = str(ctx.Constant())
        return super().exitPrimaryExprConstant(ctx)

    def _pass2parent(self, ctx: Any, child_ctx: Any):
        self._exprs[ctx] = self._exprs[child_ctx]
        self._tree[ctx] = self._tree.get(child_ctx, '')

    def exitParenthesisExpression(self, ctx):
        if ctx.expression() is not None:
            self._pass2parent(ctx, ctx.expression())
        if ctx.primaryExpression() is not None:
            self._pass2parent(ctx, ctx.primaryExpression())
        return super().exitParenthesisExpression(ctx)

    def exitBasePostfixExpression(self, ctx):
        self._pass2parent(ctx, ctx.parenthesisExpression())
        return super().exitBasePostfixExpression(ctx)

    def _new_unary_expr(self, parent: Any, child: Any, tmplt: str):
        tmpvar = self._tvars.next()
        expr = self._exprs[child]
        self._tree[parent] = prepend_non_empty(self._tree.get(child, ''),
                                               tmplt % (tmpvar, expr))
        self._exprs[parent] = tmpvar

    def exitPostIncrementExpression(self, ctx):
        self._new_unary_expr(ctx, ctx.postfixExpression(),
                             'let %s: nat = %s + 1 in ')
        return super().exitPostIncrementExpression(ctx)

    def exitPostDecrementExpression(self, ctx):
        self._new_unary_expr(ctx, ctx.postfixExpression(),
                             'let %s: nat = %s - 1 in ')
        return super().exitPostDecrementExpression(ctx)

    def exitFunctionCallExpression(self, ctx):
        tmpvar = self._tvars.next()
        expressions = ctx.expression() or []
        prev = functools.reduce(prepend_non_empty,
                                map(lambda expr: self._tree.get(expr, ''),
                                    expressions), '')
        fun = str(ctx.Identifier())
        # TODO: handle functions with definitions
        params = ', '.join(map(self._exprs.get, expressions))
        self._tree[ctx] = prepend_non_empty(prev,
            f'let {tmpvar} = {fun}({params}) in ')
        self._exprs[ctx] = tmpvar
        return super().exitFunctionCallExpression(ctx)

    def exitBaseUnaryExpression(self, ctx):
        self._pass2parent(ctx, ctx.postfixExpression())
        return super().exitBaseUnaryExpression(ctx)

    def exitSizeofExpression(self, ctx):
        self._new_unary_expr(ctx, ctx.unaryExpression(),
                             'let %s: nat = _sizeof(%s) in ')
        return super().exitSizeofExpression(ctx)

    def exitLogicalNotExpression(self, ctx):
        self._new_unary_expr(ctx, ctx.unaryExpression(),
                             'let %s: bool = not(%s) in ')
        return super().exitLogicalNotExpression(ctx)

    def exitBitwiseNotExpression(self, ctx):
        self._new_unary_expr(ctx, ctx.unaryExpression(),
                             'let %s: nat = _not(%s) in ')
        return super().exitBitwiseNotExpression(ctx)

    def exitUnaryMinusExpression(self, ctx):
        self._new_unary_expr(ctx, ctx.unaryExpression(),
                             'let %s: nat = 0 - %s in ')
        return super().exitUnaryMinusExpression(ctx)

    def exitUnaryPlusExpression(self, ctx):
        self._new_unary_expr(ctx, ctx.unaryExpression(),
                             'let %s: nat = 0 + %s in ')
        return super().exitUnaryPlusExpression(ctx)

    def exitDereferenceExpression(self, ctx):
        self._new_unary_expr(ctx, ctx.unaryExpression(),
                             'let %s: bitstring = _deref(%s) in ')
        return super().exitDereferenceExpression(ctx)

    def exitAddressOfExpression(self, ctx):
        self._new_unary_expr(ctx, ctx.unaryExpression(),
                             'let %s: bitstring = _addressof(%s) in ')
        return super().exitAddressOfExpression(ctx)

    def exitBaseCastExpression(self, ctx):
        self._pass2parent(ctx, ctx.unaryExpression())
        return super().exitBaseCastExpression(ctx)

    def exitCast2TypeExpression(self, ctx):
        _type = self._tree[ctx.typeSpecifier()]
        self._globals.append(f'fun _cast2{_type}(any_type): {_type}.')
        self._new_unary_expr(ctx, ctx.castExpression(),
                             f'let %s: {_type} = _cast2{_type}(%s) in ')
        return super().exitCast2TypeExpression(ctx)

    def exitBaseMultiplicativeExpression(self, ctx):
        self._pass2parent(ctx, ctx.castExpression())
        return super().exitBaseMultiplicativeExpression(ctx)

    def _new_binary_expression(self, parent: Any, left: Any, right: Any,
                               tmplt: str):
        tmpvar = self._tvars.next()
        self._exprs[parent] = tmpvar
        lvar = self._exprs[left]
        rvar = self._exprs[right]
        lcode = self._tree.get(left, '')
        rcode = self._tree.get(right, '')
        code = tmplt.format(tmpvar, lvar, rvar)
        # TODO: consider order of prepends
        code = prepend_non_empty(lcode, code)
        code = prepend_non_empty(rcode, code)
        self._tree[parent] = code

    def exitModuloExpression(self, ctx):
        self._new_binary_expression(ctx, ctx.castExpression(),
                                    ctx.multiplicativeExpression(),
                                    'let {}: nat = _mod({}, {}) in ')
        return super().exitModuloExpression(ctx)

    def exitDivisionExpression(self, ctx):
        self._new_binary_expression(ctx, ctx.castExpression(),
                                    ctx.multiplicativeExpression(),
                                    'let {}: nat = _div({}, {}) in ')
        return super().exitDivisionExpression(ctx)

    def exitMultiplyExpression(self, ctx):
        self._new_binary_expression(ctx, ctx.castExpression(),
                                    ctx.multiplicativeExpression(),
                                    'let {}: nat = _mul({}, {}) in ')
        return super().exitMultiplyExpression(ctx)

    def exitBaseAdditiveExpression(self, ctx):
        self._pass2parent(ctx, ctx.multiplicativeExpression())
        return super().exitBaseAdditiveExpression(ctx)

    def exitSubtractionExpression(self, ctx):
        self._new_binary_expression(ctx, ctx.multiplicativeExpression(),
                                    ctx.additiveExpression(),
                                    'let {}: nat = {} - {} in ')
        return super().exitSubtractionExpression(ctx)

    def exitAdditionExpression(self, ctx):
        self._new_binary_expression(ctx, ctx.multiplicativeExpression(),
                                    ctx.additiveExpression(),
                                    'let {}: nat = {} + {} in ')
        return super().exitAdditionExpression(ctx)

    def exitBaseShiftExpression(self, ctx):
        self._pass2parent(ctx, ctx.additiveExpression())
        return super().exitBaseShiftExpression(ctx)

    def exitRightShiftExpression(self, ctx):
        self._new_binary_expression(ctx, ctx.additiveExpression(),
                                    ctx.shiftExpression(),
                                    'let {}: nat = _shr({}, {}) in ')
        return super().exitRightShiftExpression(ctx)

    def exitLeftShiftExpression(self, ctx):
        self._new_binary_expression(ctx, ctx.additiveExpression(),
                                    ctx.shiftExpression(),
                                    'let {}: nat = _shl({}, {}) in ')
        return super().exitLeftShiftExpression(ctx)

    def exitBaseRelationalExpression(self, ctx):
        self._pass2parent(ctx, ctx.shiftExpression())
        return super().exitBaseRelationalExpression(ctx)

    def exitGreaterOrEqualsExpression(self, ctx):
        self._new_binary_expression(ctx, ctx.shiftExpression(),
                                    ctx.relationalExpression(),
                                    'let {}: bool = {} >= {} in ')
        return super().exitGreaterOrEqualsExpression(ctx)

    def exitLessOrEqualsExpression(self, ctx):
        self._new_binary_expression(ctx, ctx.shiftExpression(),
                                    ctx.relationalExpression(),
                                    'let {}: bool = {} <= {} in ')
        return super().exitLessOrEqualsExpression(ctx)

    def exitGreaterThanExpression(self, ctx):
        self._new_binary_expression(ctx, ctx.shiftExpression(),
                                    ctx.relationalExpression(),
                                    'let {}: bool = {} > {} in ')
        return super().exitGreaterThanExpression(ctx)

    def exitLessThanExpression(self, ctx):
        self._new_binary_expression(ctx, ctx.shiftExpression(),
                                    ctx.relationalExpression(),
                                    'let {}: bool = {} < {} in ')
        return super().exitLessThanExpression(ctx)

    def exitBaseEqualityExpression(self, ctx):
        self._pass2parent(ctx, ctx.relationalExpression())
        return super().exitBaseEqualityExpression(ctx)

    def exitUnequalExpression(self, ctx):
        self._new_binary_expression(ctx, ctx.relationalExpression(),
                                    ctx.equalityExpression(),
                                    'let {}: bool = {} <> {} in ')
        return super().exitUnequalExpression(ctx)

    def exitEqualExpression(self, ctx):
        self._new_binary_expression(ctx, ctx.relationalExpression(),
                                    ctx.equalityExpression(),
                                    'let {}: bool = {} = {} in ')
        return super().exitEqualExpression(ctx)

    def exitBaseBitwiseExpression(self, ctx):
        self._pass2parent(ctx, ctx.equalityExpression())
        return super().exitBaseBitwiseExpression(ctx)

    def exitAndExpression(self, ctx):
        self._new_binary_expression(ctx, ctx.equalityExpression(),
                                    ctx.bitwiseExpression(),
                                    'let {}: nat = _and({}, {}) in ')
        return super().exitAndExpression(ctx)

    def exitExclusiveOrExpression(self, ctx):
        self._new_binary_expression(ctx, ctx.equalityExpression(),
                                    ctx.bitwiseExpression(),
                                    'let {}: nat = _xor({}, {}) in ')
        return super().exitExclusiveOrExpression(ctx)

    def exitInclusiveOrExpression(self, ctx):
        self._new_binary_expression(ctx, ctx.equalityExpression(),
                                    ctx.bitwiseExpression(),
                                    'let {}: nat = _or({}, {}) in ')
        return super().exitInclusiveOrExpression(ctx)

    def exitBaseLogicalAndExpression(self, ctx):
        self._pass2parent(ctx, ctx.bitwiseExpression())
        return super().exitBaseLogicalAndExpression(ctx)

    def exitConjuctionExpression(self, ctx):
        self._new_binary_expression(ctx, ctx.bitwiseExpression(),
                                    ctx.logicalAndExpression(),
                                    'let {}: bool = {} && {} in ')
        return super().exitConjuctionExpression(ctx)

    def exitBaseLogicalOrExpression(self, ctx):
        self._pass2parent(ctx, ctx.logicalAndExpression())
        return super().exitBaseLogicalOrExpression(ctx)

    def exitDisjunctionExpression(self, ctx):
        self._new_binary_expression(ctx, ctx.logicalAndExpression(),
                                    ctx.logicalOrExpression(),
                                    'let {}: bool = {} || {} in ')
        return super().exitDisjunctionExpression(ctx)

    def exitBaseConditionalExpression(self, ctx):
        self._pass2parent(ctx, ctx.logicalOrExpression())
        return super().exitBaseConditionalExpression(ctx)

    def exitTernaryExpression(self, ctx):
        cond = ExpressionNode(ctx.logicalOrExpression(), self)
        left = ExpressionNode(ctx.expression(), self)
        right = ExpressionNode(ctx.conditionalExpression(), self)

        tmpvar = self._tvars.next()
        self._exprs[ctx] = tmpvar

        code = f'let {tmpvar} = _ternary({cond.expr}, {left.expr}, {right.expr}) in '
        # TODO: consider order of prepends
        code = prepend_non_empty(cond.tree, code)
        code = prepend_non_empty(left.tree, code)
        code = prepend_non_empty(right.tree, code)
        self._tree[ctx] = code
        return super().exitTernaryExpression(ctx)

    def exitExpression(self, ctx):
        self._pass2parent(ctx, ctx.getChild(0))
        return super().exitExpression(ctx)

    def _new_if(self, preceding: list[str], ctx: Any, subsequent: list[str]) -> str:
        branches = ctx.statement()

        self._if_id += 1
        if_cond = f'if_cond{self._if_id}'
        if_end = f'if_end{self._if_id}'
        cond = f'_cond{self._if_id}'
        lines = [
            f'new {if_cond}: channel;',
            f'new {if_end}: channel;',
            '(('
        ]
        lines.extend(preceding)
        cond_calc = self._tree.get(ctx.expression(), '').strip()
        if cond_calc:
            lines.append(cond_calc)

        goto_if_end = f'out({if_end}, true)'
        then_br = self._tree[branches[0]] + ' ' + goto_if_end
        else_br = (self._tree[branches[1]] + ' ' if len(branches) > 1 else '') \
            + goto_if_end
        lines.extend([
            f'out({if_cond}, {self._exprs[ctx.expression()]}))',
            f'| (in({if_cond}, {cond}: bool); if {cond} then {then_br} else {else_br})',
        ])

        tmpvar = self._tvars.next()
        lines.append(f'| (in({if_end}, {tmpvar}: bool);')
        lines.extend(subsequent)
        lines.append('))')
        return '\n'.join(lines)

    def exitIfNoSubsequentItems(self, ctx):
        self._tree[ctx] = self._new_if([self._tree[ctx.ifBlockItems()]],
                                       ctx.ifStatement(), [])
        return super().exitIfNoSubsequentItems(ctx)

    def exitIfNoPrecedingItems(self, ctx):
        self._tree[ctx] = self._new_if([], ctx.ifStatement(),
                                       [self._tree[ctx.ifBlockItems()]])
        return super().exitIfNoPrecedingItems(ctx)

    def exitIfBothItemsAround(self, ctx):
        preceding, subsequent = ctx.ifBlockItems()
        self._tree[ctx] = self._new_if([preceding], ctx.ifStatement(),
                                       [subsequent])
        return super().exitIfBothItemsAround(ctx)

    def exitIfNoItemsAround(self, ctx):
        self._tree[ctx] = self._new_if([], ctx.ifStatement(), [])
        return super().exitIfNoItemsAround(ctx)

    def exitJustIfBlockItems(self, ctx):
        block_items = [ctx.blockItem()]
        if_block_items = ctx.ifBlockItems()
        if if_block_items is not None:
            block_items.append(if_block_items)
        self._tree[ctx] = '\n'.join(map(self._tree.get,
                                        filter(self._tree.__contains__,
                                               block_items)))
        return super().exitJustIfBlockItems(ctx)

    def exitCompoundStatement(self, ctx):
        block_items = ctx.ifBlockItems()
        self._tree[ctx] = '0' if block_items is None else self._tree[block_items]
        return super().exitCompoundStatement(ctx)
