#!/usr/bin/env python3
from typing import Tuple, Optional, Any
import functools

from libs.SubCListener import SubCListener
from model import Model


def protect_from_redeclaration(function):
    def wrapper(self, ctx):
        fname = str(ctx.Identifier())
        if fname in self._functions:
            raise Exception(f'Function {fname} already defined/declared')
        function(self, ctx)
    return wrapper


def prepend_non_empty(line: str, cur: str) -> str:
    return ('' if not line else (line + '\n')) + cur

class SubC2PVListener(SubCListener):
    def __init__(self):
        super().__init__()
        self._tree: dict[Any, str] = {}
        self._exprs: dict[Any, str] = {}
        self._types_id = -1
        self._globals: list[str] = []
        self._functions: dict[str, str] = {}

        self._string_lits: dict[str, str] = {}
        self._string_lits_id = -1

        self._tmpvar_id = -1

    def exitEnumDeclaration(self, ctx):
        self._globals.append(f'type {str(ctx.Identifier())}.\n')
        return super().exitEnumDeclaration(ctx)

    def _new_enumeration(self, name: str, ctx) -> str:
        def _ctx2const(_ctx) -> str:
            return f'const {str(_ctx.Identifier())}: {name}.'
        lines = [f'type {name}.']
        lines.extend(map(_ctx2const, ctx.enumerator()))
        lines.append('\n')
        return '\n'.join(lines)

    def exitEnumDefinition(self, ctx):
        tname = str(ctx.Identifier())
        self._globals.append(self._new_enumeration(tname, ctx))
        return super().exitEnumDefinition(ctx)

    def exitStructOrUnionDeclaration(self, ctx):
        self._globals.append(f'type {str(ctx.Identifier())}.\n')
        return super().exitStructOrUnionDeclaration(ctx)

    def _new_fielded_type(self, name: str, ctx) -> str:
        def _ctx2field(_ctx) -> Tuple[str, str]:
            return (str(_ctx.Identifier()), self._tree[_ctx.typeSpecifier()])
        lines = [f'type {name}.', '']
        getter = 'fun _{name}_get_{fname}(self: {name}): {ftype}.'
        setter = 'fun _{name}_set_{fname}(self: {name}, {fname}: {ftype}): {name}.'
        params = []
        for fname, ftype in map(_ctx2field, ctx.field()):
            lines.append(getter.format(name=name, fname=fname, ftype=ftype))
            lines.append(setter.format(name=name, fname=fname, ftype=ftype))
            params.append(f'{fname}: {ftype}')
        lines.append(f'fun _{name}_init({", ".join(params)}): {name}.')
        return '\n'.join(lines)

    def exitStructOrUnionDefinition(self, ctx):
        tname = str(ctx.Identifier())
        self._globals.append(self._new_fielded_type(tname, ctx))
        return super().exitStructOrUnionDefinition(ctx)

    def _next_type_name(self) -> str:
        self._types_id += 1
        return f'_tmp{self._types_id}'

    def exitEnumType(self, ctx):
        is_anon = ctx.Identifier() is None
        tname = self._next_type_name() if is_anon else str(ctx.Identifier())
        self._tree[ctx] = tname
        if is_anon:
            self._globals.append(self._new_enumeration(tname, ctx))
        return super().exitEnumType(ctx)

    def exitStructOrUnionType(self, ctx):
        is_anon = ctx.Identifier() is None
        tname = self._next_type_name() if is_anon else str(ctx.Identifier())
        self._tree[ctx] = tname
        if is_anon:
            self._globals.append(self._new_fielded_type(tname, ctx))
        return super().exitStructOrUnionType(ctx)

    def exitBuiltinType(self, ctx):
        trans_table = {
            'char': 'nat',
            'short': 'nat',
            'int': 'nat',
            'long': 'nat',
            '_Bool': 'bool',
            'bool': 'bool',
            'longlong': 'nat',
            '__m128': 'nat',
            '__m128d': 'nat',
            '__m128i': 'nat',
        }
        self._tree[ctx] = trans_table[ctx.getText()]
        return super().exitBuiltinType(ctx)

    def exitTypeName(self, ctx):
        self._tree[ctx] = self._tree[ctx.getChild(0)]
        return super().exitTypeName(ctx)

    def exitTypeSpecifier(self, ctx):
        type_ctx = ctx.typeName()
        self._tree[ctx] = 'bitstring' if type_ctx is None else self._tree[type_ctx]
        return super().exitTypeSpecifier(ctx)

    def _funParams2pv(self, ctx: Any, anon: bool = False):
        params = {
            False: lambda types: zip(types, ctx.Identifier()),
            True: lambda types: map(lambda p: (p[1], f'p{p[0]}'), enumerate(types)),
        }
        _funParam2pv = lambda param: f'{param[1]}: {param[0]}'
        return ', '.join(map(_funParam2pv,
                             params[anon](map(self._tree.get, ctx.typeSpecifier()))))

    def exitFunctionParamsDefinition(self, ctx):
        self._tree[ctx] = self._funParams2pv(ctx)
        return super().exitFunctionParamsDefinition(ctx)

    def exitFunctionParamsDeclaration(self, ctx):
        self._tree[ctx] = self._tree.get(ctx.functionParamsDefinition(),
                                         self._funParams2pv(ctx, True))
        return super().exitFunctionParamsDeclaration(ctx)

    def _declare_function(self, ctx, is_void: bool = False) -> dict[str, str]:
        fname = str(ctx.Identifier())
        params = self._tree.get(ctx.functionParamsDeclaration(), '')
        return { fname: ('let {}({}) = 0.' if is_void else 'fun {}({}):') \
            .format(fname, params) }

    @protect_from_redeclaration
    def exitVoidFunctionDeclaration(self, ctx):
        self._functions.update(self._declare_function(ctx, True))
        return super().exitVoidFunctionDeclaration(ctx)

    protect_from_redeclaration
    def exitNonVoidFunctionDeclaration(self, ctx):
        name, body = self._declare_function(ctx).popitem()
        self._functions[name] = body + f' {self._tree[ctx.typeSpecifier()]}.'
        return super().exitNonVoidFunctionDeclaration(ctx)

    def _define_function(self, ctx, is_void: bool = False) -> dict[str, str]:
        fname = str(ctx.Identifier())
        params = self._tree.get(ctx.functionParamsDefinition(), '')
        if not is_void:
            params += f'{"" if not params else ", "}_ret_ch: channel'
        body: str = self._tree.get(ctx.compoundStatement(), '0').rstrip(';')
        if body.endswith(' in '):
            body += '0'
        return { fname: ('let {}({}) = {}.').format(fname, params, body) }

    def exitVoidFunctionDefinition(self, ctx):
        self._functions.update(self._define_function(ctx, True))
        return super().exitVoidFunctionDefinition(ctx)

    def exitNonVoidFunctionDefinition(self, ctx):
        self._functions.update(self._define_function(ctx))
        return super().exitNonVoidFunctionDefinition(ctx)

    def exitCompoundStatement(self, ctx):
        block_items = ctx.blockItem()
        self._tree[ctx] = '0' if block_items is None or not block_items \
            else '\n'.join(map(self._tree.get, filter(self._tree.__contains__,
                                                      block_items)))
        return super().exitCompoundStatement(ctx)

    def exitBlockItem(self, ctx):
        if ctx.statement() is not None:
            self._tree[ctx] = self._tree[ctx.statement()]
        elif ctx.variableDeclaration() is not None:
            self._tree[ctx] = self._tree[ctx.variableDeclaration()]
        return super().exitBlockItem(ctx)

    def exitNoInitializerVariable(self, ctx):
        var_name = str(ctx.Identifier())
        var_type = self._tree[ctx.typeSpecifier()]
        self._tree[ctx] = f'new {var_name}: {var_type};'
        return super().exitNoInitializerVariable(ctx)

    def exitObjectDeclarationVariable(self, ctx):
        var_name = str(ctx.Identifier())
        var_type = self._tree[ctx.typeSpecifier()]
        self._tree[ctx] = f'new {var_name}: {var_type};'
        return super().exitObjectDeclarationVariable(ctx)

    def exitStatement(self, ctx):
        self._tree[ctx] = self._tree[ctx.getChild(0)]
        return super().exitStatement(ctx)

    def _new_tmpvar(self) -> str:
        self._tmpvar_id += 1
        return f'_tmpvar{self._tmpvar_id}'

    def exitAssignmentOperator(self, ctx):
        op2tmplt = {
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
        self._tree[ctx] = op2tmplt[ctx.getText().rstrip('=')]
        return super().exitAssignmentOperator(ctx)

    def exitAssignmentStatement(self, ctx):
        expr = self._exprs[ctx.expression()]
        ident = str(ctx.Identifier())
        tmplt = self._tree[ctx.assignmentOperator()]
        lines = []
        if tmplt:
            tmpvar = self._new_tmpvar()
            lines.append(f'let {tmpvar} = ' + tmplt.format(ident, expr) + ' in ')
            expr = tmpvar
        lines.append(f'let {ident} = {expr} in ')
        self._tree[ctx] = prepend_non_empty(self._tree.get(ctx.expression(), ''),
                                            '\n'.join(lines))
        return super().exitAssignmentStatement(ctx)

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
        tmpvar = self._new_tmpvar()
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
        tmpvar = self._new_tmpvar()
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
        tmpvar = self._new_tmpvar()
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

    def exitExpression(self, ctx):
        self._pass2parent(ctx, ctx.getChild(0))
        return super().exitExpression(ctx)
