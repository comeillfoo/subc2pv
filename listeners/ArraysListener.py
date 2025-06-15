#!/usr/bin/env python3
from helpers import list_pop_n
from libs.SubCParser import SubCParser
from listeners.LoopsListener import LoopsListener


class ArraysListener(LoopsListener):
    def exitArraySpecifier(self, ctx: SubCParser.ArraySpecifierContext):
        list_pop_n(self._exprs, len(ctx.expression() or []))
        return super().exitArraySpecifier(ctx)

    def exitArrayInitializer(self, ctx: SubCParser.ArrayInitializerContext):
        list_pop_n(self._exprs, len(ctx.expression() or []))
        return super().exitArrayInitializer(ctx)
