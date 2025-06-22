#!/usr/bin/env python3
from typing import Union, Iterable, Optional, Tuple, Any

from helpers import Parameter, list_pop_n
from libs.SubCParser import SubCParser
from listeners.EnumsListener import EnumsListener


GETTER_TEMPLATE = "fun u'{name}_get_{fname}({name}): {ftype}."
SETTER_TEMPLATE = "fun u'{name}_set_{fname}({name}, {ftype}): {name}."
INIT_TEMPLATE = "fun u'{name}_init({params}): {name}."


class StructOrUnion:
    CALL_GETTER: str = "u'{}_get_{}(%s)"
    CALL_SETTER: str = "u'{}_set_{}(%s, %s)"
    CALL_INIT: str = "u'{}_init(%s)"

    def __init__(self, name: str, fields: list[Parameter] = []):
        self.name = name
        self.initializer = self.CALL_INIT.format(name)
        self.init_params = []
        self.fields = fields.copy()

        self.field2itype: dict[str, Tuple[int, str]] = {}
        # self.getters: dict[str, str] = {}
        # self.setters: dict[str, str] = {}
        for ftype, fname in self.fields:
            self.field2itype[fname] = (len(self.init_params), ftype)
            self.init_params.append('{' + fname + '}')
            # self.getters[fname] = self.CALL_GETTER.format(self.name, fname)
            # self.setters[fname] = self.CALL_SETTER.format(self.name, fname)

    def add_field(self, field: Parameter):
        ftype, fname = field
        self.field2itype[fname] = (len(self.init_params), ftype)
        self.init_params.append('{' + fname + '}')
        # self.getters[fname] = self.CALL_GETTER.format(self.name, fname)
        # self.setters[fname] = self.CALL_SETTER.format(self.name, fname)

    def _init(self, kwargs: dict[str, str]) -> str:
        return self.initializer % (', '.join(self.init_params).format(**kwargs))

    def _set_defaults(self, kwargs: dict[str, str]):
        for _, fname in self.fields:
            if fname in kwargs:
                continue
            kwargs[fname] = '0' # TODO: set defaults based on field type

    def _set_via_initializers(self, kwargs: dict[str, str],
            lines: list[str], fields: list[SubCParser.FieldInitializerContext],
            listener: Any):
        i = 0
        for fctx, expr in zip(fields, list_pop_n(listener._exprs, len(fields))):
            ident_ctx = fctx.Identifier()
            _, fname = self.fields[i]
            if ident_ctx is not None:
                fname = str(ident_ctx)
            else:
                i += 1
            lines.extend(listener._tree.get(fctx.expression(), []))
            kwargs[fname] = expr

    def init(self, ctx: Optional[SubCParser.FieldInitializerListContext],
             listener: Any) -> str:
        kwargs = {}
        lines = []
        if ctx is not None:
            self._set_via_initializers(kwargs, lines, ctx.fieldInitializer(),
                                       listener)
        self._set_defaults(kwargs)
        lines.append(self._init(kwargs))
        return '\n'.join(lines)

    # def get_field(self, _self: str, field: str) -> str:
    #     return self.getters[field] % (_self)

    # def set_field(self, _self: str, field: str, value: str) -> str:
    #     return self.setters[field] % (_self, value)


def protect_from_redeclaration(function):
    def wrapper(self, ctx: SubCParser.StructOrUnionDeclarationContext):
        tname = str(ctx.Identifier())
        if tname in self._fielded_types:
            raise Exception(f'Struct/union {tname} already defined/declared.')
        function(self, ctx)
    return wrapper


def define_accessors(name: str, fname: str, ftype: str) -> Iterable[str]:
    yield GETTER_TEMPLATE.format(name=name, fname=fname, ftype=ftype)
    yield SETTER_TEMPLATE.format(name=name, fname=fname, ftype=ftype)


class FieldedTypesListener(EnumsListener):
    def __init__(self):
        super().__init__()
        self._fielded_types: dict[str, StructOrUnion] = {}

    @protect_from_redeclaration
    def exitStructOrUnionDeclaration(self,
            ctx: SubCParser.StructOrUnionDeclarationContext):
        tname = str(ctx.Identifier())
        self._globals.append(f'type {tname}.')
        self._fielded_types[tname] = StructOrUnion(tname)
        return super().exitStructOrUnionDeclaration(ctx)

    def _field2tuple(self, ctx: SubCParser.FieldContext) -> Parameter:
        return (self._tree[ctx.typeSpecifier()], str(ctx.Identifier()))

    def _define_fielded_type(self, name: str,
            ctx: Union[SubCParser.StructOrUnionDefinitionContext,
                       SubCParser.StructOrUnionTypeContext]) -> list[str]:
        lines = [f'type {name}.']
        types = []
        fields = []
        for ftype, fname in map(self._field2tuple, ctx.field()):
            lines.extend(define_accessors(name, fname, ftype))
            types.append(ftype)
            fields.append((ftype, fname))

        lines.append(INIT_TEMPLATE.format(name=name, params=', '.join(types)))
        self._fielded_types[name] = StructOrUnion(name, fields)
        return lines

    def exitStructOrUnionDefinition(self,
            ctx: SubCParser.StructOrUnionDefinitionContext):
        name = str(ctx.Identifier())
        self._globals.extend(self._define_fielded_type(name, ctx))
        return super().exitStructOrUnionDefinition(ctx)

    def exitStructOrUnionType(self, ctx: SubCParser.StructOrUnionTypeContext):
        ident_ctx = ctx.Identifier()
        is_anon = ident_ctx is None
        name = self._anon_types.next() if is_anon else str(ctx.Identifier())
        self._tree[ctx] = name
        if is_anon: self._globals.extend(self._define_fielded_type(name, ctx))
        return super().exitStructOrUnionType(ctx)
