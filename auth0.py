import time
from typing import Dict

import requests


class Auth0ManagementClient:
    def __init__(self, domain, client_id, client_secret, audience):
        self.domain = domain
        self.client_id = client_id
        self.client_secret = client_secret
        self.audience = audience
        self.token = None
        self.token_expiry = 0

    def _get_token(self):
        response = requests.post(
            f"https://{self.domain}/oauth/token",
            json={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "audience": self.audience,
            },
        )
        data = response.json()
        self.token = data["access_token"]
        self.token_expiry = time.time() + data["expires_in"] - 60

    def get_token(self):
        if not self.token or time.time() > self.token_expiry:
            self._get_token()
        return self.token

    def get_users_by_org(self, org_id):
        token = self.get_token()
        headers = {"Authorization": f"Bearer {token}"}
        url = f"https://{self.domain}/api/v2/organizations/{org_id}/users"
        response = requests.get(url, headers=headers)
        return response.json()
