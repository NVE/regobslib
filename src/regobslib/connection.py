"""Network code interfacing with Regobs v5
"""

# To enable postponed evaluation of annotations (default for 3.10)
from __future__ import annotations

import pprint
from copy import deepcopy
from typing import Type, Optional, Iterable, Iterator, Union, List

from enum import IntEnum
import datetime as dt

import requests

from . import aps
from .region import SnowRegion
from .submit import SnowRegistration, Registration, ObsJson, Observer, Observation, Incident, AvalancheObs, DangerSign, \
    AvalancheActivity, Weather, SnowCover, CompressionTest, SnowProfile, AvalancheProblem, DangerAssessment, Note
from .misc import TZ, ApiError, NotAuthenticatedError, NoObservationError

__author__ = 'arwi'

API_TEST = "https://test-api.regobs.no/v5"
AUTH_TEST = "https://nveb2c01test.b2clogin.com/nveb2c01test.onmicrosoft.com/oauth2/v2.0/token?p=B2C_1_ROPC_Auth"
API_PROD = "https://api.regobs.no/v5"
AUTH_PROD = "https://nveb2c01prod.b2clogin.com/nveb2c01prod.onmicrosoft.com/oauth2/v2.0/token?p=B2C_1_ROPC_Auth"
APS_PROD = "https://h-web03.nve.no/apsApi/TimeSeriesReader.svc/DistributionByDate/met_obs_v2.0"


