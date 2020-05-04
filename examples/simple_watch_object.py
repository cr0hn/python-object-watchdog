import asyncio

from typing import Dict
from dataclasses import dataclass, field

from object_watchdog import ObjectWatchdog


@dataclass
class MyClass(metaclass=ObjectWatchdog):
    value: str
    my_dict: Dict = field(default_factory=dict)


async def coro_callback(instance, klass_name, key, value):
    print(f"[!] New change in key '{key}'. New value '{value}'")


async def coro_main():

    u = MyClass(value="asdfasdf", my_dict={"k": "v"})
    u.add_async_callback(coro_callback)

    print("[*] Modifying property 'value'")
    u.value = "new value!"


def main():
    asyncio.run(coro_main())


main()
