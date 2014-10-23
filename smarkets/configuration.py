import os

from six.moves import configparser


class ConfigurationReader(object):

    '''
    Reads a configuration from a series of "inheriting" .ini files.
    You may specify what config file your file inherits from like this::

        [inherit]
        from=other.conf

    Moreover files of the same name may be present in multiple directories ConfigurationReader
    is set to look for config files - in this case it will read configuration from all of them
    but in reverse order. For example, let's have:

        * ``B.conf`` inherits from ``A.conf''
        * files present:

            * ``/etc/conf/B.conf``
            * ``/home/conf/A.conf``
            * ``/home/conf/B.conf``
        * reader configured like this::

            reader = ConfigurationReader(('/etc/conf', '/home/conf'))

        Order in which files will be read:

            * ``/home/conf/A.conf``
            * ``/home/conf/B.conf``
            * ``/etc/conf/B.conf``
    '''

    def __init__(self, directories, parser_class=configparser.SafeConfigParser):
        '''
        :type directories: tuple or list of strings
        :type parser_class: subclass of ConfigParser
        '''
        self.directories = directories
        self.parser_class = parser_class

    def read(self, filename):
        '''
        Reads the configuration into new instance of :py:attr:`parser_class`.
        :rtype: ConfigParser
        '''
        config = self.parser_class()
        self.read_into(filename, config)
        return config

    def read_into(self, filename, config):
        '''
        Reads the configuration into config object.
        :type config: ConfigParser
        '''
        # Fire off recursive loading to get dependencies
        to_load = list(self._get_dependencies(filename))
        config.read(to_load)

    def _get_dependencies(self, filename):
        # Find the first of the possible files which exists
        paths = [os.path.join(directory, filename) for directory in self.directories]
        found = [path for path in paths if os.path.isfile(path)]

        if not found:
            raise ValueError("Cannot find the file %r (checked in %s)" % (
                filename, ", ".join(self.directories)))

        ancestors_first = tuple(reversed(found))

        tempconfig = self.parser_class()
        tempconfig.read(ancestors_first)

        # See if there's a inherit clause
        try:
            base = tempconfig.get("inherit", "from")
            for item in self._get_dependencies(base):
                yield item
        except (configparser.NoOptionError, configparser.NoSectionError):
            pass

        # Yell about misspellings
        if tempconfig.has_section("inherits"):
            raise ValueError(
                "Your configuration file has an [inherits] section - the correct name is [inherit].")

        # Return ourselves and our parent
        for path in ancestors_first:
            yield path
