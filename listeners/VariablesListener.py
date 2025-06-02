#!/usr/bin/env python3
from listeners.FunctionsListener import FunctionsListener


NEW_VAR_TMPLT: str = 'new {}: {};'


class VariablesListener(FunctionsListener):

    def exitNoInitializerVariable(self, ctx):
        self._tree[ctx] = NEW_VAR_TMPLT.format(str(ctx.Identifier()),
            self._tree[ctx.typeSpecifier()])
        return super().exitNoInitializerVariable(ctx)

    def exitObjectDeclarationVariable(self, ctx):
        self._tree[ctx] = NEW_VAR_TMPLT.format(str(ctx.Identifier()),
            self._tree[ctx.typeSpecifier()])
        return super().exitObjectDeclarationVariable(ctx)

    # TODO: compound initializer variable declaration
