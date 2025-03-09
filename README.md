# subc2pv

Network protocol implementations on C programming language translator. Translates into network protocol specifications.

## Mapping Model Subset of C to Applied Pi Calculus. MMSC2APC

| C                                       | Applied Pi Calculus               |
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
