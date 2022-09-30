"""
callbacks

Content:

* component: component callback
* modal: modal callback
* extension_component: extension component callback
* extension_modal: extension modal callback

GitHub: https://github.com/interactions-py/enhanced/blob/main/interactions/ext/enhanced/callbacks.py

(c) 2022 interactions-py.
"""
from re import compile
from typing import Awaitable, Callable, Optional, Union

from interactions import Button, Client, Component, Modal, SelectMenu

from ._logging import get_logger

log = get_logger("callback")
Coroutine = Callable[..., Awaitable]

__all__ = ("component", "modal", "extension_component", "extension_modal")


def component(
    bot: Client,
    component: Union[str, Button, SelectMenu],
    startswith: bool = False,
    regex: bool = False,
) -> Callable[[Coroutine], Coroutine]:
    """
    A modified decorator that allows you to add more information to the `custom_id` and use
    `startswith` or `regex` to invoke the callback.

    ```py
    bot.load("interactions.ext.enhanced")

    # startswith:
    @bot.component("test", startswith=True)
    async def test(ctx):
        ...

    # regex:
    @bot.component(r"^[a-z0-9_-]{1,32}$", regex=True)
    async def test(ctx):
        ...
    ```

    The startswith callback is called if the `custom_id` starts with the given string.

    The regex callback is called if the `custom_id` matches the given regex.

    Parameters:

    * `(X)bot: Client`: The bot client.
    * `component: str | Button | SelectMenu`: The component custom_id or regex to listen to.
    * `?startswith: bool = False`: Whether the component custom_id starts with the given string.
    * `?regex: bool = False`: Whether the component custom_id matches the given regex.
    """

    def decorator(coro: Coroutine) -> Coroutine:
        if hasattr(coro, "__extension"):
            return bot.event(coro, name=f"component_{component}")

        payload: str = (
            Component(**component._json).custom_id
            if isinstance(component, (Button, SelectMenu))
            else component
        )
        if startswith and regex:
            log.error("Cannot use both startswith and regex.")
            raise ValueError("Cannot use both startswith and regex!")

        if startswith:
            try:
                coro.startswith = True
            except AttributeError:
                coro.__func__.startswith = True
            bot.event(coro, name=f"component_startswith_{payload}")
        elif regex:
            try:
                coro.regex = compile(payload)
            except AttributeError:
                coro.__func__.regex = compile(payload)
            bot.event(coro, name=f"component_regex_{payload}")
        else:
            bot.event(coro, name=f"component_{payload}")

        log.debug(f"Component callback, {startswith=}, {regex=}")
        return coro

    return decorator


def modal(
    bot: Client,
    modal: Union[Modal, str],
    startswith: bool = False,
    regex: bool = False,
) -> Callable[[Coroutine], Coroutine]:
    """
    A modified decorator that allows you to add more information to the `custom_id` and use
    `startswith` or `regex` to invoke the callback.

    ```py
    bot.load("interactions.ext.enhanced")

    # startswith:
    @bot.modal("test", startswith=True)
    async def test(ctx):
        ...

    # regex:
    @bot.modal(r"^[a-z0-9_-]{1,32}$", regex=True)
    async def test(ctx):
        ...
    ```

    The startswith callback is called if the `custom_id` starts with the given string.

    The regex callback is called if the `custom_id` matches the given regex.

    Parameters:

    * `(X)bot: Client`: The bot client.
    * `modal: str | Modal`: The modal custom_id or regex to listen to.
    * `?startswith: bool = False`: Whether the modal custom_id starts with the given string.
    * `?regex: bool`: Whether the modal custom_id matches the given regex.
    """

    def decorator(coro: Coroutine) -> Coroutine:
        if hasattr(coro, "__extension"):
            return bot.event(coro, name=f"modal_{modal}")

        payload: str = modal.custom_id if isinstance(modal, Modal) else modal
        if startswith and regex:
            log.error("Cannot use both startswith and regex.")
            raise ValueError("Cannot use both startswith and regex!")

        if startswith:
            try:
                coro.startswith = True
            except AttributeError:
                coro.__func__.startswith = True
            bot.event(coro, name=f"modal_startswith_{payload}")
        elif regex:
            try:
                coro.regex = compile(payload)
            except AttributeError:
                coro.__func__.regex = compile(payload)
            bot.event(coro, name=f"modal_regex_{payload}")
        else:
            bot.event(coro, name=f"modal_{payload}")

        log.debug(f"Modal callback, {startswith=}, {regex=}")
        return coro

    return decorator