class Connection:
    class Language(IntEnum):
        NORWEGIAN = 1
        ENGLISH = 2

    language = Language.NORWEGIAN

    def __init__(self, prod: bool):
        """A connection to send and fetch information from Regobs

        @param prod: Whether to connect to the production server (true) or the test server (false).
        """
        self.expires = None
        self.session = requests.Session()
        self.guid = None
        self.username = None
        self.password = None
        self.client_id = None
        self.token = None
        self.authenticated = False
        self.prod = prod

    def authenticate(self, username: str, password: str, client_id: str, token: str = None) -> Connection:
        """Authenticate to be able to use the Connection to submit registrations.

        @param username: NVE Account username (make sure to use the relevant kind of NVE Account (prod/test)).
        @param password: NVE Account password.
        @param client_id: NVE Account client ID.
        @param token: Regobs API token. This will be deprecated and made optional in the near future.
        @return: self, authenticated.
        """
        self.username = username
        self.password = password
        self.client_id = client_id
        self.token = token

        if token is not None:
            headers = {"regObs_apptoken": self.token}
        else:
            headers = {}
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

    def submit(self, registration: SnowRegistration, language: Language = None) -> Registration:
        """Submit a SnowRegistration to Regobs.

        @param registration: A prepared SnowRegistation.
        @return: A dictionary corresponding to the submitted registration. This is subject to change.
        """
        if not self.authenticated:
            raise NotAuthenticatedError("Connection not authenticated.")

        if language is not None:
            self.language = language

        if self.expires < TZ.localize(dt.datetime.now()) + dt.timedelta(seconds=60):
            return self.authenticate(self.username, self.password, self.client_id, self.token).submit(
                registration)

        if not registration.any_obs:
            raise NoObservationError("No observation in registration.")

        for registration_type, images in registration.images.items():
            for image in images:
                with open(image.file_path, "rb") as file:
                    body = {"file": (image.file_path, file, image.mime)}
                    img_id = self.session.post(f"{API_PROD if self.prod else API_TEST}/Attachment/Upload", files=body)
                    if img_id.status_code != 200:
                        raise ApiError(img_id.content)
                    image.uuid = img_id.json()

        reg_id = self.session.post(f"{API_PROD if self.prod else API_TEST}/Registration", json=registration.serialize())
        if reg_id.status_code != 200:
            raise ApiError(reg_id.content)
        reg_id = reg_id.json()["RegId"]

        return self.get(reg_id)

    def get(self, registration_id: int) -> SnowRegistration:
        """Get a specific registration with a known id.

        @param: registration_id: The ID of the sought registration
        @return: The Snow
        """
        url = f"{API_PROD if self.prod else API_TEST}/Registration/{registration_id}/{self.language}"
        returned_reg = self.session.get(url)
        if returned_reg.status_code != 200:
            raise ApiError(returned_reg.content)
        return SnowRegistration.deserialize(returned_reg.json())

    def get_aps(self,
                from_date: Optional[dt.date],
                to_date: Optional[dt.date] = None,
                regions: List[SnowRegion] = None) -> aps.Aps:
        if to_date is None:
            to_date = from_date
        elif to_date <= from_date:
            raise ValueError("to_date must not be before or equal to from_date")
        if regions is None:
            regions = [r for r in SnowRegion if r > SnowRegion.SVALBARD_SOR]
        elif any([region <= SnowRegion.SVALBARD_SOR for region in regions]):
            raise ValueError("APS download is not supported for Svalbard")
        from_date -= dt.timedelta(days=1)
        to_date -= dt.timedelta(days=2)

        data = None
        data_types = [
            aps.Precip,
            aps.PrecipMax,
            aps.Temp,
            aps.Wind,
            aps.SnowDepth,
            aps.NewSnow,
            aps.NewSnowMax,
        ]
        for region in regions:
            for data_type in data_types:
                url = f"{APS_PROD}/{data_type.WEATHER_PARAM}/24/{region}/{from_date}/{to_date}"
                response = self.session.get(url)
                json = response.json()
                if data is None:
                    data = aps.Aps.deserialize(json, data_type)
                else:
                    data = data.assimilate(aps.Aps.deserialize(json, data_type))
        return data

    def search(self,
               registration_type: Type[Registration],
               observation_types: Optional[List[Type[Observation]]] = None,
               observer_competences: Optional[List[Observer.Competence]] = None,
               regions: Optional[List[SnowRegion]] = None,
               from_obs_time: Optional[dt.datetime] = None,
               to_obs_time: Optional[dt.datetime] = None,
               from_change_time: Optional[dt.datetime] = None,
               to_change_time: Optional[dt.datetime] = None,
               group_id: Optional[int] = None,
               observer_id: Optional[int] = None,
               observer_nickname: Optional[str] = None,
               location_id: Optional[int] = None,
               text_search: Optional[str] = None):
        if not isinstance(registration_type, type):
            raise ValueError("registration_type should be a type (uninstatiated class), not an object.")
        else:
            reg_instance = object.__new__(registration_type)
        if type(reg_instance) == Registration:
            raise ValueError("registration_type must be a subclass of Registration, it can not be Registration itself.")
        if not isinstance(reg_instance, Registration):
            raise ValueError("registration_type must be a subclass of Registration.")

        if observation_types is None:
            observation_types = [
                Incident,
                AvalancheObs,
                DangerSign,
                AvalancheActivity,
                Weather,
                SnowCover,
                CompressionTest,
                SnowProfile,
                AvalancheProblem,
                DangerAssessment,
                Note,
            ]

        if isinstance(reg_instance, SnowRegistration):
            query = {
                "SelectedGeoHazards": [registration_type.GEO_HAZARD],
                "SelectedRegistrationTypes": [{"id": obs_type.OBSERVATION_TYPE} for obs_type in observation_types],
                "GroupId": group_id,
                "ObserverId": observer_id,
                "ObserverCompetence": observer_competences,
                "ObserverNickName": observer_nickname,
                "FromDtObsTime": from_obs_time,
                "ToDtObsTime": to_obs_time,
                "FromDtChangeTime": from_change_time,
                "ToDtChangeTime": to_change_time,
                "SelectedRegions": regions,
                "LocationId": location_id,
                "TextSearch": text_search,
            }
            return Result(self, query)
        else:
            raise ValueError("Could not handle registration_type. This should never happen. Contact arwi@nve.no.")


