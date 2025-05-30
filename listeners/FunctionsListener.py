from typing import Union, Iterable, Tuple

from libs.SubCParser import SubCParser
from listeners.TypesListener import TypesListener


FunctionParamsContexts = Union[SubCParser.FunctionParamsDefinitionContext,
                               SubCParser.FunctionParamsDeclarationContext]
FunctionArg = Tuple[str, str]


def anonymous_args(types: Iterable[str]) -> Iterable[FunctionArg]:
    return [(f'_p{i}', _type) for i, _type in enumerate(types)]

def arg2pv(param: Tuple[str, str]) -> str:
    name, _type = param
    return name + ': ' + _type


class FunctionsListener(TypesListener):
    def _args2pv(self, ctx: FunctionParamsContexts,
                 is_anon: bool = True) -> str:
        types = map(self._tree.get, ctx.typeSpecifier())
        return ', '.join(map(arg2pv, anonymous_args(types) if is_anon \
                             else zip(types, ctx.Identifier())))

    def exitFunctionParamsDefinition(self,
            ctx: SubCParser.FunctionParamsDefinitionContext):
        self._tree[ctx] = self._args2pv(ctx, False)
        return super().exitFunctionParamsDefinition(ctx)

    def exitFunctionParamsDeclaration(self,
            ctx: SubCParser.FunctionParamsDeclarationContext):
        other_ctx = ctx.functionParamsDefinition()
        self._tree[ctx] = self._args2pv(ctx) if other_ctx is None \
            else self._tree[other_ctx]
        return super().exitFunctionParamsDeclaration(ctx)
