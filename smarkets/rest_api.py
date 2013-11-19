from __future__ import absolute_import, unicode_literals

import requests as _requests
import simplejson as _json

from smarkets.errors import Error as _Error


class RestAPIException(_Error):
    '''Base class for every rest API exception'''


class ResourceNotFound(RestAPIException):
    '''Given resource was not found'''


class RestAPIClient(object):
    '''
    Smarkets REST API client. Please use :meth:`create_unauthenticated` to construct
    its instances.
    '''

    def __init__(self, api_url='https://api.smarkets.com', requests=_requests):
        self._api_url = api_url
        self._requests = requests

    def _get(self, method):
        return self._handle_response(self._requests.get('%s/%s' % (self._api_url, method)))

    def _handle_response(self, response):
        result = _json.loads(response.text)
        code = result.get('code', 200)
        if code == 404:
            raise ResourceNotFound(response.url)
        elif code != 200:
            raise RestAPIException('Unexpected response code %s' % (code,), result)

        return result

    def get_popular_events(self):
        return self._get('events/popular')

    def get_top_level_events(self):
        return self._get('events')

    def get_event_by_path(self, path):
        '''
        Get event by its path, for example::

            rest_api.get_event_by_path('/sport/football')

        :raises:
            :ResourceNotFound: No event with such path exists.
        :type path: string
        :rtype: dict
        '''
        transformed_path = path.replace('/events', '').replace('/sports/', '/sport/').lstrip('/')
        return self._get('events/%s' % (transformed_path,))

    @classmethod
    def create_unauthenticated(cls, **kwargs):
        '''
        Create an unauthenticated :class:`RestAPIClient` instance.
        '''
        return cls(**kwargs)
