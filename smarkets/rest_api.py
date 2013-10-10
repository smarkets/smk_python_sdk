from __future__ import absolute_import, unicode_literals

import requests as _requests
import simplejson as _json


class RestAPIClient(object):
    def __init__(self, api_url, requests=_requests):
        self._api_url = api_url
        self._requests = requests

    def _get(self, method):
        return self._handle_response(self._requests.get('%s/%s' % (self._api_url, method)))

    def _handle_response(self, response):
        result = _json.loads(response.text)
        code = result.get('code', 200)
        if code != 200:
            raise Exception('Unexpected response code %s' % (code,), result)

        return result

    def get_popular_events(self):
        return self._get('events/popular')

    def get_top_level_events(self):
        return self._get('events')

    def get_event_by_url(self, url):
        transformed_url = url.replace('/events', '').replace('/sports/', '/sport/').lstrip('/')
        return self._get('events/%s' % (transformed_url,))

    @classmethod
    def create_unauthenticated(cls, api_url='https://api.smarkets.com'):
        return cls(api_url)
