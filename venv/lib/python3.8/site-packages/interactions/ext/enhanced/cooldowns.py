"""
cooldowns

Content:

* cooldown: cooldown decorator

GitHub: https://github.com/interactions-py/enhanced/blob/main/interactions/ext/enhanced/cooldowns.py

(c) 2022 interactions-py.
"""
from datetime import datetime, timedelta
from functools import wraps
from inspect import iscoroutinefunction, signature
from typing import Awaitable, Callable, Dict, Optional, Type, Union

from interactions.client.context import _Context

from interactions import Channel, Command, CommandContext, Extension, Guild, Member, User

__all__ = ("cooldown",)

NoneType: Type[None] = type(None)
_type: object = type
Coroutine = Callable[..., Awaitable]


class cooldown:
    """
    A decorator for handling cooldowns.

    Parameters for `datetime.timedelta` are `days=0, seconds=0, microseconds=0,
    milliseconds=0, minutes=0, hours=0, weeks=0`.

    ```py
    from interactions.ext.better_interactions import cooldown

    async def cooldown_error(ctx, delta):
        ...

    @client.command(...)
    @cooldown(..., error=cooldown_error, type=..., seconds=..., ...)
    async def cooldown_command(ctx, ...):
        ...
    ```

    Parameters:

    * `*delta_args: tuple[datetime.timedelta arguments]`: The arguments to pass to `datetime.timedelta`.
    * `?error: Coroutine`: The function to call if the user is on cooldown.
    * `?type: str | User | Channel | Guild = "user"`: The type of cooldown.
    * `?count: int = 1`: The number of times the user can use the command before they are on cooldown.
    * `**delta_kwargs: dict[datetime.timedelta arguments]`: The keyword arguments to pass to `datetime.timedelta`.
    """

    def __init__(
        self,
        *delta_args,
        error: Optional[Coroutine] = None,
        type: Optional[Union[str, User, Member, Channel, Guild]] = "user",
        count: int = 1,
        **delta_kwargs,
    ):
        if not (delta_args or delta_kwargs):
            raise ValueError(
                "Cooldown amount must be provided! Valid arguments and keyword arguments are listed in "
                "https://docs.python.org/3/library/datetime.html#datetime.timedelta"
            )
        if not isinstance(error, (Callable, NoneType)):
            raise TypeError("Invalid type provided for `error`! Must be a `Coroutine`!")
        if type not in {"user", User, "member", Member, "guild", Guild, "channel", Channel}:
            raise TypeError("Invalid type provided for `type`!")

        self.delta = timedelta(*delta_args, **delta_kwargs)
        self.error = error
        self.type = type

        self.last_called: Dict[str, datetime] = {}
        self.count: int = count
        self.coro_count: Dict[str, int] = {}

    def __call__(self, coro: Coroutine) -> Coroutine:
        if isinstance(coro, Command):
            raise SyntaxError("Cooldowns must go below command decorators!")

        @wraps(coro)
        async def wrapper(ctx: Union[CommandContext, Extension], *args, **kwargs):
            coro.cooldown = self
            args: list = list(args)
            _ctx: CommandContext = ctx if isinstance(ctx, _Context) else args.pop(0)
            id = self.get_id(self.type, _ctx)
            self.coro_count[id] = self.coro_count.get(id, 0) + 1
            now = datetime.now()
            unique_last_called = self.last_called.get(id)
            on_cooldown: bool = unique_last_called and (now - unique_last_called < self.delta)

            if on_cooldown and self.coro_count[id] > self.count:
                if not self.error:
                    return await _ctx.send(
                        f"This command is on cooldown for {self.delta - (now - unique_last_called)}!"
                    )
                return (
                    (
                        await self.error(_ctx, self.delta - (now - unique_last_called))
                        if iscoroutinefunction(self.error)
                        else self.error(_ctx, self.delta - (now - unique_last_called))
                    )
                    if len(signature(self.error).parameters) == 2
                    else (
                        await self.error(ctx, _ctx, self.delta - (now - unique_last_called))
                        if iscoroutinefunction(self.error)
                        else self.error(ctx, _ctx, self.delta - (now - unique_last_called))
                    )
                )

            self.last_called[id] = now
            self.coro_count[id] = 1 if self.coro_count[id] > self.count else self.coro_count[id]
            if isinstance(ctx, _Context):
                return await coro(_ctx, *args, **kwargs)
            return await coro(ctx, _ctx, *args, **kwargs)

        return wrapper

    def reset(self, id: Optional[str] = None):
        """
        Resets the cooldown.

        ```py
        @client.command(...)
        @cooldown(..., type=..., seconds=..., ...)
        async def cooldown_command(ctx, ...):
            cooldown_command.cooldown.reset(cooldown.get_id("user", ctx))
        ```

        Parameters:

        * `?id: str`: The id of the cooldown to reset. If not provided, all cooldowns are reset.
        """
        if id:
            self.last_called.pop(id)
            self.coro_count.pop(id)
        else:
            self.last_called = {}
            self.coro_count = {}

    @staticmethod
    def get_id(
        type: Optional[Union[str, User, Member, Channel, Guild]], ctx: CommandContext
    ) -> str:
        """
        Returns the appropriate ID for the type provided.

        Parameters:

        * `?type: str | User | Member | Channel | Guild`: The type of cooldown.
        * `ctx: CommandContext`: The context to get the id from.
        """
        type = type.lower() if isinstance(type, str) else type

        if type == "user" or type is User:
            return str(ctx.user.id)
        if type == "member" or type is Member:
            return f"{ctx.guild.id}:{ctx.author.id}"
        if type == "channel" or type is Channel:
            return str(ctx.channel_id)
        if type == "guild" or type is Guild:
            return str(ctx.guild_id)
        raise TypeError("Invalid type provided for `type`!")
