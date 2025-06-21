#!/usr/bin/env python3
from typing import Tuple, Iterable

from auxilaries.LoopTranslator import LoopTranslator, \
    LoopsStatementsContexts


class ForLoopTranslator(LoopTranslator):
    @classmethod
    def _counters(cls, listener) -> Tuple[str, str, str, str]:
        return tuple(listener._fors.next())

    @classmethod
    def _loop_body(cls, ctx: LoopsStatementsContexts, listener, begin: str,
                   end: str, cond: str, var: str) -> Iterable[str]:
        enter = listener.GOTO_TMPLT.format(begin)
        exit = listener.GOTO_TMPLT.format(end)
        tvar0 = listener._tvars.next()
        tvar1 = listener._tvars.next()

        # generate iteration instructions
        iter_ctx = ctx.assignmentExpression()
        update_iter = listener._tree.get(iter_ctx, [])
        if iter_ctx is not None:
            listener._exprs.pop()

        # generate condition instructions
        cond_ctx = ctx.expression()
        update_cond, cond_expr = ([], 'true') if cond_ctx is None \
            else (listener._tree.get(cond_ctx, []), listener._exprs.pop())
        update_cond.append('out({}, {})'.format(cond, cond_expr))

        lines: list[str] = listener._tree.get(ctx.variableDeclaration() \
                                              or ctx.assignmentStatement(), [])
        lines.extend(update_cond)
        lines.extend([
            ')',
            f'| !(in({cond}, {var}: bool); if {var} then {enter} else {exit})',
            f'| !(in({begin}, {tvar0}: bool);'
        ])
        lines.extend(listener._tree.get(ctx.statement(), []))
        lines.extend(update_iter)
        lines.extend(update_cond)
        lines.extend([')', f'| (in({end}, {tvar1}: bool);'])
        return lines