class Result(Iterable):
    class ResultIter(Iterator):
        def __init__(self, parent: Result):
            self.parent = parent
            self.offset = parent.start
            self.current = parent.start
            self.cache = []

        def __next__(self) -> SnowRegistration:
            if not self.cache:
                self.offset = self.current
                search_body = deepcopy(self.parent.search_body)
                search_body["Offset"] = self.offset
                search_body["NumberOfRecords"] = 50

                url = f"{API_PROD if self.parent.connection.prod else API_TEST}/Search"
                failed = 0
                while True:
                    returned_result = self.parent.connection.session.post(url, json=search_body)
                    if returned_result.status_code != 200:
                        failed += 1
                        if failed >= 5:
                            raise ApiError(returned_result.content)
                    else:
                        break
                self.cache = list(map(lambda x: SnowRegistration.deserialize(x), returned_result.json()))

            try:
                elem = self.cache[self.parent.step - 1]
            except IndexError:
                raise StopIteration()
            below_max = self.current < self.parent.stop if self.parent.stop is not None else True
            done = not self.cache
            self.cache = self.cache[self.parent.step:]
            self.current += self.parent.step

            if not done and below_max:
                return elem
            else:
                raise StopIteration()

        def __iter__(self) -> Iterator:
            return Result.ResultIter(self.parent)

    def __init__(self, connection: Connection, search_body: ObsJson, start: int = 0, stop: int = None, step: int = 1):
        self.step = step if step is not None else 1
        if self.step <= 0:
            raise ValueError("Given step size not supported")

        self.connection = connection
        self.search_body = search_body
        self.start = start
        self.stop = stop

    def __len__(self) -> int:
        url = f"{API_PROD if self.connection.prod else API_TEST}/Search/Count"
        search_len = self.connection.session.post(url, json=self.search_body)
        if search_len.status_code != 200:
            raise ApiError(search_len.content)
        search_len = search_len.json()["TotalMatches"]
        length = min(self.stop, search_len) if self.stop is not None else search_len
        length -= self.start
        length = length if length > 0 else 0
        length = length // self.step + int(bool(length % self.step)) if length else 0
        return length

    def __iter__(self) -> Iterator:
        return Result.ResultIter(self)

    def __getitem__(self, offset: Union[int, slice]) -> Union[SnowRegistration, Iterator[SnowRegistration]]:
        if isinstance(offset, int):
            if offset < 0:
                raise TypeError()

            search_body = deepcopy(self.search_body)
            search_body["Offset"] = offset
            search_body["NumberOfRecords"] = 1

            url = f"{API_PROD if self.connection.prod else API_TEST}/Search"
            returned_result = self.connection.session.post(url, json=search_body)
            if returned_result.status_code != 200:
                raise ApiError(returned_result.content)
            returned_result = list(map(lambda x: SnowRegistration.deserialize(x), returned_result.json()))

            if returned_result:
                return returned_result.pop(0)
            else:
                raise IndexError()

        if isinstance(offset, slice):
            if offset.start is not None and offset.start < 0:
                raise TypeError("start must be >= 0")
            if not any(e is None for e in [offset.stop, offset.start]) and offset.stop < offset.start:
                raise TypeError("stop must be >= start")
            elif not any(e is None for e in [offset.start, self.start, self.step]):
                start = offset.start * self.step + self.start
            elif not any(e is None for e in [offset.start, self.start]):
                start = offset.start + self.start
            else:
                start = offset.start if offset.start is not None else self.start

            if not any(e is None for e in [offset.stop, self.start, self.stop, self.step]):
                stop = min(offset.stop * self.step + self.start, self.stop)
            elif not any(e is None for e in [offset.stop, self.start, self.stop, offset.step]):
                stop = min(offset.stop * offset.step + self.start, self.stop)
            elif not any(e is None for e in [offset.stop, self.start, self.stop]):
                stop = min(offset.stop + self.start, self.stop)
            elif not any(e is None for e in [offset.stop, self.start]):
                stop = offset.stop + self.start
            elif offset.stop is not None:
                stop = offset.stop
            else:
                stop = self.stop

            step = offset.step * self.step if offset.step is not None else self.step
            return Result(self.connection, self.search_body, start, stop, step)

    def __str__(self) -> str:
        return pprint.pformat(list(map(lambda x: x.to_dict(), self)))
