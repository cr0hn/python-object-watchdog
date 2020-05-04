import asyncio
import hashlib

from dataclasses import dataclass, field

from object_watchdog import ObjectWatchdog


@dataclass
class User(metaclass=ObjectWatchdog):
    __cache_callbacks__ = ["__build_hash__"]

    def __init__(self, user: str, password: str):
        self.user = user
        self.password = password
        self.__cached_hash = None

    @property
    def hash(self):
        if not self.__cached_hash:
            self.__build_hash__()
        return self.__cached_hash

    def __build_hash__(self, key: str = None):
        if key and key != "user" and key != "password":
            return

        h = hashlib.sha512()
        h.update(
            f"{self.user}#{self.password}".encode("UTF-8")
        )

        self.__cached_hash = h.hexdigest()


async def coro_main():

    u1 = User(user="john", password="password")

    print("User hash before: ", u1.hash)

    u1.password = "mynewpassword"
    print("User hash after: ", u1.hash)


def main():
    asyncio.run(coro_main())


main()
