from enum import Enum
from http.client import HTTPConnection
import time
import requests
import sys
import jwt
import pyperclip
import json


def timestamp():
    return round(time.time(), 3)


class RESTMethod(Enum):
    RESTLET = 'restlets.api.netsuite.com'
    RESTWEBSERVICE = 'suitetalk.api.netsuite.com'


class HTTPMethod(Enum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'


class SuiteTalk:
    def __init__(self, cli):
        self._cli = cli
        self._access_token = None

    @property
    def access_token(self):
        if self._access_token is None:
            self.request_access_token()
        return self._access_token

    @property
    def cli(self):
        return self._cli

    def request_access_token(self):
        if self._cli.pk[0] == 'p':
            private_key = open(f'{self._cli.pk[1]}', 'rb').read()
        elif self._cli.pk[0] == 'b':
            private_key = self._cli.pk[1]
        else:
            print('can not process private key, please check --help')
            sys.exit()

        audience = f'https://{self._cli.i}.{RESTMethod.RESTWEBSERVICE.value}/services/rest/auth/oauth2/v1/token'
        token_header = {
            'typ': 'JWT',
            'alg': self._cli.alg,
            'kid': self._cli.kid
        }
        token_payload = {
            'iss': self._cli.iss,
            'scope': ['restlets', 'rest_webservices', 'suite_analytics'],
            'aud': audience,
            'exp': timestamp() + (60 * 60),
            'iat': timestamp()
        }
        secret = jwt.encode(token_payload, private_key,
                            algorithm=self._cli.alg, headers=token_header)

        response = requests.request(
            'POST', audience,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data=f'grant_type=client_credentials&client_assertion_type=urn:ietf:params:oauth:client-assertion-type:jwt-bearer&client_assertion={secret}')
        print(response.text)
        self._access_token = json.loads(response.text)['access_token']

        if self._cli.copy:
            pyperclip.copy(self._access_token)
            print('access token copied.')

        return self._access_token

    def request_rest(self, api):
        response = requests.request(
            api['method'],
            api['url'],
            headers={'Authorization': f'Bearer {api["token"]}'})
        print(response.text)

    def request_prepare(self, api):
        req = requests.Request(
            api['method'],
            api['url'],
            headers={'Authorization': f'Bearer {api["token"]}'}).prepare()
        header_info = ''.join(f'{k}: {v}\n' for k, v in req.headers.items())
        return f'---------------------------\r\n{req.method} {req.url} {HTTPConnection._http_vsn_str}\r\n ---Headers:\r\n{header_info}\r\n ---Body:\r\n{req.body}'
