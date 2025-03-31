enum foo;

enum bar {
    A,
    B,
    C
};

enum baz {
    D = 0,
    E,
};

enum {
    F,
    G = 45,
};

/* Translated to:
type foo.
type baz.
const D,E: baz.
type bar.
const A,B,C: bar.
type anon_enum0.
const F,G: anon_enum0.
*/
