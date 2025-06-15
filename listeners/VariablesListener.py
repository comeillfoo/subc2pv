#!/usr/bin/env python3
from libs.SubCParser import SubCParser
from listeners.TypesListener import TypesListener


class VariablesListener(TypesListener):
    NEW_VAR_TMPLT: str = 'new {}: {};'
    LET_PAT_TMPLT: str = 'let {} = {} in'

    def __init__(self):
        super().__init__()
        self._exprs: list[str] = []

    def exitNoInitializerVariable(self,
            ctx: SubCParser.NoInitializerVariableContext):
        self._tree[ctx] = self.NEW_VAR_TMPLT.format(str(ctx.Identifier()),
            self._tree[ctx.typeSpecifier()])
        return super().exitNoInitializerVariable(ctx)

    def exitObjectDeclarationVariable(self,
            ctx: SubCParser.ObjectDeclarationVariableContext):
        self._tree[ctx] = self.NEW_VAR_TMPLT.format(str(ctx.Identifier()),
            self._tree[ctx.typeSpecifier()])
        self._exprs.pop()
        return super().exitObjectDeclarationVariable(ctx)

    def _fielded_init(self, type_name: str,
            ctx: SubCParser.StructOrUnionInitializerContext) -> str:
        try:
            return self._fielded_types[type_name].init(
                ctx.fieldInitializerList(), self)
        except KeyError:
            raise Exception(f'No definition of struct/union named {type_name} found.')

    def _compound_init(self, type_name: str,
            ctx: SubCParser.CompoundInitializerContext) -> str:
        comp_ctx = ctx.structOrUnionInitializer()
        if comp_ctx is not None:
            return self._fielded_init(type_name, comp_ctx)
        raise NotImplementedError

    def exitCompoundInitializerVariable(self,
            ctx: SubCParser.CompoundInitializerVariableContext):
        tname = self._tree[ctx.typeSpecifier()]

        self._tree[ctx] = self.LET_PAT_TMPLT.format(str(ctx.Identifier()) \
            + ': ' + tname, self._compound_init(tname, ctx.compoundInitializer()))
        return super().exitCompoundInitializerVariable(ctx)
