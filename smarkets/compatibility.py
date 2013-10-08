import socket
from logging.handlers import SysLogHandler

from six import text_type

__all__ = ['configparser', 'UTFFixedSysLogHandler']

try:
    import ConfigParser as configparser
except ImportError:
    import configparser


class UTFFixedSysLogHandler(SysLogHandler):

    """
    Python 2.6 backport of Python 2.7 SysLogHandler.
    This handler should be compatible with Python > 2.6 as well.
    Fixes BOM issue, bug Reference: http://bugs.python.org/issue7077
    """

    def emit(self, record):
        """
        Emit a record.

        The record is formatted, and then sent to the syslog server.  If
        exception information is present, it is NOT sent to the server.
        """
        msg = self.format(record) + '\000'
        """
        We need to convert record level to lowercase, maybe this will
        change in the future.
        """
        prio = '<%d>' % self.encodePriority(self.facility,
                                            self.mapPriority(record.levelname))
        prio = prio.encode('utf-8')

        # Message may be a string. Convert to bytes as required by RFC 5424.
        if isinstance(msg, text_type):
            msg = msg.encode('utf-8')

        msg = prio + msg
        try:
            if self.unixsocket:
                try:
                    self.socket.send(msg)
                except socket.error:
                    self._connect_unixsocket(self.address)
                    self.socket.send(msg)
            elif getattr(self, 'socktype', socket.SOCK_DGRAM):
                self.socket.sendto(msg, self.address)
            else:
                self.socket.sendall(msg)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)
