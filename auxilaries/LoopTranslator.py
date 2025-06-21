#!/usr/bin/env python3
from abc import ABC, abstractmethod
from typing import Optional, Union, Tuple, Iterable

from libs.SubCParser import SubCParser


LoopsStatementsContexts = Union[SubCParser.WhileStatementContext,
                                SubCParser.DoWhileStatementContext,
                                SubCParser.ForStatementContext]


class LoopTranslator(ABC):
    @classmethod
    def translate(cls, preceding: list[str],
                  ctx: LoopsStatementsContexts,
                  subsequent: list[str],
                  listener) -> list[str]:
        begin, end, cond, var = cls._counters(listener)

        lines = [
            listener.NEW_VAR_TMPLT.format(begin, 'channel'),
            listener.NEW_VAR_TMPLT.format(end, 'channel'),
            listener.NEW_VAR_TMPLT.format(cond, 'channel'),
            '((',
        ]
        lines.extend(preceding)
        lines.extend(cls._loop_body(ctx, listener, begin, end, cond, var))
        lines.extend(subsequent)
        lines.append('))')
        return lines

    @classmethod
    @abstractmethod
    def _counters(cls, listener) -> Tuple[str, str, str, str]:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def _loop_body(cls, ctx: LoopsStatementsContexts, listener, begin: str,
                   end: str, cond: str, var: str) -> Iterable[str]:
        raise NotImplementedError
