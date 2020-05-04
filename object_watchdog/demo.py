import uuid
import asyncio
import dataclasses

from functools import partial

try:
    import ujson as json
except ImportError:
    import json

from typing import Dict, List, Callable
from dataclasses import dataclass, field


def new__setattr__(self, class_name, key, value):

    if self.__instance__ and not key.startswith("_"):
        if not key.startswith("_"):
            for coro in self.__callbacks__:
                t = asyncio.create_task(coro(self, class_name, key, value))

                # if self.track_tasks:
                #     self._pending_tasks.append(t)

            for f in self.__cache_callbacks__:
                print("Cache: ", key, "#", value)
                f()

    setattr(self, key, value)


class TrackableObject(type):
    __instance__ = False
    __callbacks__ = []

    def __new__(cls, clsname, bases, dct):
        o = super(TrackableObject, cls).__new__(cls, clsname, bases, dct)
        o.__instance__ = False
        o.__callbacks__ = []
        o.__cache_callbacks__ = []
        o.add_callback = lambda self, x: self.__callbacks__.append(x)
        o.add_cache_callback = lambda self, x: self.__cache_callbacks__.append(x)
        o.__setattr__ = partial(new__setattr__, o, clsname)
        return o

    def __call__(cls, *args, **kwargs):
        if dataclasses.is_dataclass(cls):
            o = super().__call__(*args, **kwargs)
        else:
            o = super().__call__()
        o.__callbacks__ = TrackableObject.__callbacks__.copy()
        o.__pending_tasks__ = []
        o.__cache_callbacks__ = []
        o.__json_cache__ = None
        o.__instance__ = True

        return o

    @staticmethod
    def add_global_callback(callback: Callable):
        TrackableObject.__callbacks__.append(callback)


@dataclass(init=True)
class OauthProvider:
    id: str
    email: str
    username: str
    picture: str
    first_name: str = None
    last_name: str = None
    link: str = None
    locale: str = None
    city: str = None
    country: str = None
    gender: str = None


# @dataclass
# class User2(metaclass=TrackableObject):
#     ppp: str


#
# @dataclass
# class Meta(type):
#     # def __new__(metacls, name, bases, namespace, **kwargs):
#     #     print(name, '__new__ was called')
#     #     return super().__new__(metacls, name, bases, namespace, **kwargs)
#     #
#     # def __init__(self, name, bases, namespace, **kwargs):
#     #     print(name, '__init__ was called')
#
#     def __call__(self, *args, **kwargs):
#         print(args, kwargs)
#         print('__call__ was called')
#         o = type.__call__(self, *args, **kwargs)
#         o.callbacks = []
#         o.json_cache = None
#         o.pending_tasks = []
#         o.add_callback = lambda self, x: self.callbacks.append(x)
#
#         return o
#
#     @staticmethod
#     def add_something():
#         print("static")


@dataclass
class User(metaclass=TrackableObject):
    # class User:
    #     __metaclass__ = TrackableObject
    username: str
    password: str
    user_id: str = None
    email: str = None
    first_name: str = None
    picture: str = None
    # providers: Dict[str, OauthProvider] = None
    # roles: List[str] = None
    # allowed_apps: List[str] = None

    # picture: str = None
    # providers: Dict[str, OauthProvider] = {}
    providers: Dict[str, OauthProvider] = field(default_factory=dict)
    # roles: List[str] = []
    # allowed_apps: List[str] = []
    #
    # def __init__(self,
    #              username: str,
    #              password: str,
    #              user_id: str = None,
    #              email: str = None,
    #              first_name: str = None,
    #              picture: str = None,
    #              providers: Dict[str, OauthProvider] = None,
    #              roles: List[str] = None,
    #              allowed_apps: List[str] = None,
    #              ):
    #     self.email = email
    #     self.picture = picture
    #     self.password = password
    #     self.username = username
    #     self.first_name = first_name
    #     self.user_id = user_id or uuid.uuid4().hex
    #
    #     self.roles = roles or []
    #     self.providers = providers or {}
    #     self.allowed_apps = allowed_apps or []
    #
    #     self.__instance__: bool = True

    @classmethod
    def from_json(cls, json_data: str):
        json_loaded = json.loads(json_data)

        json_loaded["providers"] = {
            x: OauthProvider(**y)
            for x, y in json_loaded["providers"].items()
        }

        return cls(**json_loaded)

    def to_json(self) -> str:
        if not self.__json_cache__:
            self.__json_cache__ = self.__build__json__()

        return self.__json_cache__

    def __build__json__(self):
        if self.__instance__:
            print("Cache json")
            _dump_obj_ = {
                x: y for x, y in self.__dict__.items()
                if not x.startswith("_") or x == "providers"
            }
            _dump_obj_["providers"] = {
                x: y.__dict__ for x, y in self.providers.items()
            }

            return json.dumps(_dump_obj_)
        else:
            return ""

    # def __setattr__(self, key, value):
    #     print("New setattr")
    #     # if self.__instance__ and not key.startswith("_"):
    #     if not key.startswith("_"):
    #         for coro in self.callbacks:
    #             t = asyncio.create_task(coro(key, value))
    #
    #             # if self.track_tasks:
    #             #     self._pending_tasks.append(t)
    #
    #         if hasattr(self, "__build__json__"):
    #             self.__build__json__()
    #
    #     self.__dict__[key] = value


async def main():
    async def callback(obj, class_name, k, v):
        print("##### Global Callback !!", str(obj.user_id), "#", class_name, "#", k, v)

    async def local_callback(obj, class_name, k, v):
        print("##### Local callback", str(obj), k, v)

    TrackableObject.add_global_callback(callback)

    u = User(username="asdfasdf", password="asdfasdf")
    u.add_cache_callback(u.__build__json__)
    u.add_callback(local_callback)
    u.providers["one"] = OauthProvider(
        id="asdf",
        email="asdf",
        picture="asdf",
        username="asdf"
    )
    u.providers["two"] = OauthProvider(
        id="asdf",
        email="asdf",
        picture="asdf",
        username="asdf"
    )
    print(u.__callbacks__)
    print(u)
    u.user_id = "XXXX"
    js = u.to_json()
    # u = User.from_json(js)
    # print(u)

if __name__ == '__main__':
    asyncio.run(main())
