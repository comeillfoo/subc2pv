#!/usr/bin/env python3
from typing import Tuple, Optional, Any

from libs.SubCListener import SubCListener
from model import Model


def protect_from_redeclaration(function):
    def wrapper(self, ctx):
        fname = str(ctx.Identifier())
        if fname in self._functions:
            raise Exception(f'Function {fname} already defined/declared')
        function(self, ctx)
    return wrapper


class SubC2PVListener(SubCListener):
    def __init__(self):
        super().__init__()
        self._tree = {}
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
        sign: str = ctx.getText().rstrip('=')
        self._tree[ctx] = op2tmplt[sign]
        return super().exitAssignmentOperator(ctx)

    def exitAssignmentStatement(self, ctx):
        ident = str(ctx.Identifier())
        expr = self._tree[ctx.expression()]
        tmplt = self._tree[ctx.assignmentOperator()]
        lines = []
        if tmplt:
            tmpvar = self._new_tmpvar()
            lines.append(f'let {tmpvar} = ' + tmplt.format(ident, expr) + ' in ')
            expr = tmpvar
        lines.append(f'let {ident} = {expr} in ')
        self._tree[ctx] = '\n'.join(lines)
        return super().exitAssignmentStatement(ctx)

    def exitExpression(self, ctx):
        self._tree[ctx] = self._tree[ctx.getChild(0)]
        return super().exitExpression(ctx)

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
        self._tree[ctx] = self._new_string_literal(''.join(string_lits))
        return super().exitPrimaryExprStringLits(ctx)

    def exitPrimaryExprIdentifier(self, ctx):
        self._tree[ctx] = str(ctx.Identifier())
        return super().exitPrimaryExprIdentifier(ctx)

    def exitPrimaryExprConstant(self, ctx):
        # TODO: handle chars
        self._tree[ctx] = str(ctx.Constant())
        return super().exitPrimaryExprConstant(ctx)
