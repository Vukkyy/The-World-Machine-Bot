"""
command_models

Content:

* EnhancedOption: typehintable option
* option: decoratable option

GitHub: https://github.com/interactions-py/enhanced/blob/main/interactions/ext/enhanced/command_models.py

(c) 2022 interactions-py.
"""
from inspect import _empty, signature
from typing import TYPE_CHECKING, Awaitable, Callable, List, Optional, Type, Union, get_args

from interactions import MISSING, Attachment, Channel, File, Member, Option, OptionType, Role, User

from ._logging import get_logger

if TYPE_CHECKING:
    from types import MappingProxyType
    from inspect import Parameter

from typing_extensions import _AnnotatedAlias

__all__ = ("EnhancedOption",)

log = get_logger("command_models")
_type: type = type


def get_type(param):
    """Gets the type of the parameter."""
    return get_args(param.annotation)[0] or get_args(param.annotation)[1].type


def get_option(param):
    """Gets the `EnhancedOption` of the parameter."""
    return get_args(param.annotation)[1]


def type_to_int(param):
    """Converts the type to an integer."""
    type: Union[_type, int, OptionType] = get_type(param)
    if isinstance(type, int):
        return type
    if type in (str, int, float, bool):
        if type is str:
            return OptionType.STRING
        if type is int:
            return OptionType.INTEGER
        if type is float:
            return OptionType.NUMBER
        if type is bool:
            return OptionType.BOOLEAN
    elif isinstance(type, OptionType):
        return type
    elif type is User or type is Member:
        return OptionType.USER
    elif type is Channel:
        return OptionType.CHANNEL
    elif type is Role:
        return OptionType.ROLE
    else:
        raise TypeError(f"Invalid type: {type}")


class EnhancedOption:
    """
    An alternative way of providing options by typehinting.

    Basic example:

    ```py
    @bot.command(...)
    async def command(ctx, name: EnhancedOption(int, "description") = 5):
        ...
    ```

    Full-blown example:

    ```py
    from interactions import OptionType, Channel
    from interactions.ext.enhanced import EnhancedOption
    from typing_extensions import Annotated

    @bot.command()
    async def options(
        ctx,
        option1: Annotated[str, EnhancedOption(description="...")],
        option2: Annotated[OptionType.MENTIONABLE, EnhancedOption(description="...")],
        option3: Annotated[Channel, EnhancedOption(description="...")],
    ):
        \"""Says something!\"""
        await ctx.send("something")
    ```

    Parameters:

    * `?option_type: type | int | OptionType`: The type of the option.
    * `?description: str = "No description"`: The description of the option.
    * `?name: str`: The name of the option. Defaults to the argument name.
    * `?**kwargs`: Any additional keyword arguments, same as `ipy.Option`.
    """

    def __init__(
        self,
        option_type: Union[_type, int, OptionType] = None,
        /,
        description: str = "No description",
        name: Optional[str] = None,
        **kwargs,
    ):
        log.debug("EnhancedOption.__init__")
        if isinstance(option_type, (int, _type(None))):
            self.type = option_type
        elif option_type in (str, int, float, bool):
            if option_type is str:
                self.type = OptionType.STRING
            elif option_type is int:
                self.type = OptionType.INTEGER
            elif option_type is float:
                self.type = OptionType.NUMBER
            elif option_type is bool:
                self.type = OptionType.BOOLEAN
        elif isinstance(option_type, OptionType):
            self.type = option_type
        elif option_type is User or option_type is Member:
            self.type = OptionType.USER
        elif option_type is Channel:
            self.type = OptionType.CHANNEL
        elif option_type is Role:
            self.type = OptionType.ROLE
        elif option_type is File or option_type is Attachment:
            self.type = OptionType.ATTACHMENT
        else:
            raise TypeError(f"Invalid type: {option_type}")

        self.description = description or "No description"
        self.name = name
        self.kwargs = kwargs

    def __repr__(self):
        return f"<EnhancedOption type={self.type}, name={self.name}>"


def loop_params(params: dict, stop: int) -> dict:
    """Loops through the parameters and deletes until stop index."""
    for i, key in enumerate(params.copy()):
        if i > stop:
            break
        del params[key]
    return params


def format_parameters(coro: Callable[..., Awaitable]):
    """Formats the parameters of a function."""
    params: MappingProxyType[str, Parameter] = signature(coro).parameters
    _params: dict = dict(params.items())

    if "." in coro.__qualname__:
        return loop_params(_params, 1)
    else:
        return loop_params(_params, 0)


def parameters_to_options(
    coro: Callable[..., Awaitable], has_res: bool = False
) -> Optional[List[Option]]:
    """Converts `EnhancedOption`s to `Option`s."""
    log.debug("parameters_to_options:")
    params: dict = format_parameters(coro)
    if has_res:
        for key in params:
            del params[key]
            break

    _options: List[Union[Option, Type[MISSING]]] = [
        Option(
            type=param.annotation.type,
            name=param.annotation.name or __name,
            description=param.annotation.description,
            required=param.default is _empty,
            **param.annotation.kwargs,
        )
        if isinstance(param.annotation, EnhancedOption)
        else Option(
            type=type_to_int(param),
            name=get_option(param).name or __name,
            description=get_option(param).description,
            required=param.default is _empty,
            **get_option(param).kwargs,
        )
        if isinstance(param.annotation, _AnnotatedAlias)
        else MISSING
        for __name, param in params.items()
    ]

    if any(opt is MISSING for opt in _options):
        raise TypeError(
            "You must typehint with `EnhancedOption` or specify `options=...` in the decorator!"
        )
    log.debug(f"  _options: {_options}\n")

    return _options
