from libs.SubCParser import SubCParser
from listeners.FieldedTypesListener import FieldedTypesListener


BUILTIN_TYPES = {
    'char': 'nat',
    'short': 'nat',
    'int': 'nat',
    'long': 'nat',
    '_Bool': 'bool',
    'bool': 'bool',
    'longlong': 'nat',
    '__m128': 'nat',
    '__m128d': 'nat',
    '__m128i': 'nat',
}


class TypesListener(FieldedTypesListener):
    def exitBuiltinType(self, ctx: SubCParser.BuiltinTypeContext):
        self._tree[ctx] = BUILTIN_TYPES[ctx.getText()]
        return super().exitBuiltinType(ctx)

    def exitTypeName(self, ctx: SubCParser.TypeNameContext):
        self._tree[ctx] = self._tree[ctx.getChild(0)]
        return super().exitTypeName(ctx)

    def exitTypeSpecifier(self, ctx: SubCParser.TypeSpecifierContext):
        type_ctx = ctx.typeName()
        self._tree[ctx] = 'bitstring' if type_ctx is None else self._tree[type_ctx]
        return super().exitTypeSpecifier(ctx)
