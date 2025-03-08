# subc2pv

Network protocol implementations on C programming language translator. Translates into network protocol specifications.

## Mapping Model Subset of C to Applied Pi Calculus. MMSC2APC

| C                                    | Applied Pi Calculus                   |
| :----------------------------------- | :------------------------------------ |
| `static int foo(...)`                | `fun ident(ident1,...)/n`             |
| `foo(...)`                           | `<process>`                           |
| `int a;`                             | `new a;`                              |
| `int a = 123;`                       | `new a;`                              |
| `int a = foo(...);`                  | `let a = in <process>;`               |
| `if (<expr>) <statement>;`           | `if <expr> then <statement>`          |
| `if (<expr>) { <statements> }`       | `if <expr> then <statements>`         |
| `if (<expr>) <stmnt>; else <stmnt>;` | `if <expr> then <stmnt> else <stmnt>` |