def extension_component(
    component: Union[str, Button, SelectMenu],
    startswith: Optional[bool] = False,
    regex: Optional[bool] = False,
):
    """
    A modified decorator that allows you to add more information to the `custom_id` and use
    `startswith` or `regex` to invoke the callback inside of `Extension`s.

    ```py
    # main.py:
    bot.load("interactions.ext.enhanced")

    # startswith:
    @extension_component("test", startswith=True)
    async def test(self, ctx):
        ...

    # regex:
    @extension_component(r"^[a-z0-9_-]{1,32}$", regex=True)
    async def test(self, ctx):
        ...
    ```

    The startswith callback is called if the `custom_id` starts with the given string.

    The regex callback is called if the `custom_id` matches the given regex.

    Parameters:

    * `component: str | Button | SelectMenu`: The component custom_id or regex to listen to.
    * `?startswith: bool = False`: Whether the component custom_id starts with the given string.
    * `?regex: bool = False`: Whether the component custom_id matches the given regex.
    """

    def decorator(func):
        if startswith and regex:
            log.error("Cannot use both startswith and regex.")
            raise ValueError("Cannot use both startswith and regex!")

        func.__extension = True
        payload: str = (
            Component(**component._json).custom_id
            if isinstance(component, (Button, SelectMenu))
            else component
        )

        if startswith:
            try:
                func.startswith = True
            except AttributeError:
                func.__func__.startswith = True
            payload = f"startswith_{payload}"
        elif regex:
            try:
                func.regex = compile(payload)
            except AttributeError:
                func.__func__.regex = compile(payload)
            payload = f"regex_{payload}"

        log.debug(f"Extension component callback, {startswith=}, {regex=}")

        func.__component_data__ = (
            (),
            {"component": payload, "startswith": startswith, "regex": regex},
        )
        return func

    return decorator


def extension_modal(
    modal: Union[Modal, str],
    startswith: bool = False,
    regex: bool = False,
):
    """
    A modified decorator that allows you to add more information to the `custom_id` and use
    `startswith` or `regex` to invoke the callback inside of `Extension`s.

    ```py
    # main.py:
    bot.load("interactions.ext.enhanced")

    # startswith:
    @extension_modal("test", startswith=True)
    async def test(self, ctx):
        ...

    # regex:
    @extension_modal(r"^[a-z0-9_-]{1,32}$", regex=True)
    async def test(self, ctx):
        ...
    ```

    The startswith callback is called if the `custom_id` starts with the given string.

    The regex callback is called if the `custom_id` matches the given regex.

    Parameters:

    * `modal: str | Modal`: The modal custom_id or regex to listen to.
    * `?startswith: bool = False`: Whether the modal custom_id starts with the given string.
    * `?regex: bool` = False: Whether the modal custom_id matches the given regex.
    """

    def decorator(func):
        if startswith and regex:
            log.error("Cannot use both startswith and regex.")
            raise ValueError("Cannot use both startswith and regex!")

        func.__extension = True
        payload: str = modal.custom_id if isinstance(modal, Modal) else modal

        if startswith:
            try:
                func.startswith = True
            except AttributeError:
                func.__func__.startswith = True
            payload = f"startswith_{payload}"
        elif regex:
            try:
                func.regex = compile(payload)
            except AttributeError:
                func.__func__.regex = compile(payload)
            payload = f"regex_{payload}"

        log.debug(f"Extension modal callback, {startswith=}, {regex=}")

        func.__modal_data__ = (
            (),
            {"modal": payload, "startswith": startswith, "regex": regex},
        )
        return func

    return decorator
