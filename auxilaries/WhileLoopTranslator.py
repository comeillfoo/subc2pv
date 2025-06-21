#!/usr/bin/env python3
from typing import Tuple, Iterable

from auxilaries.LoopTranslator import LoopTranslator, \
    LoopsStatementsContexts


class WhileLoopTranslator(LoopTranslator):
    @classmethod
    def _counters(cls, listener) -> Tuple[str, str, str, str]:
        return tuple(listener._whiles.next())

    @classmethod
    def _loop_body(cls, ctx: LoopsStatementsContexts, listener, begin: str,
                   end: str, cond: str, var: str) -> Iterable[str]:
        enter = listener.GOTO_TMPLT.format(begin)
        exit = listener.GOTO_TMPLT.format(end)
        tvar0 = listener._tvars.next()
        tvar1 = listener._tvars.next()
        update_cond: list[str] = listener._tree.get(ctx.expression(), [])
        update_cond.append('out({}, {})'.format(cond, listener._exprs.pop()))

        lines = []
        lines.extend(update_cond)
        lines.extend([
            ')',
            f'| !(in({cond}, {var}: bool); if {var} then {enter} else {exit})',
            f'| !(in({begin}, {tvar0}: bool);'
        ])
        lines.extend(listener._tree.get(ctx.statement(), []))
        lines.extend(update_cond)
        lines.extend([')', f'| (in({end}, {tvar1}: bool);'])
        return lines
