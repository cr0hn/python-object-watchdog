import asyncio

from typing import Callable
from functools import partial


def new__setattr__(self, class_name, key, value):

    setattr(self, key, value)

    if self.__instance__ and not key.startswith("_"):
        for coro in self.__async_callbacks__:
            asyncio.create_task(
                coro(self.__instance_object__, class_name, key, value)
            )

        for fn in self.__callbacks__:
            fn(self.__instance_object__, class_name, key, value)

        for f in self.__cache_callbacks__:
            getattr(self.__instance_object__, f)(self, key)


class ObjectWatchdog(type):
    __instance__ = False
    __callbacks__ = []
    __async_callbacks__ = []
    __cache_callbacks__ = []

    def __new__(cls, clsname, bases, dct):
        o = type.__new__(cls, clsname, bases, dct)

        # Meta info
        o.__instance__ = False
        o.__instance_object__ = None

        # Add methods
        o.add_callback = lambda self, x: self.__callbacks__.append(x)
        o.add_async_callback = lambda self, x: self.__async_callbacks__.append(x)
        o.add_cache_callback = lambda self, x: self.__cache_callbacks__.append(x)

        # Overwrite setattr
        o.__setattr__ = partial(new__setattr__, o, clsname)

        return o

    def __call__(cls, *args, **kwargs):
        o = super().__call__(*args, **kwargs)
        if not hasattr(o, "__callbacks__"):
            o.__callbacks__ = []
        if not hasattr(o, "__async_callbacks__"):
            o.__async_callbacks__ = []
        if not hasattr(o, "__cache_callbacks__"):
            o.__cache_callbacks__ = []

        o.__callbacks__.extend(ObjectWatchdog.__callbacks__.copy())
        o.__async_callbacks__.extend(ObjectWatchdog.__async_callbacks__.copy())
        o.__cache_callbacks__.extend(ObjectWatchdog.__cache_callbacks__.copy())

        o.__instance__ = True
        o.__instance_object__ = o

        return o

    @staticmethod
    def add_global_callback(callback: Callable):
        ObjectWatchdog.__callbacks__.append(callback)

    @staticmethod
    def add_global_async_callback(callback: Callable):
        ObjectWatchdog.__async_callbacks__.append(callback)

    @staticmethod
    def add_global_cache_callback(callback: str):
        ObjectWatchdog.__cache_callbacks__.append(callback)

