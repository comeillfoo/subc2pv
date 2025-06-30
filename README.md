# subc2pv

Network protocol implementations on C programming language translator.
Translates into network protocol specifications.

## Mapping Model Subset of SubC to Applied Pi Calculus. MMSC2APC

| SubC                                    | Applied Pi Calculus               |
| :-------------------------------------- | :-------------------------------- |
| `static int foo(...);`                  | `fun foo(ident1,...)/n`           |
| `extern int foo(...);`                  | `fun foo(...)/n`                  |
| `int a;`                                | `new a;`                          |
| `int a = 123;`                          | `new a;`                          |
| `int a = foo(...);`                     | `let a = in <process>;`           |
| `if (<expr>) <statement>;`              | `if <expr> then <process>`        |
| `if (<expr>) { <statements> }`          | `if <expr> then <process>`        |
| `if (<expr>) <stmnt1>; else <stmnt2>;`  | `if <expr> then <P1> else <P2>`   |
| `for (<init>; <cond>; <expr>) <stmnt>;` | `!(<process>)`                    |
| `struct foo {};`                        | `type foo.`                       |
| `enum foo { BOO = 0 };`                 | `type foo. const BOO: foo.`       |
| `static void foo(...) { ... }`          | `let foo(...) = ....`             |
| `int main(void) { ... }`                | `process ...`                     |

## Expressions

### Binary expressions

| SubC      | Applied Pi Calculus |
| :-------: | :-----------------: |
| `a + b`   | -                   |
| `a + c`   | `a + c`             |
| `c + a`   | `c + a`             |
| `a - b`   | -                   |
| `a - c`   | `a - c`             |
| `c - a`   | `c - a`             |
| `a * b`   | `u'mul(a, b)`       |
| `a / b`   | `u'div(a, b)`       |
| `a % b`   | `u'mod(a, b)`       |
| `a \| b`  | `u'or(a, b)`        |
| `a & b`   | `u'and(a, b)`       |
| `a ^ b`   | `u'xor(a, b)`       |
| `a << b`  | `u'shl(a, b)`       |
| `a >> b`  | `u'shr(a, b)`       |

#### Multiplication

It could be defined in the following way, but recursion is prohibited:

```ocaml
fun u'mul(nat, nat, nat): nat
  reduc forall a: nat, b: nat; u'mul(a, b, 0) = u'mul(a, b - 1, a)
  otherwise forall a: nat, b: nat, c: nat; u'mul(a, b, c) = u'mul(a, b - 1, c + a)
  otherwise forall a: nat, c: nat; u'mul(a, 0, c) = c.
```

so, for now there is just a stub:

```ocaml
fun u'mul(nat, nat): nat
  reduc forall a, b: nat; u'mul(a, b) = 0.
```

## Declarations

TODO: fill in

## Definitions

TODO: fill in

## Statements

### Branching statements

#### If statements

##### w/ else

```c
/* statements-before */
if (/* condition */)
    /* then-branch */
else
    /* else-branch */
/* statements-after */
```
---
```ocaml
new u'if_end0: channel;
(
    ((* statements-before *) if (* condition *) then
         (* then-branch *); out(u'if_end0, true)
       else
         (* else_branch *); out(u'if_end0, true))
    | (in(u'if_end0, u'tvar0: bool); (* statements-after *))
)
```

##### w/o else

```c
/* statements-before */
if (/* condition */)
    /* then-branch */
/* statements-after */
```
---
```ocaml
new u'if_end0: channel;
(
    ((* statements-before *) if (* condition *) then
         (* then-branch *); out(u'if_end0, true)
       else
         out(u'if_end0, true))
    | (in(u'if_end0: u'tvar0: bool); (* statements-after *))
)
```

#### Switch-case statements

```c
/* statements-before */
switch (/* expression */) {
  case /* const-expr0 */: /* stmnt0 */
  case /* const-expr1 */: /* stmnt1 */ break;
  case /* const-expr2 */: /* stmnt2 */ break;
  default: /* def-stmnt */
}
/* statements-after */
```
---
```ocaml
new u'sw0_case0: channel;
new u'sw0_case1: channel;
new u'sw0_case2: channel;
new u'sw0_default: channel;
new u'sw0_end: channel;
(((* statements-before *)
  if (* expression *) = (* const-expr0 *) then
    out(u'sw0_case0, true)
  else
    if (* expression *) = (* const-expr1 *) then
      out(u'sw0_case1, true)
    else
      if (* expression *) = (* const-expr2 *) then
        out(u'sw0_case2, true)
      else
        out(u'sw0_default, true))
  | (in(u'sw0_case0, u'tvar0: bool); (* stmnt0 *) out(u'sw0_case1, true))
  | (in(u'sw0_case1, u'tvar1: bool); (* stmnt1 *) out(u'sw0_end, true))
  | (in(u'sw0_case2, u'tvar2: bool); (* stmnt2 *) out(u'sw0_end, true))
  | (in(u'sw0_default, u'tvar3: bool); (* def-stmnt *) out(u'sw0_end, true))
  | (in(u'sw0_end, u'tvar4: bool);
     (* statements-after *)))
```

### Loops

#### While loops

