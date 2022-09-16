import itertools
from asyncio import gather, sleep
from typing import List, Optional

from interactions.api.models.flags import Intents
from interactions.api.models.presence import ClientPresence
from interactions.base import get_logger
from interactions.client.bot import Client, Extension

__all__ = ("DummyClient", "AutoShardedClient")


class DummyClient(Client):
    """
    This class is representing a dummy without sync behaviour, handling a shard without getting
    commands or making extra sync calls. Do not use this class.
    """

    def __init__(self, token, **kwargs):
        super().__init__(token, **kwargs)

    async def _ready(self) -> None:
        log = get_logger("Client")
        ready: bool = False

        try:
            if self.me.flags is not None:
                # This can be None.
                if self._intents.GUILD_PRESENCES in self._intents and not (
                    self.me.flags.GATEWAY_PRESENCE in self.me.flags
                    or self.me.flags.GATEWAY_PRESENCE_LIMITED in self.me.flags
                ):
                    raise RuntimeError("Client not authorised for the GUILD_PRESENCES intent.")
                if self._intents.GUILD_MEMBERS in self._intents and not (
                    self.me.flags.GATEWAY_GUILD_MEMBERS in self.me.flags
                    or self.me.flags.GATEWAY_GUILD_MEMBERS_LIMITED in self.me.flags
                ):
                    raise RuntimeError("Client not authorised for the GUILD_MEMBERS intent.")
                if self._intents.GUILD_MESSAGES in self._intents and not (
                    self.me.flags.GATEWAY_MESSAGE_CONTENT in self.me.flags
                    or self.me.flags.GATEWAY_MESSAGE_CONTENT_LIMITED in self.me.flags
                ):
                    log.critical("Client not authorised for the MESSAGE_CONTENT intent.")
            elif self._intents.value != Intents.DEFAULT.value:
                raise RuntimeError("Client not authorised for any privileged intents.")

            # await self._Client__get_all_commands()
            # await self.__register_name_autocomplete()
            # self.__register_events()

            # no dispatch things here

            ready = True
        except Exception:
            log.exception("Could not prepare the client:")
        finally:
            if ready:
                log.debug("Client is now ready.")
                await self._login()


class AutoShardedClient(Client):
    def __init__(self, token: str, max_concurrency: int = None, **kwargs):
        super().__init__(token, **kwargs)
        self._clients: List[DummyClient] = []
        self.max_concurrency: int = max_concurrency

    @property
    def total_latency(self) -> float:
        _latencies = [getattr(self, "latency", 0.0)]
        _latencies.extend(getattr(_client, "latency", 0.0) for _client in self._clients)
        return sum(_latencies) / len(_latencies)

    async def __sync(self) -> None:
        await super()._Client__sync()

    def start(self):
        if self._automate_sync:
            self._loop.run_until_complete(self.__sync())
            # self._automate_sync = False
        self._loop.run_until_complete(self.__ready())

    async def change_presence(self, presence: ClientPresence) -> None:
        await super().change_presence(presence)
        for client in self._clients:
            await client.change_presence(presence)

    async def _ready(self) -> None:
        await self._login()

    async def __ready(self) -> None:
        ready: bool = False
        log = get_logger("Client")
        try:
            if self.me.flags is not None:
                # This can be None.
                if self._intents.GUILD_PRESENCES in self._intents and not (
                    self.me.flags.GATEWAY_PRESENCE in self.me.flags
                    or self.me.flags.GATEWAY_PRESENCE_LIMITED in self.me.flags
                ):
                    raise RuntimeError("Client not authorised for the GUILD_PRESENCES intent.")
                if self._intents.GUILD_MEMBERS in self._intents and not (
                    self.me.flags.GATEWAY_GUILD_MEMBERS in self.me.flags
                    or self.me.flags.GATEWAY_GUILD_MEMBERS_LIMITED in self.me.flags
                ):
                    raise RuntimeError("Client not authorised for the GUILD_MEMBERS intent.")
                if self._intents.GUILD_MESSAGES in self._intents and not (
                    self.me.flags.GATEWAY_MESSAGE_CONTENT in self.me.flags
                    or self.me.flags.GATEWAY_MESSAGE_CONTENT_LIMITED in self.me.flags
                ):
                    log.critical("Client not authorised for the MESSAGE_CONTENT intent.")
            elif self._intents.value != Intents.DEFAULT.value:
                raise RuntimeError("Client not authorised for any privileged intents.")

            self._Client__register_events()

            await self._Client__register_name_autocomplete()

            ready = True
        except Exception:
            log.exception("Could not prepare the client:")
        finally:
            if ready:
                log.debug("Client is now ready.")
                await self.__login()

    async def __login(self) -> None:

        for attrib, client in itertools.product(self._websocket._dispatch.__slots__, self._clients):
            setattr(client._websocket._dispatch, attrib, getattr(self._websocket._dispatch, attrib))

        tasks = []
        _clients = [self]
        _clients.extend(self._clients)

        index = 0
        num = 0
        tasks.append([])
        for client in _clients:
            if num > self.max_concurrency:
                index += 1
                tasks.append([])
                num = 0

            tasks[index].append(client._ready())
            num += 1

        setattr(self, "gather_tasks", tasks)
        __tasks = [self.run_gathered(i) for i in range(len(tasks))]
        await gather(*__tasks)

    async def run_gathered(self, index: int):
        await sleep(index * 10)
        await gather(*self.gather_tasks[index])

    def remove(
        self, name: str, remove_commands: bool = True, package: Optional[str] = None
    ) -> None:
        super().remove(name, remove_commands, package)

        for attrib, client in itertools.product(self._websocket._dispatch.__slots__, self._clients):
            setattr(client._websocket._dispatch, attrib, getattr(self._websocket._dispatch, attrib))

    def load(
        self, name: str, package: Optional[str] = None, *args, **kwargs
    ) -> Optional[Extension]:
        extension = super().load(name, package, *args, **kwargs)

        for attrib, client in itertools.product(self._websocket._dispatch.__slots__, self._clients):
            setattr(client._websocket._dispatch, attrib, getattr(self._websocket._dispatch, attrib))

        return extension
