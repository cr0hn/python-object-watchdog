Object Watchdog
===============

This library allow to monitor changes in a Python object and, when some attribute changes, then launch callbacks.

Support this project
====================

Support this project (to solve issues, new features...) by applying the Github "Sponsor" button.

Install
=======

.. code-block:: console

    $ pip install object-watchdog

Callbacks types
===============

There're 3 types of callbacks:

- Async callbacks: launch coroutines as callbacks
- Callbacks: launch functions as callbacks
- Cache callbacks: Launch methods of class to update caches

Global vs local callbacks
=========================

- Local callbacks are called only for these classes that have set the callbacks
- Global callbacks are called for all classes that uses the Object Watchdog

How to usage
============

Object Watchdog should be used as metaclass:

.. code-block:: python

    from object_watchdog import ObjectWatchdog

    class User(metaclass=ObjectWatchdog):
        ...

Defining local callbacks
========================

Callbacks could be defined in running time and in definition.

Definition mode
---------------

At the classes you can put callbacks when any attribute changes, you can define these types of callbacks in these properties:

- `__async_callbacks__`
- `__callbacks__`
- `__cache_callbacks__`

Example:

.. code-block:: python

    async def async_callback(instance, klass_name, key, value):
        print(f"[!] New change local callback in key '{key}'. New value '{value}'")


    async def async_callback2(instance, klass_name, key, value):
        print(f"[0] New change local callback in key '{key}'. New value '{value}'")


    def callback(instance, klass_name, key, value):
        print(f"[!] Sync New change local callback in key '{key}'. New value '{value}'")


    class User(metaclass=ObjectWatchdog):
        __async_callbacks__ = [async_callback, async_callback2]
        __callbacks__ = [callback]
        __cache_callbacks__ = ["__build_hash__"]

        ...

Running time
------------

If you need to add some callback in run time, Metaclass add these methods:

- `add_callback`
- `add_async_callback`
- `add_cache_callback`

.. code-block:: python

    import asyncio

    from typing import Dict
    from dataclasses import dataclass, field

    from object_watchdog import ObjectWatchdog


    @dataclass
    class User(metaclass=ObjectWatchdog):
        user: str
        password: str

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

    async def coro_callback(instance, klass_name, key, value):
        print(f"[!] New change in key '{key}'. New value '{value}'")


    async def main():

        u = User(user="john", password="password")
        u.add_async_callback(coro_callback)
        u.add_cache_callback("__build_hash__")

        print("[*] Modifying property 'value'")
        u.password = "new password!"


    def main():
        asyncio.run(coro_main())


    main()


Defining global callbacks
=========================

Global callback applies to all classes (or dataclasses) that uses ObjectWatchdog as a metaclass.

If you want to call any function / coroutine when some class have been modified, you also can use this method. ObjectWatchdog metaclass has these methods:

- `add_global_callback`
- `add_global_async_callback`
- `add_global_cache_callback`

.. code-block:: python

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
        u2 = MyClass2(value="class 2", my_dict={"k": "v"})

        print("[*] Modifying property 'value'")
        u1.value = "new value!"
        u2.value = "new value!"


    def main():
        asyncio.run(coro_main())


    main()
