from __future__ import absolute_import, unicode_literals

from urlparse import parse_qs as _parse_qs

import requests as _requests
import simplejson as _json
from requests_oauthlib import OAuth1 as _OAuth1


class RestAPIClient(object):
    def __init__(self, oauth, api_url, requests=_requests):
        self._oauth = oauth
        self._api_url = api_url
        self._requests = requests

    def _post(self, method):
        result = self._requests.post('%s/%s' % (self._api_url, method), auth=self._oauth)
        return _json.loads(result.text)

    def authenticate(self):
        response = self._post('request_token')
        #TODO: authorize token here
        return response

    @classmethod
    def create(cls, key, secret, auto_authenticate=True, api_url='https://api.smarkets.com'):
        oauth = _OAuth1(key, secret)
        client = cls(oauth, api_url)
        if auto_authenticate:
            client.authenticate()
        return client
