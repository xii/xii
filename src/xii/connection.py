import os
import random
import string
from stat import S_IRWXU

from abc import ABCMeta, abstractmethod


class Connection():
    __metaclass__ = ABCMeta

    def finalize(self):
        pass

    @abstractmethod
    def open(self, path, mode):
        """Open a file

        open files works as python's builtin method. Make sure that the
        path exists on the host where the file will be opend (remote + local)

        Args:
            path:    Path to the file which should be opend
            mode:    Mode in which the file should be opened

            TODO: Add link to builtin method

        Returns:
            The file object for the given path

        Throws:
            Can throw IOError
        """
        pass

    @abstractmethod
    def mkdir(self, directory):
        """Creates a new directory

        Creates one or more directories recursivly.

        Args:
            directory: The path which should be created
        """
        pass

    @abstractmethod
    def stat(self, path):
        """Get stat of a inode

        Args:
            path: path to stat

        Returns:
            the stats object
        """
        pass

    @abstractmethod
    def which(self, executable):
        """Get the path of a executable

        This will return the path to the search exectuable if available

        Args:
            executable:     The application which is searched

        Returns:
            The path to the executable if found, None otherwise
        """
        pass

    @abstractmethod
    def exists(self, path):
        """Check if a path exists.

        Args:
            path:   Path which should be checked

        Returns:
            True if found, False otherwise
        """
        pass

    @abstractmethod
    def user(self):
        """Get current username

        This method also returns the correct user name if a remote host
        is used.

        Returns:
            The name of the current user
        """
        pass

    @abstractmethod
    def user_home(self):
        """Get current user home

        This method also returns the correct user home if a remote host
        is used.

        Returns:
            The path to home for the current user
        """
        pass

    @abstractmethod
    def copy(self, source, dest):
        """Copies data from source to destination

        This copies files on host from source to destination.

        Make sure path exists and is writable!

        Args:
            source: Source of data
            dest: Destination where data should be copied

        Returns:
            True if copying was successfull, False otherwise
        """
        pass

    @abstractmethod
    def upload(self, source, dest):
        """Uploads data to host

        This copies files from local to host. If host is also local
        it copies from local to local.

        Make sure destination exists and has proper rights!

        Args:
            source: Source of data
            dest: Destination of data

        Returns:
            True if transfer was successfull, False otherwise
        """
        pass

    @abstractmethod
    def download(self, source, dest):
        """Downloads data from host

        This copies from host to local. If host is also local
        it copies from local to local.

        Args:
            source: Source of data on host
            dest: Destination on local

        Returns:
            True if transfer was successfull, False otherwise
        """
        pass

    @abstractmethod
    def download_url(self, url, dest):
        """Downloads data from an url

        Make sure dest exists and is writable!

        Args:
            url: URL to data
            dest: Destination where to save the data

        Returns:
            True if transfer was successfull, False otherwise
        """
        pass

    @abstractmethod
    def chmod(self, path, new_mode, append=False):
        """Set permissions for a path

        Without append=True this function overwrites existing
        permissions.

        Args:
            path:       Path where permission should be changed
            new_mode:   New mode for the path
            append:     Just add new permissions to old one
        """
        pass

    @abstractmethod
    def chown(self, path, uid=None, guid=None):
        """Set ownership of a path

        Only change the user id is working like

        ::

            self.chown(some_path, uid=1000)

        Args:
            path:       The patch which should be changed
            uid:        User id which should own the file
            guid:       Group user id which should be owned
        """
        pass

    @abstractmethod
    def get_users(self):
        """Get all users defined

        This method fetches all users defined from the used host (remote +
        local) and returns them.

        Returns:
            A list of all users defined
        """
        pass

    @abstractmethod
    def rm(self, path):
        """Delete a path

        Args:
            path:   Path which should be deleted
        """
        pass

    @abstractmethod
    def get_groups(self):
        """Get all groups with extradata

        This method fetches groups from the used host (remote + local) and
        returns them.

        Returns:
            Returns a list of groups defined in the host system
        """
        pass

    def ensure_path_exists(self, path):
        """Make sure a path exsists if not create it

        When a path is not exisiting, it will be recursivly created

        Args:
            path: The path which should exist
        """
        if self.exists(path):
            return

        self.mkdir(path)
        self.chmod(path, S_IRWXU)

    def mktempdir(self, prefix):
        """Creates a temporary directory under /var/tmp/<user>

        Args:
            prefix: Prefix for the temprary directory
            (eg. xii -> /var/tmp/xii-2d72ddk9d3)

        Returns:
            The path for the new created directory
        """

        suffix = ''.join(random.choice(string.lowercase) for i in range(8))
        path = os.path.join("/var/tmp", prefix + "-" + suffix)

        self.mkdir(path)
        self.chmod(path, S_IRWXU)

        return path

    def call(self, command, *args):
        """run a command

        Args:
            command:    The command to spawn
            *args:      Arguments for the command

        Returns:
            return a tuple with (returncode, output) of the
            executed command
        """
        pass

    def sudo_call(self, command, *args):
        """run a command using sudo

        Args:
            command:    The command to spawn with different rights
            *args:      Arguments for the command

        Returns:
            return a tuple with (returncode, output) of the
            executed command
        """
        pass
