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
        body = listener._tree[ctx.statement()]
        tvar0 = listener._tvars.next()
        tvar1 = listener._tvars.next()

        # generate iteration instructions
        iter_ctx = ctx.assignmentExpression()
        update_iter = ''
        if iter_ctx is not None:
            listener._exprs.pop()
            update_iter = listener._tree[iter_ctx] + ' '

        # generate condition instructions
        cond_ctx = ctx.expression()
        cond_stmts, cond_expr = ('', 'true') if cond_ctx is None \
            else (listener._tree[cond_ctx], listener._exprs.pop())
        update_cond = cond_stmts + \
            '{}out({}, {})'.format('' if not cond_stmts else ' ', cond,
                                   cond_expr)

        init_ctx = ctx.variableDeclaration() or ctx.assignmentStatement()
        lines = [] if init_ctx is None else [listener._tree[init_ctx]]
        lines.extend([
            update_cond + ')',
            f'| !(in({cond}, {var}: bool); if {var} then {enter} else {exit})',
            f'| !(in({begin}, {tvar0}: bool); {body} {update_iter}{update_cond})',
            f'| (in({end}, {tvar1}: bool);'
        ])
        return lines
