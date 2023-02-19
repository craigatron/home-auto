import requests


class AirthingsClient:
    AUTH_URL = 'https://accounts-api.airthings.com/v1/token'
    AUTH_DATA = {
        'grant_type': 'client_credentials',
        'scope': 'read:device:current_values'
    }
    API_URL = 'https://ext-api.airthings.com/v1'

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = None

    def auth(self):
        token_resp = requests.post(AirthingsClient.AUTH_URL,
                                   data=AirthingsClient.AUTH_DATA,
                                   auth=(self.client_id, self.client_secret),
                                   timeout=10)
        self.token = token_resp.json()['access_token']

    def _make_request(self, url):
        if not self.token:
            self.auth()
        headers = {'Authorization': f'Bearer {self.token}'}
        return requests.get(url, headers=headers, timeout=10).json()

    def get_latest_readings(self, device_id):
        return self._make_request(
            f'{AirthingsClient.API_URL}/devices/{device_id}/latest-samples')
