#!/usr/bin/env python3

import tarfile
import hashlib
from datetime import datetime
from pathlib import Path

class ArchiveException(Exception):
    pass

class Archive:
    """Create an Archive that can be packaged and unpackaged to and from
    a TAR with GZIP compression.
    """
    def __init__(self, froot, fitems, base_name="Archive", packed=False):
        self._set_root(froot)
        self.__items = []
        self._set_items(fitems)
        self._set_name(base_name)
        self.__packed = packed
        self.__timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")


    def is_packed(self):
        """Check if the archive has been zipped and compressed."""
        return self.__packed


    def get_root(self):
        """Root directory of all of the targeted files and directories."""
        return self.__root


    def get_items(self):
        """Targeted files and directories for the archive."""
        return self.__items


    def get_name(self, packed=False):
        """Returns the archive's base name with a timestamp and file
        extension. Passing 'packed' changes the file extension
        between ".tar" and ".tgz"
        """
        extension = ".tar"
        if packed:
            extension = ".tgz"
        return f"{self.__base_name}-{self.__timestamp}{extension}"


    def get_md5(self):
        if not self.is_packed():
            raise ArchiveException(
                "Archive needs to be packed before generating md5sum."
            )
        with open(self.get_name(packed=True), "rb") as f:
            fhash = hashlib.md5()
            chunk = f.read(8192)
            while chunk:
                fhash.update(chunk)
                chunk = f.read(8192)
        return fhash.hexdigest()



    def _set_root(self, root):
        """Validates that the root directory exists and sets it."""
        if not self.is_valid_dir(root):
            raise ArchiveException("'root directory' provided is not valid.")
        self.__root = root


    def _set_items(self, items):
        """Checks each targeted directory and file and verifies that it
        exists. If it does exist, it will be saved.
        """
        for item in items:
            if self.is_valid_item(item):
                self.__items.append(item)
                continue
            # Check if root + item is valid.
            alt_item = Path(self.__root) / item
            if self.is_valid_item(alt_item):
                self.__items.append(item)


    def _set_name(self, name):
        """Set the name of the archive, defaulting to "Archive" if one was not
        provided.
        """
        # Prevent blank / empty / None strings.
        if not name.strip():
            name = "Archive"
        self.__base_name = name.strip()


    def pack(self):
        with tarfile.open(self.get_name(packed=True), "w:gz") as tar:
            for item in self.get_items():
                tar.add(Archive.join_path(self.get_root(), item), item)
        self.__packed = True


    @staticmethod
    def is_valid_dir(directory):
        """Wrapper for Pathlib .is_dir() to check if it passed item is
        valid.
        """
        return Path(directory).is_dir()


    @staticmethod
    def is_valid_file(fname):
        """Wrapper for Pathlib .is_file() to check if it passed item is
        valid.
        """
        return Path(fname).is_file()


    @staticmethod
    def is_valid_item(item):
        """Checks if the passed item is a directory or a file."""
        return Archive.is_valid_dir(item) or Archive.is_valid_file(item)


    @staticmethod
    def join_path(root, ext):
        full = Path(root) / ext
        if not Archive.is_valid_item(full):
            return None

        return full
