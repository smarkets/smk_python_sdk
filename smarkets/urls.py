"Smarkets helpers for HTTP requests"
# Copyright (C) 2011 Smarkets Limited <support@smarkets.com>
#
# This module is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.php
import logging
import urllib2

from smarkets.exceptions import InvalidUrlError, DownloadError


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
    except urllib2.URLError as exc:
        if exc.args and isinstance(exc.args[0], str):
            raise InvalidUrlError(exc.args[0])
        else:
            raise DownloadError(exc.reason)
