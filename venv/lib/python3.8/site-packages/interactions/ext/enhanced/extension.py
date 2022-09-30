"""
extension

Content:

* base: base class for extension.
* version: version of the extension.

GitHub: https://github.com/interactions-py/enhanced/blob/main/interactions/ext/enhanced/extension.py

(c) 2022 interactions-py.
"""
import types
from logging import Logger
from re import fullmatch
from typing import Union

from interactions import Client, CommandContext, ComponentContext, Extension
from interactions.ext import Base, Version, VersionAuthor

from ._logging import get_logger

__all__ = ("Enhanced", "setup")

log: Logger = get_logger("extension")


version: Version = Version(
    version="4.0.0",
    author=VersionAuthor(
        name="Toricane",
        email="prjwl028@gmail.com",
    ),
)

base = Base(
    name="enhanced",
    version=version,
    description="Enhanced interactions for interactions.py",
    link="https://github.com/interactions-py/enhanced",
    packages=["interactions.ext.enhanced"],
    requirements=[
        "discord-py-interactions>=4.3.0",
        "typing_extensions",
    ],
)


class Enhanced(Extension):
    """
    This is the core of this library, initialized when loading the extension.

    It applies hooks to the client for additional and modified features.

    ```py
    # main.py
    client.load("interactions.ext.enhanced", ...)  # optional args/kwargs
    ```

    Parameters:

    * `(?)bot: Client`: The client instance. Not required if using `client.load("interactions.ext.enhanced", ...)`.
    * `?ignore_warning: bool`: Whether to ignore the warning. Defaults to `False`.
    * `?modify_callbacks: bool`: Whether to modify callback decorators. Defaults to `True`.
    """

    def __init__(
        self,
        bot: Client,
        *,
        ignore_warning: bool = False,
        modify_callbacks: bool = True,
    ):
        if not isinstance(bot, Client):
            log.critical("The bot is not an instance of Client")
            if not ignore_warning:
                raise TypeError(f"{bot.__class__.__name__} is not interactions.Client!")
        log.debug("The bot is an instance of Client")

        if modify_callbacks:
            from .callbacks import component, modal

            log.debug("Modifying component callbacks (modify_callbacks)")
            bot.component = types.MethodType(component, bot)

            bot.event(self._on_component, name="on_component")
            log.debug("Registered on_component")

            log.debug("Modifying modal callbacks (modify_callbacks)")
            bot.modal = types.MethodType(modal, bot)

            bot.event(self._on_modal, name="on_modal")
            log.debug("Registered on_modal")

        log.info("Hooks applied")

    async def __callback(self, ctx: Union[ComponentContext, CommandContext]):
        callback = "component" if isinstance(ctx, ComponentContext) else "modal"
        websocket = self.client._websocket

        if not any(
            any(hasattr(func, "startswith") or hasattr(func, "regex") for func in funcs)
            for _, funcs in websocket._dispatch.events.items()
        ):
            return

        for decorator_custom_id, funcs in websocket._dispatch.events.items():
            for func in funcs:
                if hasattr(func, "startswith"):
                    if ctx.data.custom_id.startswith(
                        decorator_custom_id.replace(f"{callback}_startswith_", "")
                    ):
                        log.info(f"{func} startswith {func.startswith} matched")
                        return websocket._dispatch.dispatch(decorator_custom_id, ctx)
                elif hasattr(func, "regex") and fullmatch(
                    func.regex,
                    ctx.data.custom_id.replace(f"{callback}_regex_", ""),
                ):
                    log.info(f"{func} regex {func.regex} matched")
                    return websocket._dispatch.dispatch(decorator_custom_id, ctx)

    async def _on_component(self, ctx: ComponentContext):
        """on_component callback for modified callbacks."""
        return await self.__callback(ctx)

    async def _on_modal(self, ctx: CommandContext):
        """on_modal callback for modified callbacks."""
        return await self.__callback(ctx)


def setup(
    bot: Client,
    *,
    ignore_warning: bool = False,
    modify_callbacks: bool = True,
) -> Enhanced:
    """
    This function initializes the core of the library, `Enhanced`.

    It applies hooks to the client for additional and modified features.

    ```py
    # main.py
    client.load("interactions.ext.enhanced", ...)  # optional args/kwargs
    ```

    Parameters:

    * `(?)client: Client`: The client instance. Not required if using `client.load("interactions.ext.enhanced", ...)`.
    * `?ignore_warning: bool`: Whether to ignore the warning. Defaults to `False`.
    * `?modify_callbacks: bool`: Whether to modify callback decorators. Defaults to `True`.
    """
    log.info("Setting up Enhanced")
    return Enhanced(
        bot,
        ignore_warning=ignore_warning,
        modify_callbacks=modify_callbacks,
    )
