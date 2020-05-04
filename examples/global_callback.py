import asyncio

from typing import Dict
from dataclasses import dataclass, field

from object_watchdog import ObjectWatchdog


@dataclass
class MyClass(metaclass=ObjectWatchdog):
    value: str
    my_dict: Dict = field(default_factory=dict)


@dataclass
class MyClass2(metaclass=ObjectWatchdog):
    value: str
    my_dict: Dict = field(default_factory=dict)


async def coro_local_callback(instance, klass_name, key, value):
    print(f"[!] New change local callback in key '{key}'. New value '{value}'")


async def coro_global_callback(instance, klass_name, key, value):
    print(f"[!] New change global callback in instance '{repr(instance)}' key '{key}'. New value '{value}'")


async def coro_main():

    ObjectWatchdog.add_global_callback(coro_global_callback)

    u1 = MyClass(value="class 1", my_dict={"k": "v"})
    u1.add_async_callback(coro_local_callback)

    u2 = MyClass2(value="class 2", my_dict={"k": "v"})

    print("[*] Modifying property 'value'")
    u1.value = "new value!"
    u2.value = "new value!"


def main():
    asyncio.run(coro_main())


main()
