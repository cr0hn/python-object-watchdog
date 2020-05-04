import asyncio

from typing import Dict
from dataclasses import dataclass, field

from object_watchdog import ObjectWatchdog


async def async_callback(instance, klass_name, key, value):
    print(f"[!] New change local callback in key '{key}'. New value '{value}'")


async def async_callback2(instance, klass_name, key, value):
    print(f"[0] New change local callback in key '{key}'. New value '{value}'")


def callback(instance, klass_name, key, value):
    print(f"[!] Sync New change local callback in key '{key}'. New value '{value}'")


@dataclass
class User(metaclass=ObjectWatchdog):
    __async_callbacks__ = [async_callback, async_callback2]
    __callbacks__ = [callback]

    user: str
    password: str


async def coro_main():

    u1 = User(user="john", password="password")

    print("[*] Modifying property 'value'")
    u1.value = "new value!"


def main():
    asyncio.run(coro_main())


main()
