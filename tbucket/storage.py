#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of tbucket daemon released under the MIT license.
# See the LICENSE file for more information.

import tornado.gen


class StorageException(Exception):
    """Exception class for exceptions at the storage level"""

    pass


class TObjectStorage(object):
    """Class to store the body of a transient object.

    It's an abstract class to describe the API.

    Attributes:
        uid (str): the uid of the transient object.
    """

    uid = None

    @tornado.gen.coroutine
    def append(self, strg):
        """Appends some string in the storage object.

        You can't use this method anymore after using seek0() or read().

        It's a coroutine decorated generator. So, don't block the event loop
        inside this function. If you have some blocking calls to do, use
        tornado async operations inside.

        Args:
            strg (str): some data to append.

        Raises:
            StorageException: an error occured at the storage level.
        """
        raise NotImplemented()

    @tornado.gen.coroutine
    def destroy(self):
        """Destroys the storage object.

        After this call, the instance is not usable anymore. But we can
        invoke safely this method several times.

        It's a coroutine decorated generator. So, don't block the event loop
        inside this function. If you have some blocking calls to do, use
        tornado async operations inside.

        Raises:
            StorageException: an error occured at the storage level.
        """
        raise NotImplemented()

    @tornado.gen.coroutine
    def flush(self):
        """Closes the storage for writing.

        After this call, the instance is not writable anymore.

        It's a coroutine decorated generator. So, don't block the event loop
        inside this function. If you have some blocking calls to do, use
        tornado async operations inside.

        Raises:
            StorageException: an error occured at the storage level.
        """
        raise NotImplemented()

    @tornado.gen.coroutine
    def seek0(self):
        """Sets the read pointer to the start of the body.

        This method must be called before read().

        It's a coroutine decorated generator. So, don't block the event loop
        inside this function. If you have some blocking calls to do, use
        tornado async operations inside.

        Raises:
            StorageException: an error occured at the storage level.
        """
        raise NotImplemented()

    @tornado.gen.coroutine
    def read(self, size=-1):
        """Reads some bytes in the body and returns them.

        This method reads at most size (-1: no limit) bytes from the read
        pointer and returns them. Then it moves the read pointers to the
        end of the read section.

        When you use this method if the end of the body has been reached,
        the method returns an empty string.

        It's a coroutine decorated generator. So, don't block the event loop
        inside this function. If you have some blocking calls to do, use
        tornado async operations inside.

        Raises:
            tornado.gen.Return: because of tornado.gen.couroutine decorator,
                this exception is raised to return read bytes.
            StorageException: an error occured at the storage level.
        """
        raise NotImplemented()


class TObjectStorageFactory(object):
    """Singleton which makes some TObjectStorage objects.

    It's an abstract class to describe the API and to factorize some code.
    """

    __instance = None

    def __del__(self):
        self.destroy()

    @classmethod
    def get_instance(cls):
        """Class method to get the singleton instance of the class.

        You don't have to override this method.

        Raises:
            StorageException: an error occured at the storage level.
        """
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    @classmethod
    def destroy_instance(cls):
        """Class method to destroy the singleton instance of the class.

        You don't have to override this method (see destroy() instead).

        It must be safe to call this method several times().

        Raises:
            StorageException: an error occured at the storage level.
        """
        if cls.__instance is None:
            return
        cls.__instance.destroy()
        cls.__instance = None

    def destroy(self):
        """Destroys the factory.

        Can be useful for freeing some resources.

        Raises:
            StorageException: an error occured at the storage level
        """
        raise NotImplemented()

    def make_storage_object(self):
        """Makes a new storage object.

        Returns:
            A new storage object (subclass of TObjectStorage).

        Raises:
            StorageException: an error occured at the storage level.
        """
        raise NotImplemented()

    @staticmethod
    def get_name():
        """Returns the name of the storage method implemented

        Returns:
            The name (str) of the storage method implemented
        """
        raise NotImplemented()
