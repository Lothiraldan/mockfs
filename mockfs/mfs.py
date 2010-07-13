"""mockfs: A simple mock filesystem for unit tests."""

import os
import glob

from mockfs import util


class MockFS(object):
    """
    MockFS implementation object

    Provides stubs for functions in :mod:`os`, :mod:`os.path`, and :mod:`glob`.

    """

    def __init__(self, entries=None, pathmap=None):
        self._entries = util.build_nested_dict(entries)
        self._pathmap = pathmap
        self._inwalk = False
        self._path = None
        self._walkdir = self._entries

    def add_entries(self, entries):
        """Add new entries to mockfs."""
        new_entries = util.build_nested_dict(entries)
        util.merge_dicts(new_entries, self._entries)

    def exists(self, path):
        """
        Return True if path exists

        Implements the :func:`os.path.exists` interface.

        """
        path = util.sanitize(path)
        dirent = self._direntry(os.path.dirname(path))
        if path == '/':
            return bool(dirent)
        return bool(dirent) and os.path.basename(path) in dirent

    def isdir(self, path):
        """
        Return True if path is a directory

        Implements the :func:`os.path.isdir` interface.

        """
        path = util.sanitize(path)
        return type(self._direntry(path)) is dict

    def isfile(self, path):
        """
        Return True if path is a file

        Implements the :func:`os.path.isfile` interface.

        """
        return self.exists(path) and not self.isdir(path)

    def islink(self, path):
        """
        Return True if path is a symlink

        .. note::

            Currently hard-wired to return False

        """
        path = util.sanitize(path)
        return False

    def listdir(self, path):
        """
        Return the directory contents of 'path'

        Implements the :func:`os.listdir` interface.
        :param path: filesystem path

        """
        path = util.sanitize(path)
        direntry = self._direntry(path)
        if direntry:
            entries = list(direntry.keys())
            entries.sort()
            return entries
        return []

    def walk(self, path):
        """
        Walk a filesystem path

        Implements the :func:`os.walk` interface.

        """
        path = util.sanitize(path)
        entries = []
        inspect = [path]
        while True:
            dirstack = []
            for entry in inspect:
                dirent = self._direntry(entry)
                dirs = []
                files = []
                if dirent:
                    for e in dirent:
                        if type(dirent[e]) is dict:
                            dirs.append(e)
                        else:
                            files.append(e)
                yield (entry, dirs, files)
                dirstack.extend([os.path.join(entry, d) for d in dirs])
            inspect = dirstack
            if not inspect:
                break
        raise StopIteration

    def _direntry(self, path):
        """Return the directory "dict" entry for a path"""
        path = util.sanitize(path)
        if path == '/':
            return self._entries
        elts = path.split('/')[1:]
        current = self._entries
        retval = None
        for elt in elts:
            if elt in current:
                retval = current[elt]
                current = current[elt]
            else:
                return None
        return retval
