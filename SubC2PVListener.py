#!/usr/bin/env python3
from libs.SubCListener import SubCListener

from model import Model


class SubC2PVListener(SubCListener):
    def __init__(self):
        super().__init__()
        self.tree = {}
        self._model = Model()

    def model(self) -> Model:
        return self._model

    def exitCompilationUnit(self, ctx):
        self._model.preamble = '\n'.join(map(self.tree.get,
                                             ctx.declarationOrDefinition()))
        return super().exitCompilationUnit(ctx)

    def exitDeclarationOrDefinition(self, ctx):
        self.tree[ctx] = self.tree[ctx.getChild(0)]
        return super().exitDeclarationOrDefinition(ctx)

    def exitEnumDeclaration(self, ctx):
        self.tree[ctx] = f'type {str(ctx.Identifier())}.\n'
        return super().exitEnumDeclaration(ctx)

    def exitEnumDefinition(self, ctx):
        enum_t = str(ctx.Identifier())
        lines = [f'type {enum_t}.']
        lines.extend(map(lambda _ctx: self.tree[_ctx].format(enum_t),
                         ctx.enumerator()))
        lines.append('\n')
        self.tree[ctx] = '\n'.join(lines)
        return super().exitEnumDefinition(ctx)

    def exitEnumerator(self, ctx):
        self.tree[ctx] = f'const {str(ctx.Identifier())}: ' + '{}.'
        return super().exitEnumerator(ctx)

