#!/usr/bin/env python3
from listeners.FunctionsListener import FunctionsListener


class VariablesListener(FunctionsListener):
    NEW_VAR_TMPLT: str = 'new {}: {};'

    def __init__(self):
        super().__init__()
        self._exprs: list[str] = []

    def exitNoInitializerVariable(self, ctx):
        self._tree[ctx] = self.NEW_VAR_TMPLT.format(str(ctx.Identifier()),
            self._tree[ctx.typeSpecifier()])
        return super().exitNoInitializerVariable(ctx)

    def exitObjectDeclarationVariable(self, ctx):
        self._tree[ctx] = self.NEW_VAR_TMPLT.format(str(ctx.Identifier()),
            self._tree[ctx.typeSpecifier()])
        self._exprs.pop()
        return super().exitObjectDeclarationVariable(ctx)

    # TODO: compound initializer variable declaration
