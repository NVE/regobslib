"""Network code interfacing with Regobs v5
"""

# To enable postponed evaluation of annotations (default for 3.10)
from __future__ import annotations
from enum import IntEnum
import datetime as dt

import requests

from .submit import SnowRegistration
from .misc import TZ, ApiError, NotAuthenticatedError, NoObservationError

__author__ = 'arwi'

API_TEST = "https://test-api.regobs.no/v5"
AUTH_TEST = "https://nveb2c01test.b2clogin.com/nveb2c01test.onmicrosoft.com/oauth2/v2.0/token?p=B2C_1_ROPC_Auth"
API_PROD = "https://api.regobs.no/v5"
AUTH_PROD = "https://nveb2c01prod.b2clogin.com/nveb2c01prod.onmicrosoft.com/oauth2/v2.0/token?p=B2C_1_ROPC_Auth"


class Connection:
    class Language(IntEnum):
        NORWEGIAN = 1
        ENGLISH = 2

    def __init__(self):
        self.expires = None
        self.session = None
        self.guid = None
        self.username = None
        self.password = None
        self.client_id = None
        self.token = None
        self.authenticated = False
        self.prod = False

    def authenticate(self, username: str, password: str, client_id: str, token: str, prod: bool) -> Connection:
        self.username = username
        self.password = password
        self.client_id = client_id
        self.token = token
        self.prod = prod

        headers = {"regObs_apptoken": self.token}
        self.session = requests.Session()
        self.session.headers.update(headers)

        url = AUTH_PROD if self.prod else AUTH_TEST
        body = {
            "client_id": client_id,
            "scope": f"openid {client_id}",
            "grant_type": "password",
            "username": self.username,
            "password": self.password,
        }
        response = requests.post(url, data=body).json()
        token = response["access_token"]
        expires_in = int(response["expires_in"])

        headers["Authorization"] = f"Bearer {token}"
        self.session.headers.update(headers)
        self.expires = TZ.localize(dt.datetime.now()) + dt.timedelta(seconds=expires_in)

        guid = self.session.get(f"{API_PROD if self.prod else API_TEST}/Account/Mypage")
        if guid.status_code != 200:
            raise ApiError(guid.content)
        self.guid = guid.json()["Guid"]

        self.authenticated = True
        return self

    def submit(self, registration: SnowRegistration, language: Language = 1) -> dict:
        if not self.authenticated:
            raise NotAuthenticatedError("Connection not authenticated.")

        if self.expires < TZ.localize(dt.datetime.now()) + dt.timedelta(seconds=60):
            return self.authenticate(self.username, self.password, self.client_id, self.token, self.prod).submit(
                registration)

        if not registration.any_obs:
            raise NoObservationError("No observation in registration.")

        reg_filtered = {k: v for k, v in registration.reg.items() if v}
        reg_id = self.session.post(f"{API_PROD if self.prod else API_TEST}/Registration", json=reg_filtered)
        if reg_id.status_code != 200:
            raise ApiError(reg_id.content)
        reg_id = reg_id.json()["RegId"]

        returned_reg = self.session.get(f"{API_PROD if self.prod else API_TEST}/Registration/{reg_id}/{language}")
        if returned_reg.status_code != 200:
            raise ApiError(returned_reg.content)
        return returned_reg.json()
