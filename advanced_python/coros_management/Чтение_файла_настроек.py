"""
await coro()

Есть async-функция load_config().

После загрузки конфига нужно:
- проверить поле service_enabled
- если False, выбросить исключение
- если True, вернуть конфиг
"""

from dataclasses import dataclass


@dataclass
class Config:
    service_enabled: bool


class ServiceDisabledError(Exception):
    msg: str


async def load_config() -> Config:
    return Config(service_enabled=True)


async def init_service() -> Config | ServiceDisabledError:
    conf = await load_config()
    if not conf.service_enabled:
        raise ServiceDisabledError
    return conf
