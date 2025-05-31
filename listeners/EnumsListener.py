#!/usr/bin/env python3
from typing import Any

from libs.SubCListener import SubCListener
from libs.SubCParser import SubCParser
from ObjectsCounter import ObjectsCounter


def enumerators2consts(enumeration: str):
    def enumerator2const(ctx: SubCParser.EnumeratorContext) -> str:
        return f'const {str(ctx.Identifier())}: {enumeration}.'
    return enumerator2const


def define_enumeration(name: str,
                       ctx: SubCParser.EnumDefinitionContext) -> list[str]:
    lines = [f'type {name}.']
    lines.extend(map(enumerators2consts(name), ctx.enumerator()))
    return lines


class EnumsListener(SubCListener):
    def __init__(self):
        super().__init__()
        self._tree: dict[Any, str] = {}
        self._globals: list[str] = []
        self._anon_types = ObjectsCounter('_anon_t')

    def exitEnumDeclaration(self, ctx: SubCParser.EnumDeclarationContext):
        self._globals.append(f'type {str(ctx.Identifier())}.')
        return super().exitEnumDeclaration(ctx)

    def exitEnumDefinition(self, ctx: SubCParser.EnumDefinitionContext):
        name = str(ctx.Identifier())
        self._globals.extend(define_enumeration(name, ctx))
        return super().exitEnumDefinition(ctx)

    def exitEnumType(self, ctx: SubCParser.EnumTypeContext):
        ident_ctx = ctx.Identifier()
        is_anon = ident_ctx is None
        name = self._anon_types.next() if is_anon else str(ident_ctx)
        self._tree[ctx] = name
        if is_anon: self._globals.extend(define_enumeration(name, ctx))
        return super().exitEnumType(ctx)
