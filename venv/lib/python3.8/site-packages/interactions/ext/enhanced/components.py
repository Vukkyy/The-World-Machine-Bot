"""
components

Content:

* ActionRow: enhanced action row
* Button: enhanced button
* SelectOption: enhanced select option
* SelectMenu: enhanced select menu
* TextInput: enhanced text input
* Modal: enhanced modal
* spread_to_rows: spread components to rows

GitHub: https://github.com/interactions-py/enhanced/blob/main/interactions/ext/enhanced/components.py

(c) 2022 interactions-py.
"""
from typing import List, Optional, Union

from interactions import ActionRow as AR
from interactions import Button as B
from interactions import ButtonStyle, Emoji
from interactions import Modal as M
from interactions import SelectMenu as SM
from interactions import SelectOption as SO
from interactions import TextInput as TI
from interactions import TextStyleType as TST

from ._logging import get_logger

__all__ = (
    "ActionRow",
    "Button",
    "SelectOption",
    "SelectMenu",
    "TextInput",
    "Modal",
)

log = get_logger("components")


def ActionRow(*args: Union[B, SM, TI]) -> AR:
    """
    A helper function that passes arguments to `ActionRow`.

    Previous:

    ```py
    row = ActionRow(components=[...])
    ```

    Now:

    ```py
    row = ActionRow(...)
    ```

    Parameters:

    * `*args: tuple[Button | SelectMenu | TextInput]`: The components to add to the `ActionRow`.

    Returns:

    `ActionRow`
    """
    log.debug(f"Creating ActionRow with {list(args)}")
    return AR(components=list(args))


def Button(
    style: Union[ButtonStyle, int],
    label: str,
    *,
    custom_id: Optional[str] = None,
    url: Optional[str] = None,
    emoji: Optional[Emoji] = None,
    disabled: bool = False,
    **kwargs,
) -> B:
    """
    A helper function that passes arguments to `Button`.

    Previous:

    ```py
    button = Button(style=1, label="1", custom_id="1", ...)
    ```

    Now:

    ```py
    button = Button(1, "1", custom_id="1", ...)
    ```

    Parameters:

    * `style: ButtonStyle | int`: The style of the button.
    * `label: str`: The label of the button.
    * `(?)custom_id: str`: The custom id of the button. *Required if the button is not a link.*
    * `(?)url: str`: The URL of the button. *Required if the button is a link.*
    * `?emoji: Emoji`: The emoji of the button.
    * `?disabled: bool = False`: Whether the button is disabled.
    * `**kwargs: dict`: Any additional arguments of the button.

    Returns:

    `Button`
    """
    log.debug(
        f"Creating Button with {style=}, {label=}, {custom_id=}, {url=}, {emoji=}, {disabled=}"
    )
    if custom_id and url:
        raise ValueError("`custom_id` and `url` cannot be used together!")

    if not (custom_id or url):
        raise ValueError("`custom_id` or `url` must be specified!")

    if style == ButtonStyle.LINK and not url:
        raise ValueError("`url` must be specified if `style` is `ButtonStyle.LINK`!")
    if url and style != ButtonStyle.LINK:
        raise ValueError("`url` can only be specified if `style` is `ButtonStyle.LINK`!")

    if style != ButtonStyle.LINK and not custom_id:
        raise ValueError("`custom_id` must be specified if `style` is not `ButtonStyle.LINK`!")
    if custom_id and style == ButtonStyle.LINK:
        raise ValueError("`custom_id` can only be specified if `style` is not `ButtonStyle.LINK`!")

    return B(
        style=style,
        label=label,
        custom_id=custom_id,
        url=url,
        emoji=emoji,
        disabled=disabled,
        **kwargs,
    )


