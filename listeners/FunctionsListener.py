from typing import Union, Iterable, Tuple

from libs.SubCParser import SubCParser
from listeners.TypesListener import TypesListener


FunctionParamsContexts = Union[SubCParser.FunctionParamsDefinitionContext,
                               SubCParser.FunctionParamsDeclarationContext]
FunctionDeclarationContexts = Union[SubCParser.VoidFunctionDeclarationContext,
                                    SubCParser.NonVoidFunctionDeclarationContext]
FunctionDefinitionContexts = Union[SubCParser.VoidFunctionDefinitionContext,
                                   SubCParser.NonVoidFunctionDefinitionContext]
FunctionArg = Tuple[str, str]


FUN_TMPLT: str = 'fun {}({}): {}.'
FUN_MACRO_TMPLT: str = 'let {}({}) = {}.'


def anonymous_args(types: Iterable[str]) -> Iterable[FunctionArg]:
    return [(_type, f'_p{i}') for i, _type in enumerate(types)]

def arg2pv(param: Tuple[str, str]) -> str:
    _type, name = param
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

    def exitFunctionParamsDefinition(self,
            ctx: SubCParser.FunctionParamsDefinitionContext):
        self._tree[ctx] = list(zip(map(self._tree.get, ctx.typeSpecifier()),
                                   map(str, ctx.Identifier())))
        return super().exitFunctionParamsDefinition(ctx)

    def exitFunctionParamsDeclaration(self,
            ctx: SubCParser.FunctionParamsDeclarationContext):
        other_ctx = ctx.functionParamsDefinition()
        if other_ctx is None:
            self._tree[ctx] = anonymous_args(map(self._tree.get,
                                                 ctx.typeSpecifier()))
        else:
            self._tree[ctx] = self._tree[other_ctx]
        return super().exitFunctionParamsDeclaration(ctx)

    @protect_from_redeclaration
    def exitVoidFunctionDeclaration(self,
            ctx: SubCParser.VoidFunctionDeclarationContext):
        name = str(ctx.Identifier())
        params = ', '.join(map(arg2pv,
                               self._tree.get(ctx.functionParamsDeclaration(),
                                              [])))
        self._functions[name] = FUN_MACRO_TMPLT.format(name, params, '0')
        return super().exitVoidFunctionDeclaration(ctx)

    @protect_from_redeclaration
    def exitNonVoidFunctionDeclaration(self,
            ctx: SubCParser.NonVoidFunctionDeclarationContext):
        name = str(ctx.Identifier())
        params = ', '.join(map(lambda p: p[0],
                               self._tree.get(ctx.functionParamsDeclaration(),
                                              [])))
        rettype = self._tree[ctx.typeSpecifier()]
        self._functions[name] = FUN_TMPLT.format(name, params, rettype)
        return super().exitNonVoidFunctionDeclaration(ctx)

    def _define_function(self, ctx: FunctionDefinitionContexts,
                         is_void: bool = False):
        name = str(ctx.Identifier())
        params = self._tree.get(ctx.functionParamsDefinition(), [])
        if not is_void:
            params.append(('channel', '_ret_ch'))
        params = ', '.join(map(arg2pv, params))
        body: str = self._tree.get(ctx.compoundStatement(), '0').rstrip(';')
        if body.endswith(' in '):
            body += '0'
        body = FUN_MACRO_TMPLT.format(name, params, body)
        self._functions[name] = body

    def exitVoidFunctionDefinition(self,
            ctx: SubCParser.VoidFunctionDefinitionContext):
        self._define_function(ctx, True)
        return super().exitVoidFunctionDefinition(ctx)

    def exitNonVoidFunctionDefinition(self,
            ctx: SubCParser.NonVoidFunctionDefinitionContext):
        self._define_function(ctx)
        return super().exitNonVoidFunctionDefinition(ctx)
