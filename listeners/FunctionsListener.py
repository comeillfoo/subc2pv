from typing import Union, Iterable, Tuple

from libs.SubCParser import SubCParser
from listeners.TypesListener import TypesListener


FunctionParamsContexts = Union[SubCParser.FunctionParamsDefinitionContext,
                               SubCParser.FunctionParamsDeclarationContext]
FunctionDeclarationContexts = Union[SubCParser.VoidFunctionDeclarationContext,
                                    SubCParser.NonVoidFunctionDeclarationContext]
FunctionArg = Tuple[str, str]


def anonymous_args(types: Iterable[str]) -> Iterable[FunctionArg]:
    return [(f'_p{i}', _type) for i, _type in enumerate(types)]

def arg2pv(param: Tuple[str, str]) -> str:
    name, _type = param
    return name + ': ' + _type

def protect_from_redeclaration(function):
    def wrapper(self, ctx: FunctionDeclarationContexts):
        fname = str(ctx.Identifier())
        if fname in self._functions:
            raise Exception(f'Function {fname} already defined/declared.')
        function(self, ctx)
    return wrapper


class FunctionsListener(TypesListener):
    def __init__(self):
        super().__init__()
        self._functions: dict[str, str] = {}

    def _args2pv(self, ctx: FunctionParamsContexts,
                 is_anon: bool = True) -> str:
        types = map(self._tree.get, ctx.typeSpecifier())
        return ', '.join(map(arg2pv, anonymous_args(types) if is_anon \
                             else zip(map(str, ctx.Identifier()), types)))

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

    @protect_from_redeclaration
    def exitVoidFunctionDeclaration(self,
            ctx: SubCParser.VoidFunctionDeclarationContext):
        name = str(ctx.Identifier())
        params = self._tree.get(ctx.functionParamsDeclaration(), '')
        self._functions[name] = f'let {name}({params}) = 0.'
        return super().exitVoidFunctionDeclaration(ctx)

    @protect_from_redeclaration
    def exitNonVoidFunctionDeclaration(self,
            ctx: SubCParser.NonVoidFunctionDeclarationContext):
        name = str(ctx.Identifier())
        params = self._tree.get(ctx.functionParamsDeclaration(), '').strip()
        if params:
            params = ', '.join(map(lambda s: s.split(':')[1].strip(),
                                   params.split(',')))
        rettype = self._tree[ctx.typeSpecifier()]
        self._functions[name] = f'fun {name}({params}): {rettype}.'
        return super().exitNonVoidFunctionDeclaration(ctx)
