"""
commands

Content:

* setup_options: Sets up the options of the command.

GitHub: https://github.com/interactions-py/enhanced/blob/main/interactions/ext/enhanced/commands.py

(c) 2022 interactions-py.
"""
from inspect import signature
from logging import Logger
from typing import Awaitable, Callable

from typing_extensions import _AnnotatedAlias

from ._logging import get_logger
from .command_models import EnhancedOption, parameters_to_options

__all__ = ("setup_options",)

log: Logger = get_logger("command")


def setup_options(coro: Callable[..., Awaitable]):
    """
    Sets up the options of the command.

    Usage:
    ```py
    @bot.command()
    @setup_options
    async def test(ctx, option: EnhancedOption(...)):
        ...
    ```

    Parameters:

    * `(X)coro: Callable[..., Awaitable]`: The coroutine to setup the options of.
    """
    params = signature(coro).parameters

    def check(num: int):
        nonlocal params
        return len(params) > num and all(
            isinstance(param.annotation, (EnhancedOption, _AnnotatedAlias))
            for param in list(params.values())[num:]
        )

    if not (check(1) or check(2)):
        return coro

    options = parameters_to_options(coro)

    if hasattr(coro, "_options") and isinstance(coro._options, list):
        coro._options.extend(options)
    else:
        coro._options = options

    return coro
