#!/usr/bin/env python3
from typing import Union, Iterable

from helpers import Parameter
from libs.SubCParser import SubCParser
from listeners.EnumsListener import EnumsListener


GETTER_TEMPLATE = 'fun _{name}_get_{fname}({name}): {ftype}.'
SETTER_TEMPLATE = 'fun _{name}_set_{fname}({name}, {ftype}): {name}.'
INIT_TEMPLATE = 'fun _{name}_init({params}): {name}.'


def define_accessors(name: str, fname: str, ftype: str) -> Iterable[str]:
    yield GETTER_TEMPLATE.format(name=name, fname=fname, ftype=ftype)
    yield SETTER_TEMPLATE.format(name=name, fname=fname, ftype=ftype)


class FieldedTypesListener(EnumsListener):
    def exitStructOrUnionDeclaration(self,
            ctx: SubCParser.StructOrUnionDeclarationContext):
        tname = str(ctx.Identifier())
        self._globals.append(f'type {tname}.')
        return super().exitStructOrUnionDeclaration(ctx)

    def _field2tuple(self, ctx: SubCParser.FieldContext) -> Parameter:
        return (self._tree[ctx.typeSpecifier()], str(ctx.Identifier()))

    def _define_fielded_type(self, name: str,
            ctx: Union[SubCParser.StructOrUnionDefinitionContext,
                       SubCParser.StructOrUnionTypeContext]) -> list[str]:
        lines = [f'type {name}.']
        types = []
        for ftype, fname in map(self._field2tuple, ctx.field()):
            lines.extend(define_accessors(name, fname, ftype))
            types.append(ftype)
        lines.append(INIT_TEMPLATE.format(name=name, params=', '.join(types)))
        return lines

    def exitStructOrUnionDefinition(self,
            ctx: SubCParser.StructOrUnionDefinitionContext):
        name = str(ctx.Identifier())
        self._globals.extend(self._define_fielded_type(name, ctx))
        return super().exitStructOrUnionDefinition(ctx)

    def exitStructOrUnionType(self, ctx: SubCParser.StructOrUnionTypeContext):
        ident_ctx = ctx.Identifier()
        is_anon = ident_ctx is None
        name = self._anon_types.next() if is_anon else str(ctx.Identifier())
        self._tree[ctx] = name
        if is_anon: self._globals.extend(self._define_fielded_type(name, ctx))
        return super().exitStructOrUnionType(ctx)
