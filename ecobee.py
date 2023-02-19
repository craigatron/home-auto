import datetime

import requests


class EcobeeClient:
    TOKEN_URL = 'https://api.ecobee.com/token'
    API_URL = 'https://api.ecobee.com/1'

    def __init__(self, client_id, refresh_token):
        self.client_id = client_id
        self.refresh_token = refresh_token
        self.access_token = None
        self.access_token_exp = None

    def auth(self):
        url = f'{EcobeeClient.TOKEN_URL}?grant_type=refresh_token&refresh_token={self.refresh_token}&client_id={self.client_id}'
        token_resp = requests.get(url, timeout=10)
        self.access_token = token_resp.json()['access_token']
        self.access_token_exp = datetime.datetime.now() + datetime.timedelta(
            hours=1)

    def _make_request(self, url, data=None):
        if not self.access_token or datetime.datetime.now(
        ) > self.access_token_exp:
            self.auth()
        headers = {'Authorization': f'Bearer {self.access_token}'}
        if data:
            return requests.post(url, json=data, headers=headers,
                                 timeout=10).json()
        else:
            return requests.get(url, headers=headers, timeout=10).json()

    def is_fan_on(self) -> bool:
        status_resp = self._make_request(
            f'{EcobeeClient.API_URL}/thermostat?format=json&body={{"selection":{{"selectionType":"registered","selectionMatch":"","includeRuntime":true}}}}'
        )
        print('Current thermostat status: ' + str(status_resp))
        ts = status_resp['thermostatList'][0]
        return ts['runtime']['desiredFanMode'] == 'on'

    def set_fan_hold(self) -> bool:
        hold_json = {
            'selection': {
                'selectionType': 'registered',
                'selectionMatch': ''
            },
            'functions': [{
                'type': 'setHold',
                'params': {
                    'holdType': 'holdHours',
                    'holdHours': 1,
                    'fan': 'on'
                }
            }]
        }
        resp = self._make_request(
            f'{EcobeeClient.API_URL}/thermostat?format=json', data=hold_json)
        return resp['status']['code'] == 0
