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

### If statements

#### w/ else

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
    (<statements-before>; out(if_cond0, <condition>))
    | (in(if_cond0, _cond0: bool);
       if _cond then
         <then-branch>; out(if_end0, true)
       else
         <else_branch>; out(if_end0, true))
    | (in(if_end0, _tvar0: bool); <statements-after>)
)
```

#### w/o else

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
    (<statements-before>; out(if_cond0, <condition>))
    | (in(if_cond0, _cond0: bool);
       if _cond then
         <then-branch>; out(if_end0, true)
       else
         out(if_end0, true))
    | (in(if_end0: _tvar0: bool); <statements-after>)
)
```

### Loops

#### While loops

```c
<операторы до цикла>
while (<условие>) {
  <тело цикла> }
<операторы после цикла>
```
---
```ocaml
new _while0_begin: channel;
new _while0_end: channel;
new _while0_cond: channel;
((<операторы до цикла>;
  out(_while0_cond, <условие>))
 |!(in(_while0_cond, _cond0: bool);
    if _cond0 then
      out(_while0_begin, true)
    else
      out(_while0_end, true))
 |!(in(_while0_begin, _tmp0: bool);
    <тело цикла>
    out(_while0_cond, <условие>))
 |(in(_while0_end, _tmp1: bool);
   <операторы после цикла>))
```

#### Do-while loops

```c
// операторы до цикла>
do {
    /* тело цикла */
} while (/* условие */)
/* операторы после цикла */
```
---
```ocaml
new _dowhile0_begin: channel;
new _dowhile0_end: channel;
new _dowhile0_cond: channel;
((<операторы до цикла>;
  out(_dowhile0_cond, true))
 |!(in(_dowhile0_cond, _cond0: bool);
    if _cond0 then
      out(_dowhile0_begin, true)
    else
      out(_dowhile0_end, true))
 |!(in(_dowhile0_begin, _tmp0: bool);
    <тело цикла>
    out(_dowhile0_cond, <условие>))
 |(in(_dowhile0_end, _tmp1: bool);
   <операторы после цикла>))
```

#### For-loops

```c
/* операторы до цикла */
for (/* инициализация */; /* условие */; /* выражение */)
    /* тело цикла */
/* операторы после цикла */
```
---
```ocaml
new _for0_begin: channel;
new _for0_end: channel;
new _for0_cond: channel;
((<операторы до цикла> <инициализация> out(_for0_cond, <условие>))
 |!(in(_for0_cond, _cond0: bool);
    if _cond0 then
      out(_for0_begin, true)
    else
      out(_for0_end, true))
 |!(in(_for0_begin, _tmp0: bool);
    <тело цикла>
    <выражение>
    out(_for0_cond, <условие>))
 |(in(_for0_end, _tmp1: bool); <операторы после цикла>))
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
/* операторы до вызова */
baz(8);
/* операторы после вызова*/
```

```ocaml
let baz(a: nat, _end: channel) = let x: nat = a + 1 in out(_end, true).
...
new _fcall_begin0: channel;
new _fcall_end0: channel;
(
  (<операторы до вызова> out(_fcall_begin0))
  | (in(_fcall_begin0, _tvar0: bool); baz(8, _fcall_end0))
  | (in(_fcall_end0, _tvar1: bool); <операторы после вызова>)
)
```

Another temporary channel should be defined if function returns any value.

```c
int foo(int a)
{
  return a + 1;
}
...
/* операторы до вызова */
int x = foo(8);
/* операторы после вызова*/
```

```ocaml
let foo(a: nat, _ret_ch: channel, _end: channel) =
  let _tvar0: nat = a + 1 in out(_ret_ch, _tvar0); out(_end, true).
...
new _fcall_begin0: channel;
new _fcall_end0: channel;
new _fcall_ret0: channel;
(
  (<операторы до вызова> out(_fcall_begin0))
  | (in(_fcall_begin0, _tvar1: bool); foo(8, _fcall_ret0, _fcall_end0))
  | (in(_fcall_end0, _tvar2: bool);
     in(_fcall_ret0, _tvar3: nat);
     let x: nat = _tvar3 in
     <операторы после вызова>)
)
```