def SelectOption(
    label: str,
    value: str,
    description: Optional[str] = None,
    emoji: Optional[Emoji] = None,
    disabled: bool = False,
    **kwargs,
) -> SO:
    """
    A helper function that passes arguments to `SelectOption`.

    Before:

    ```py
    option = SelectOption(label="1", value="1", ...)
    ```

    Now:

    ```py
    option = SelectOption("1", "1", ...)
    ```

    Parameters:

    * `label: str`: The label of the option.
    * `value: str`: The value of the option.
    * `?description: str`: The description of the option.
    * `?emoji: Emoji`: The emoji of the option.
    * `?disabled: bool = False`: Whether the option is disabled.
    * `**kwargs: dict`: Any additional arguments of the option.

    Returns:

    `SelectOption`
    """
    log.debug(
        f"Creating SelectOption with {label=}, {value=}, {description=}, {emoji=}, {disabled=}"
    )
    return SO(
        label=label,
        value=value,
        description=description,
        emoji=emoji,
        disabled=disabled,
        **kwargs,
    )


def SelectMenu(
    custom_id: str,
    options: List[SO],
    *,
    placeholder: Optional[str] = None,
    min_values: Optional[int] = None,
    max_values: Optional[int] = None,
    disabled: bool = False,
    **kwargs,
) -> SM:
    """
    A helper function that passes arguments to `SelectMenu`.

    Previous:

    ```py
    select = SelectMenu(custom_id="s", options=[...], ...)
    ```

    Now:

    ```py
    select = SelectMenu("s", [...], ...)
    ```

    Parameters:

    * `custom_id: str`: The custom id of the select menu.
    * `options: list[SelectOption]`: The options of the select menu.
    * `?placeholder: str`: The placeholder of the select menu.
    * `?min_values: int`: The minimum number of values that can be selected.
    * `?max_values: int`: The maximum number of values that can be selected.
    * `?disabled: bool`: Whether the select menu is disabled. Defaults to `False`.
    * `**kwargs: dict`: Any additional arguments of the select menu.

    Returns:

    `SelectMenu`
    """
    log.debug(
        f"Creating SelectMenu with {custom_id=}, {options=}, {placeholder=}, {min_values=}, {max_values=}, {disabled=}"
    )
    return SM(
        custom_id=custom_id,
        options=options,
        placeholder=placeholder,
        min_values=min_values,
        max_values=max_values,
        disabled=disabled,
        **kwargs,
    )


def TextInput(
    custom_id: str,
    label: str,
    style: TST = TST.SHORT,
    value: Optional[str] = None,
    required: bool = True,
    placeholder: Optional[str] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    **kwargs,
) -> TI:
    """
    A helper function that passes arguments to `TextInput`.

    Before:

    ```py
    ti = TextInput(custom_id="ti", label="ti", style=1, ...)
    ```

    Now:

    ```py
    ti = TextInput("ti", "ti", 1, ...)
    ```

    Parameters:

    * `custom_id: str`: The custom id of the text input.
    * `label: str`: The label of the text input.
    * `?style: TextInputStyle | int`: The style of the text input.
    * `?value: str`: The value of the text input.
    * `?required: bool = True`: Whether the text input is required.
    * `?placeholder: str`: The placeholder of the text input.
    * `?min_length: int`: The minimum length of the text input.
    * `?max_length: int`: The maximum length of the text input.

    Returns:

    `TextInput`
    """
    log.debug(
        f"Creating TextInput with {custom_id=}, {label=}, {style=}, {value=}, {required=}, {placeholder=}, {min_length=}, {max_length=}"
    )
    return TI(
        custom_id=custom_id,
        label=label,
        style=style,
        value=value,
        required=required,
        placeholder=placeholder,
        min_length=min_length,
        max_length=max_length,
        **kwargs,
    )


def Modal(custom_id: str, title: str, components: List[TI], **kwargs) -> M:
    """
    A helper function that passes arguments to `Modal`.

    Before:

    ```py
    modal = Modal(custom_id="modal", title="Modal", components=[...])
    ```

    Now:

    ```py
    modal = Modal("modal", "Modal", [...])
    ```

    Parameters:

    * `custom_id: str`: The custom id of the modal.
    * `title: str`: The title of the modal.
    * `components: list[TextInput]`: The components of the modal.
    * `**kwargs: dict`: Any additional arguments of the modal.

    Returns:

    `Modal`
    """
    log.debug(f"Creating Modal with {custom_id=}, {title=}, {components=}")
    return M(custom_id=custom_id, title=title, components=components, **kwargs)
