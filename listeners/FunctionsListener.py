from typing import Union, Iterable, Optional, Any
from functools import reduce

from helpers import Parameter, list_pop_n, list_extended, shadow_name
from objects_counters import ObjectsGroupCounter
from libs.SubCParser import SubCParser
from listeners.StatementsListener import StatementsListener


FunctionParamsContexts = Union[SubCParser.FunctionParamsDefinitionContext,
                               SubCParser.FunctionParamsDeclarationContext]
FunctionDeclarationContexts = Union[SubCParser.VoidFunctionDeclarationContext,
                                    SubCParser.NonVoidFunctionDeclarationContext]
FunctionDefinitionContexts = Union[SubCParser.VoidFunctionDefinitionContext,
                                   SubCParser.NonVoidFunctionDefinitionContext]


FUN_TMPLT: str = 'fun {}({}): {}.'
FUN_MACRO_TMPLT: str = 'let {}({}) = {}.'


def anonymous_args(types: Iterable[str]) -> Iterable[Parameter]:
    return [(_type, shadow_name(f'p{i}')) for i, _type in enumerate(types)]

def arg2pv(param: Parameter) -> str:
    _type, name = param
    return name + ': ' + _type

def protect_from_redeclaration(function):
    def wrapper(self, ctx: FunctionDeclarationContexts):
        fname = str(ctx.Identifier())
        if fname in self._functions:
            raise Exception(f'Function {fname} already defined/declared.')
        function(self, ctx)
    return wrapper


