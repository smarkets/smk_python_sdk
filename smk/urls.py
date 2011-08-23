"Smarkets helpers for HTTP requests"
import logging
import urllib2

import seto.piqi_pb2 as seto

from exceptions import InvalidUrlError, DownloadError


def fetch(url):
    "Fetch a URL and raise the appropriate exception when it fails"
    try:
        logging.debug('fetching url %s', url)
        result = urllib2.urlopen(url)
        logging.debug('got response with code %d', result.code)
        if result.code == 200:
            content_type = result.headers.get('content-type')
            entity_body = result.read()
            logging.debug(
                'returning an entity of type %s with %d bytes',
                content_type, len(entity_body))
            return content_type, entity_body
        raise DownloadError('http status code was not 200: %d', result.code)
    except urllib2.URLError as e:
        if e.args and isinstance(e.args[0], str):
            raise InvalidUrlError(e.args[0])
        else:
            raise DownloadError(e.reason)
