#!/usr/bin/env python3
from typing import Tuple, Iterable

from auxilaries.LoopTranslator import LoopTranslator, \
    LoopsStatementsContexts


class DoWhileLoopTranslator(LoopTranslator):
    @classmethod
    def _counters(cls, listener) -> Tuple[str, str, str, str]:
        return tuple(listener._dowhiles.next())

    @classmethod
    def _loop_body(cls, ctx: LoopsStatementsContexts, listener, begin: str,
                   end: str, cond: str, var: str) -> Iterable[str]:
        enter = listener.GOTO_TMPLT.format(begin)
        exit = listener.GOTO_TMPLT.format(end)
        body = listener._tree[ctx.statement()]
        tvar0 = listener._tvars.next()
        tvar1 = listener._tvars.next()
        cond_stmts = listener._tree.get(ctx.expression(), '').strip()
        update_cond = cond_stmts + \
            '{}out({}, {})'.format('' if not cond_stmts else ' ', cond,
                                   listener._exprs.pop())
        return [
            f'out({cond}, true))',
            f'| !(in({cond}, {var}: bool); if {var} then {enter} else {exit})',
            f'| !(in({begin}, {tvar0}: bool); {body} {update_cond})',
            f'| (in({end}, {tvar1}: bool);'
        ]
