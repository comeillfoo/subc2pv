#!/usr/bin/env python3
from typing import Tuple, Optional, Any

from libs.SubCListener import SubCListener
from model import Model


class SubC2PVListener(SubCListener):
    def __init__(self):
        super().__init__()
        self._tree = {}
        self._types_id = -1
        self._globals = []
        self._functionsDeclarations = {}
        self._functionsDefinitions = {}

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
            return (str(_ctx.Identifier()), self._tree[_ctx.typeName()])
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

    def exitTypeName(self, ctx):
        self._tree[ctx] = self._tree[ctx.getChild(0)]
        return super().exitTypeName(ctx)

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
            '__m128': 'nat',
            '__m128d': 'nat',
            '__m128i': 'nat',
        }
        self._tree[ctx] = trans_table[ctx.getText()]
        return super().exitBuiltinType(ctx)

    def _funParams2pv(self, ctx: Any, anon: bool = False):
        params = {
            False: lambda types: zip(types, ctx.Identifier()),
            True: lambda types: map(lambda p: (f'p{p[0]}', p[1]), enumerate(types)),
        }
        _funParam2pv = lambda param: f'{param[1]}: {param[0]}'
        return ', '.join(map(_funParam2pv,
                             params[anon](map(self._tree.get, ctx.typeName()))))

    def exitFunctionParamsDefinition(self, ctx):
        self._tree[ctx] = self._funParams2pv(ctx)
        return super().exitFunctionParamsDefinition(ctx)

    def exitFunctionParamsDeclaration(self, ctx):
        self._tree[ctx] = self._tree.get(ctx.functionParamsDefinition(),
                                         self._funParams2pv(ctx, True))
        return super().exitFunctionParamsDeclaration(ctx)

    def exitVoidFunctionDeclaration(self, ctx):
        fname = str(ctx.Identifier())
        params = self._tree.get(ctx.functionParamsDeclaration(), '')
        self._functionsDeclarations[fname] = f'let {fname}({params}) = 0.'
        return super().exitVoidFunctionDeclaration(ctx)

    def exitNonVoidFunctionDeclaration(self, ctx):
        fname = str(ctx.Identifier())
        rtype = self._tree[ctx.typeName()]
        params = self._tree.get(ctx.functionParamsDeclaration(), '')
        self._functionsDeclarations[fname] = f'fun {fname}({params}): {rtype}.'
        return super().exitNonVoidFunctionDeclaration(ctx)