```c
/* statements-before */
while (/* condition */) {
  /* loop-body */ }
/* statements-after */
```
---
```ocaml
new u'while_begin0: channel;
new u'while_end0: channel;
new u'while_cond0: channel;
(((* statements-before *);
  out(u'while_cond0, (* condition *)))
 |!(in(u'while_cond0, _cond0: bool);
    if _cond0 then
      out(u'while_begin0, true)
    else
      out(u'while_end0, true))
 |!(in(u'while_begin0, u'tvar0: bool);
    (* loop-body *)
    out(u'while_cond0, (* condition *)))
 |(in(u'while_end0, u'tvar1: bool);
   (* statements-after *)))
```

#### Do-while loops

```c
/* statements-before */
do {
    /* loop-body */
} while (/* condition */)
/* statements-after */
```
---
```ocaml
new u'dowhile_begin0: channel;
new u'dowhile_end0: channel;
new u'dowhile_cond0: channel;
(((* statements-before *);
  out(u'dowhile_cond0, true))
 |!(in(u'dowhile_cond0, _cond0: bool);
    if _cond0 then
      out(u'dowhile_begin0, true)
    else
      out(u'dowhile_end0, true))
 |!(in(u'dowhile_begin0, u'tvar0: bool);
    (* loop-body *)
    out(u'dowhile_cond0, (* condition *)))
 |(in(u'dowhile_end0, u'tvar1: bool);
   (* statements-after *)))
```

#### For-loops

```c
/* statements-before */
for (/* initialization */; /* condition */; /* expression */)
    /* loop-body */
/* statements-after */
```
---
```ocaml
new u'for_begin0: channel;
new u'for_end0: channel;
new u'for_cond0: channel;
(((* statements-before *) (* initialization *) out(u'for_cond0, (* condition *)))
 |!(in(u'for_cond0, _cond0: bool);
    if _cond0 then
      out(u'for_begin0, true)
    else
      out(u'for_end0, true))
 |!(in(u'for_begin0, u'tvar0: bool);
    (* loop-body *)
    (* expression *)
    out(u'for_cond0, (* condition *)))
 |(in(u'for_end0, u'tvar1: bool); (* statements-after *)))
```

## Expressions

### Function calls

#### ProVerif Functions

It's enough just call as it is:

```ocaml
fun foo(nat): nat.
...
let ret: nat = foo(42) in ...
```

#### ProVerif Process macros

If function returns nothing (`void`):

```c
void baz(int a)
{
  int x = a + 1;
}
...
/* statements-before */
baz(8);
/* statements-after */
```
---
```ocaml
let baz(a: nat, u'end: channel) = let x: nat = a + 1 in out(u'end, true).
...
new u'fcall_begin0: channel;
new u'fcall_end0: channel;
(
  ((* statements-before *) out(u'fcall_begin0, true))
  | (in(u'fcall_begin0, u'tvar0: bool); baz(8, u'fcall_end0))
  | (in(u'fcall_end0, u'tvar1: bool); (* statements-after *))
)
```

Another temporary channel should be defined if function returns any value.

```c
int foo(int a)
{
  return a + 1;
}
...
/* statements-before */
int x = foo(8);
/* statements-after*/
```
---
```ocaml
let foo(a: nat, u'ret: channel, u'end: channel) =
  let u'tvar0: nat = a + 1 in out(u'ret, u'tvar0); out(u'end, true).
...
new u'fcall_begin0: channel;
new u'fcall_end0: channel;
new u'fcall_ret0: channel;
(
  ((* statements-before *) out(u'fcall_begin0, true))
  | (in(u'fcall_begin0, u'tvar1: bool); foo(8, u'fcall_ret0, u'fcall_end0))
  | (in(u'fcall_end0, u'tvar2: bool);
     in(_fcall_ret0, u'tvar3: nat);
     let x: nat = u'tvar3 in
     (* statements-after *))
)
```

#### Recursive functions call

```c
unsigned int fact(unsigned int n)
{
  return (n > 0) ? (n * fact(n - 1)) : n;
}

int main(int argc, char** argv)
{
  int ans = fact(8);
  return 0;
}
```

Suggestion (won't work):

```ocaml
let fact(n: nat, u'ret: channel, u'end: channel) =
  if n > 0 then
    new u'fcall_begin0: channel;
    new u'fcall_end0: channel;
    new u'fcall_ret0: channel;
    (
      (out(u'fcall_begin0, true))
      | (in(u'fcall_begin0, u'tvar0: bool);
         fact(n - 1, u'fcall_ret0, u'fcall_end0))
      | (in(u'fcall_end0, u'tvar1: bool);
         in(u'fcall_ret0, u'tvar2: nat);
         let u'tvar3: nat = u'mul(n, u'tvar2) in
         out(u'ret, u'tvar3);
         out(u'end, true))
    )
  else
    out(u'ret, n);
    out(u'end, true).

let main(argc: nat, argv: bitstring, u'ret: channel, u'end: channel) =
  new u'fcall_begin1: channel;
  new u'fcall_end1: channel;
  new u'fcall_ret1: channel;
  (
    (out(u'fcall_begin1, true))
    | (in(u'fcall_begin1, u'tvar0: bool);
       fact(8, u'fcall_ret1, u'fcall_end1))
    | (in(u'fcall_end1, u'tvar1: bool);
       in(u'fcall_ret1, u'tvar2: nat);
       let ans: nat = u'tvar2 in
       out(u'ret, 0);
       out(u'end, true))
  ).
```