class FunctionsListener(StatementsListener):
    GOTO_TMPLT: str = 'out({}, true)'

    def __init__(self):
        super().__init__()
        self._functions: dict[str, str] = {}
        self._fcalls = ObjectsGroupCounter('fcall', ['begin', 'end'])
        # TODO: maybe need for '_fcall_ret%i'

    def exitFunctionParamDefinition(self,
            ctx: SubCParser.FunctionParamDefinitionContext):
        _type = self._tree[ctx.typeSpecifier()] if ctx.arraySpecifier() is None \
            else 'bitstring'
        self._tree[ctx] = (_type, str(ctx.Identifier()))
        return super().exitFunctionParamDefinition(ctx)

    def exitFunctionParamsDefinition(self,
            ctx: SubCParser.FunctionParamsDefinitionContext):
        self._tree[ctx] = list(map(self._tree.get,
                                   ctx.functionParamDefinition()))
        return super().exitFunctionParamsDefinition(ctx)

    def exitFunctionParamDeclaration(self,
            ctx: SubCParser.FunctionParamDeclarationContext):
        if ctx.arraySpecifier() is None:
            self._tree[ctx] = self._tree[ctx.typeSpecifier()]
        else:
            self._tree[ctx] = 'bitstring'
        return super().exitFunctionParamDeclaration(ctx)

    def exitFunctionParamsDeclaration(self,
            ctx: SubCParser.FunctionParamsDeclarationContext):
        other_ctx = ctx.functionParamsDefinition()
        if other_ctx is None:
            self._tree[ctx] = anonymous_args(map(
                self._tree.get, ctx.functionParamDeclaration()))
        else:
            self._tree[ctx] = self._tree[other_ctx]
        return super().exitFunctionParamsDeclaration(ctx)

    @protect_from_redeclaration
    def exitVoidFunctionDeclaration(self,
            ctx: SubCParser.VoidFunctionDeclarationContext):
        name = str(ctx.Identifier())
        params = self._tree.get(ctx.functionParamsDeclaration(), [])
        params.append(('channel', "u'end"))
        params = ', '.join(map(arg2pv, params))
        self._functions[name] = FUN_MACRO_TMPLT.format(name, params,
                                                       "out(u'end, true)")
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
            params.append(('channel', "u'ret"))
        params.append(('channel', "u'end"))
        params = ', '.join(map(arg2pv, params))
        body = '\n'.join(self._tree[ctx.compoundStatement()]) \
            .removesuffix('0').rstrip(';')
        body += (' ' if not body or body.endswith(' in') else '; ') \
            + "out(u'end, true)"
        body = FUN_MACRO_TMPLT.format(name, params, body.strip())
        self._functions[name] = body

    def exitVoidFunctionDefinition(self,
            ctx: SubCParser.VoidFunctionDefinitionContext):
        self._define_function(ctx, True)
        return super().exitVoidFunctionDefinition(ctx)

    def exitNonVoidFunctionDefinition(self,
            ctx: SubCParser.NonVoidFunctionDefinitionContext):
        self._define_function(ctx)
        return super().exitNonVoidFunctionDefinition(ctx)

    def exitFunctionCall(self, ctx: SubCParser.FunctionCallContext):
        func = str(ctx.Identifier())
        ctxes = ctx.expression() or []
        args = ', '.join(list_pop_n(self._exprs, len(ctxes)))
        # TODO: consider order or statements
        lines = reduce(lambda acc, _ctx: \
                       list_extended(acc, self._tree.get(_ctx, [])), ctxes, [])
        lines.append(func + '(' + args + ')')
        self._tree[ctx] = lines
        return super().exitFunctionCall(ctx)

    def exitFunctionCallExpression(self,
            ctx: SubCParser.FunctionCallExpressionContext):
        target = self._tvars.next()
        # TODO: handle functions with definitions (process macros)
        lines = self._tree[ctx.functionCall()]
        lines[-1] = self.LET_PAT_TMPLT.format(target, lines[-1])
        self._tree[ctx] = lines
        self._exprs.append(target)
        return super().exitFunctionCallExpression(ctx)

    def exitFunCallStatement(self, ctx: SubCParser.FunCallStatementContext):
        lines = self._tree[ctx.functionCall()]
        # add end channel argument
        func, args = lines[-1].split('(')
        args = args.rstrip(')')
        lines[-1] = func + '(' + args + ('' if not args else ', ') + '{})'
        self._tree[ctx] = lines
        return super().exitFunCallStatement(ctx)

    def _funcall(self, preceding: list[str],
                 ctx: SubCParser.FunCallStatementContext,
                 subsequent: list[str]) -> str:
        begin, end = self._fcalls.next()
        tvar0 = self._tvars.next()
        tvar1 = self._tvars.next()
        fcall = self._tree[ctx]
        fcall[-1] = fcall[-1].format(end)

        lines = [
            self.NEW_VAR_TMPLT.format(begin, 'channel'),
            self.NEW_VAR_TMPLT.format(end, 'channel'),
            '(('
        ]
        if not (not preceding):
            lines.extend(preceding)
        lines.extend([f'out({begin}, true))',
                      f'| (in({begin}, {tvar0}: bool);'])
        lines.extend(fcall)
        lines.extend([')', f'| (in({end}, {tvar1}: bool);'])
        if not (not subsequent):
            lines.extend(subsequent)
        lines.append('))')
        return lines

    def exitFunCallNoSubsequentItems(self,
            ctx: SubCParser.FunCallNoSubsequentItemsContext):
        self._tree[ctx] = self._funcall(self._tree[ctx.funCallItems()],
                                        ctx.funCallStatement(), [])
        return super().exitFunCallNoSubsequentItems(ctx)

    def exitFunCallNoPrecedingItems(self,
            ctx: SubCParser.FunCallNoPrecedingItemsContext):
        self._tree[ctx] = self._funcall([], ctx.funCallStatement(),
                                        self._tree[ctx.funCallItems()])
        return super().exitFunCallNoPrecedingItems(ctx)

    def exitFunCallBothItemsAround(self,
            ctx: SubCParser.FunCallBothItemsAroundContext):
        preceding, subsequent = ctx.funCallItems()
        preceding, subsequent = self._tree[preceding], self._tree[subsequent]
        self._tree[ctx] = self._funcall(preceding, ctx.funCallStatement(),
                                        subsequent)
        return super().exitFunCallBothItemsAround(ctx)

    def exitFunCallNoItemsAround(self,
            ctx: SubCParser.FunCallNoItemsAroundContext):
        self._tree[ctx] = self._funcall([], ctx.funCallStatement(), [])
        return super().exitFunCallNoItemsAround(ctx)

    def _just_concat_items(self, ctx: Any, first: Any, next: Optional[Any]):
        items = [first] if next is None else [first, next]
        self._tree[ctx] = reduce(lambda acc, item: \
                                 list_extended(acc, self._tree.get(item, [])),
                                 items, [])

    def exitJustFunCallItems(self,
            ctx: SubCParser.JustFunCallItemsContext):
        self._just_concat_items(ctx, ctx.blockItem(), ctx.funCallItems())
        return super().exitJustFunCallItems(ctx)
