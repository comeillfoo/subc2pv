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
new if_cond0: channel;
new if_end0: channel;
(
    ((* statements-before *) out(if_cond0, (* condition *)))
    | (in(if_cond0, _cond0: bool);
       if _cond0 then
         (* then-branch *); out(if_end0, true)
       else
         (* else_branch *); out(if_end0, true))
    | (in(if_end0, _tvar0: bool); (* statements-after *))
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
new if_cond0: channel;
new if_end0: channel;
(
    ((* statements-before *); out(if_cond0, (* condition *)))
    | (in(if_cond0, _cond0: bool);
       if _cond then
         (* then-branch *); out(if_end0, true)
       else
         out(if_end0, true))
    | (in(if_end0: _tvar0: bool); (* statements-after *))
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

```ocaml
new _sw0_case0: channel;
new _sw0_case1: channel;
new _sw0_case2: channel;
new _sw0_default: channel;
new _sw0_end: channel;
(((* statements-before *)
  if (* expression *) = (* const-expr0 *) then
    out(_sw0_case0, true)
  else
    if (* expression *) = (* const-expr1 *) then
      out(_sw0_case1, true)
    else
      if (* expression *) = (* const-expr2 *) then
        out(_sw0_case2, true)
      else
        out(_sw0_default, true))
  | (in(_sw0_case0, _tvar0: bool); (* stmnt0 *) out(_sw0_case1, true))
  | (in(_sw0_case1, _tvar1: bool); (* stmnt1 *) out(_sw0_end, true))
  | (in(_sw0_case2, _tvar2: bool); (* stmnt2 *) out(_sw0_end, true))
  | (in(_sw0_default, _tvar3: bool); (* def-stmnt *) out(_sw0_end, true))
  | (in(_sw0_end, _tvar4: bool);
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
new _while_begin0: channel;
new _while_end0: channel;
new _while_cond0: channel;
(((* statements-before *);
  out(_while_cond0, (* condition *)))
 |!(in(_while_cond0, _cond0: bool);
    if _cond0 then
      out(_while_begin0, true)
    else
      out(_while_end0, true))
 |!(in(_while_begin0, _tvar0: bool);
    (* loop-body *)
    out(_while_cond0, (* condition *)))
 |(in(_while_end0, _tvar1: bool);
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
new _dowhile_begin0: channel;
new _dowhile_end0: channel;
new _dowhile_cond0: channel;
(((* statements-before *);
  out(_dowhile_cond0, true))
 |!(in(_dowhile_cond0, _cond0: bool);
    if _cond0 then
      out(_dowhile_begin0, true)
    else
      out(_dowhile_end0, true))
 |!(in(_dowhile_begin0, _tvar0: bool);
    (* loop-body *)
    out(_dowhile_cond0, (* condition *)))
 |(in(_dowhile_end0, _tvar1: bool);
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
new _for_begin0: channel;
new _for_end0: channel;
new _for_cond0: channel;
(((* statements-before *) (* initialization *) out(_for_cond0, (* condition *)))
 |!(in(_for_cond0, _cond0: bool);
    if _cond0 then
      out(_for_begin0, true)
    else
      out(_for_end0, true))
 |!(in(_for_begin0, _tvar0: bool);
    (* loop-body *)
    (* expression *)
    out(_for_cond0, (* condition *)))
 |(in(_for_end0, _tvar1: bool); (* statements-after *)))
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

```ocaml
let baz(a: nat, _end: channel) = let x: nat = a + 1 in out(_end, true).
...
new _fcall_begin0: channel;
new _fcall_end0: channel;
(
  ((* statements-before *) out(_fcall_begin0, true))
  | (in(_fcall_begin0, _tvar0: bool); baz(8, _fcall_end0))
  | (in(_fcall_end0, _tvar1: bool); (* statements-after *))
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

```ocaml
let foo(a: nat, _ret_ch: channel, _end: channel) =
  let _tvar0: nat = a + 1 in out(_ret_ch, _tvar0); out(_end, true).
...
new _fcall_begin0: channel;
new _fcall_end0: channel;
new _fcall_ret0: channel;
(
  ((* statements-before *) out(_fcall_begin0, true))
  | (in(_fcall_begin0, _tvar1: bool); foo(8, _fcall_ret0, _fcall_end0))
  | (in(_fcall_end0, _tvar2: bool);
     in(_fcall_ret0, _tvar3: nat);
     let x: nat = _tvar3 in
     (* statements-after *))
)
```
