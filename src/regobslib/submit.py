"""Classes representing the submission forms in Regobs v5
"""

# To enable postponed evaluation of annotations (default for 3.10)
from __future__ import annotations

import pprint
from enum import IntEnum, Enum
from typing import Optional, List, Union, Dict, TypeVar, Type, Callable
import datetime as dt
import mimetypes
import re

from .misc import TZ, NoObservationError, FloatEnum

__author__ = 'arwi'

# PyCharm can not parse this type, but it is correctly defined.
ObsJson = Dict[str,
               Optional[Union[str,
                              int,
                              float,
                              'ObsJson',
                              List['ObsJson']]]]

ObsDict = Dict[str, Optional[Union[str, int, float, List[Union[str, int, float, 'ObsDict']]]]]

T = TypeVar('T')
U = TypeVar('U')


class Serializable:
    def serialize(self) -> ObsJson:
        raise NotImplementedError()

    @staticmethod
    def _clean(json: ObsJson) -> ObsJson:
        return {k: v for k, v in json.items() if v is not None and v != []}


class Deserializable:
    @classmethod
    def deserialize(cls, json: ObsJson) -> Deserializable:
        raise NotImplementedError()

    @staticmethod
    def _convert(json: ObsJson, idx: str, target: Type[T], target_sec: Optional[Type[U]] = int) -> Union[T, U]:
        elem = json[idx] if idx in json else None
        try:
            return target(elem) if elem is not None else None
        except ValueError:
            return target_sec(elem)

    @staticmethod
    def _apply(json: ObsJson, idx: str, apply: Callable[[Union[str, int, float]], T] = None) -> Optional[T]:
        elem = json[idx] if idx in json else None
        return apply(elem) if elem is not None else None

    @staticmethod
    def _deserialize_to(json: ObsJson, idx: str, target: Type[Deserializable]) -> Deserializable:
        elem = json[idx] if idx in json else None
        return target.deserialize(elem) if elem is not None else None


class Dictable:
    def to_dict(self) -> ObsDict:
        raise NotImplementedError()

    def __str__(self) -> str:
        return pprint.pformat(self.to_dict())


class Registration(Serializable, Deserializable, Dictable):
    GEO_HAZARD = None

    def to_dict(self) -> ObsDict:
        raise NotImplementedError()

    def serialize(self) -> ObsJson:
        raise NotImplementedError()

    @classmethod
    def deserialize(cls, json: ObsJson) -> Registration:
        raise NotImplementedError()


class Observation(Serializable, Deserializable, Dictable):
    OBSERVATION_TYPE = None

    def to_dict(self) -> ObsDict:
        raise NotImplementedError()

    def serialize(self) -> ObsJson:
        raise NotImplementedError()

    @classmethod
    def deserialize(cls, json: ObsJson) -> SnowObservation:
        raise NotImplementedError()


class SnowObservation(Observation):
    def to_dict(self) -> ObsDict:
        raise NotImplementedError()

    def serialize(self) -> ObsJson:
        raise NotImplementedError()

    @classmethod
    def deserialize(cls, json: ObsJson) -> SnowObservation:
        raise NotImplementedError()


class SnowRegistration(Registration):
    GEO_HAZARD = 10

    class Source(IntEnum):
        SEEN = 10
        TOLD = 20
        NEWS = 21
        PICTURE = 22
        ASSUMED = 23

    class SpatialPrecision(IntEnum):
        EXACT = 0
        ONE_HUNDRED = 100
        FIVE_HUNDRED = 500
        ONE_KM = 1000
        OVER_KM = -1

    class ObservationType(IntEnum):
        NOTE = 10
        INCIDENT = 11
        DANGER_SIGN = 13
        WEATHER = 21
        SNOW_COVER = 22
        COMPRESSION_TEST = 25
        AVALANCHE_OBS = 26
        DANGER_ASSESSMENT = 31
        AVALANCHE_PROBLEM = 32
        AVALANCHE_ACTIVITY = 33
        SNOW_PROFILE = 36

    def __init__(self,
                 obs_time: dt.datetime,
                 position: Position,
                 spatial_precision: Optional[Union[SnowRegistration.SpatialPrecision, int]] = None,
                 source: Optional[SnowRegistration.Source] = None):
        """A registration corresponding to the ones made using the Snow Registration form in the web app.

        @param obs_time: A localized datetime, denoting the observation time. Use REGOBS_TZ.localize() to localize.
        @param position: The position of the observation. Use WGS84 coordinates.
        @param spatial_precision: The margin of error of the observation position, in meters.
        @param source: What kind of source the knowledge this registration is based upon is based on.
        """
        self.any_obs = False
        self.obs_time = obs_time
        self.position = position
        self.spatial_precision = spatial_precision
        self.source = source
        self.id = None
        self.observer = None

        self.danger_signs = []
        self.avalanche_obs = None
        self.avalanche_activities = []
        self.weather = None
        self.snow_cover = None
        self.compression_tests = []
        self.snow_profile = None
        self.avalanche_problems = []
        self.danger_assessment = None
        self.incident = None
        self.note = None

        self.images = {
            SnowRegistration.ObservationType.NOTE: [],
            SnowRegistration.ObservationType.INCIDENT: [],
            SnowRegistration.ObservationType.DANGER_SIGN: [],
            SnowRegistration.ObservationType.WEATHER: [],
            SnowRegistration.ObservationType.SNOW_COVER: [],
            SnowRegistration.ObservationType.COMPRESSION_TEST: [],
            SnowRegistration.ObservationType.AVALANCHE_OBS: [],
            SnowRegistration.ObservationType.DANGER_ASSESSMENT: [],
            SnowRegistration.ObservationType.AVALANCHE_PROBLEM: [],
            SnowRegistration.ObservationType.AVALANCHE_ACTIVITY: [],
            SnowRegistration.ObservationType.SNOW_PROFILE: [],
        }

    def add_danger_sign(self, danger_sign: DangerSign) -> SnowRegistration:
        """Add a DongerSign. Previously added DongerSigns will still be in the registration.

        @param danger_sign: The DangerSign to add.
        @return: self, with an added danger sign.
        """
        self.any_obs = True
        self.danger_signs.append(danger_sign)
        return self

    def set_avalanche_obs(self, avalanche_obs: AvalancheObs) -> SnowRegistration:
        """Set an AvalancheObs. Previously set AvalancheObs will be overwritten.

        @param avalanche_obs: The AvalancheObs to set.
        @return: self, with the provided AvalancheObs set.
        """
        self.any_obs = True
        self.avalanche_obs = avalanche_obs
        return self

    def add_avalanche_activity(self, avalanche_activity: AvalancheActivity) -> SnowRegistration:
        """Add an AvalancheActivity. Any previously added AvalancheActivity will still be in the registration.

        @param avalanche_activity: The AvalancheActivity to add.
        @return: self, with an added AvalancheActivity.
        """
        self.any_obs = True
        self.avalanche_activities.append(avalanche_activity)
        return self

    def set_weather(self, weather: Weather) -> SnowRegistration:
        """Set a Weather. Previously set Weather will be overwritten.

        @param weather: The Weather to set.
        @return: self, with the provided Weather set.
        """
        self.any_obs = True
        self.weather = weather
        return self

    def set_snow_cover(self, snow_cover: SnowCover) -> SnowRegistration:
        """Set a SnowCover. Previosly set SnowCover will be overwritten.

        @param snow_cover: The SnowCover to set.
        @return: self, with the provided SnowCover set.
        """
        self.any_obs = True
        self.snow_cover = snow_cover
        return self

    def add_compression_test(self, compression_test: CompressionTest) -> SnowRegistration:
        """Add a CompressionTest. Any previously added CompressionTest will still be in the registration.

        @param compression_test: The CompressionTest to add.
        @return: self, with an added CompressionTest.
        """
        self.any_obs = True
        self.compression_tests.append(compression_test)
        return self

    def set_snow_profile(self, snow_profile: SnowProfile) -> SnowRegistration:
        """Set a SnowProfile. Previously set SnowProfile will be overwritten.

        @param snow_profile: The SnowProfile to set.
        @return: self, with the provided SnowProfile set.
        """
        self.any_obs = True
        self.snow_profile = snow_profile
        return self

    def add_avalanche_problem(self, avalanche_problem: AvalancheProblem) -> SnowRegistration:
        """Add an AvalancheProblem. Any previously added AvalancheProblem will still be in the registration.

        @param avalanche_problem: The AvalancheProblem to add.
        @return: self, with an added AvalancheProblem.
        """
        if len(self.avalanche_problems) >= 3:
            raise ValueError("Too many avalanche problems.")

        self.any_obs = True
        self.avalanche_problems.append(avalanche_problem)
        return self

    def set_danger_assessment(self, danger_assessment: DangerAssessment) -> SnowRegistration:
        """Set a DangerAssessment. Previously set DangerAssessment will be overwritten.

        @param danger_assessment: The DangerAssessment to set.
        @return: self, with the provided DangerAssessment set.
        """
        self.any_obs = True
        self.danger_assessment = danger_assessment
        return self

    def set_incident(self, incident: Incident) -> SnowRegistration:
        """Set an Incident. Previously set Incident will be overwritten.

        @param incident: The Incident to set.
        @return: self, with the provided Incident set.
        """
        self.any_obs = True
        self.incident = incident
        return self

    def set_note(self, note: Note) -> SnowRegistration:
        """Set a Note. Previously set Note will be overwritten.

        @param note: The Note to set.
        @return: self, with the Note set.
        """
        self.any_obs = True
        self.note = note
        return self

    def add_image(self,
                  image: Image,
                  parent_registration_type: Type[SnowObservation],
                  ) -> SnowRegistration:
        """Add an image to the danger sign schema

        @param image: The Image to add.
        @param parent_registration_type: The schema under which to add the image.
        @return: self, with an added image.
        """
        if isinstance(parent_registration_type, object) and hasattr(parent_registration_type, "OBSERVATION_TYPE"):
            self.images[parent_registration_type.OBSERVATION_TYPE].append(image)
        elif isinstance(parent_registration_type, int):
            self.images[parent_registration_type].append(image)
        else:
            raise ValueError("Invalid type for parent_registration_type.")
        return self

    def to_dict(self) -> ObsDict:
        return {
            "obs_time": self.obs_time,
            "position": self.position.to_dict() if self.position is not None else None,
            "spatial_precision": self.spatial_precision,
            "source": self.source,
            "id": self.id,
            "observer": self.observer.to_dict() if self.observer is not None else None,
            "danger_signs": list(map(lambda x: x.to_dict(), self.danger_signs)),
            "avalanche_obs": self.avalanche_obs.to_dict() if self.avalanche_obs is not None else None,
            "avalanche_activities": list(map(lambda x: x.to_dict(), self.avalanche_activities)),
            "weather": self.weather.to_dict() if self.weather is not None else None,
            "snow_cover": self.snow_cover.to_dict() if self.snow_cover is not None else None,
            "compression_tests": list(map(lambda x: x.to_dict(), self.compression_tests)),
            "snow_profile": self.snow_profile.to_dict() if self.snow_profile is not None else None,
            "avalanche_problems": list(map(lambda x: x.to_dict(), self.avalanche_problems)),
            "danger_assessment": self.danger_assessment.to_dict() if self.danger_assessment is not None else None,
            "incident": self.incident.to_dict() if self.incident is not None else None,
            "note": self.note.to_dict() if self.note is not None else None,
            "images": {obs_type: list(map(lambda x: x.to_dict(), images)) for obs_type, images in self.images.items()}
        }

    def serialize(self) -> ObsJson:
        all_images = []
        for obs_type, images in self.images.items():
            all_images += [
                {**image.serialize(), "GeoHazardTID": SnowRegistration.GEO_HAZARD, "RegistrationTID": obs_type}
                for image in images
            ]
        return self._clean({
            'Attachments': all_images,
            'AvalancheActivityObs2': list(map(lambda x: x.serialize(), self.avalanche_activities)),
            'AvalancheEvalProblem2': list(map(lambda x: x.serialize(), self.avalanche_problems)),
            'AvalancheEvaluation3': self.danger_assessment.serialize() if self.danger_assessment is not None else None,
            'AvalancheObs': self.avalanche_obs.serialize() if self.avalanche_obs is not None else None,
            'CompressionTest': list(map(lambda x: x.serialize(), self.compression_tests)),
            'DangerObs': list(map(lambda x: x.serialize(), self.danger_signs)),
            'DtObsTime': self.obs_time.isoformat() if self.obs_time is not None else None,
            'GeneralObservation': self.note.serialize() if self.note is not None else None,
            'GeoHazardTID': 10,
            'Incident': self.incident.serialize() if self.incident is not None else None,
            'ObsLocation': self._clean({
                'Latitude': self.position.lat,
                'Longitude': self.position.lon,
                'Uncertainty': self.spatial_precision,
            }),
            'SourceTID': self.source,
            'SnowProfile2': self.snow_profile.serialize() if self.snow_profile is not None else None,
            'SnowSurfaceObservation': self.snow_cover.serialize() if self.snow_cover is not None else None,
            'WeatherObservation': self.weather.serialize() if self.weather is not None else None,
        })

    @classmethod
    def deserialize(cls, json) -> SnowRegistration:
        obs_time = cls._apply(json, "DtObsTime", lambda x: dt.datetime.fromisoformat(x))
        position = object.__new__(Position)
        position.lat = json["ObsLocation"]["Latitude"]
        position.lon = json["ObsLocation"]["Longitude"]
        source = cls._convert(json, "SourceTID", cls.Source)
        spatial_precision = cls._convert(json["ObsLocation"], "Uncertainty", cls.SpatialPrecision)
        reg = cls(obs_time, position, spatial_precision, source)

        reg.id = cls._convert(json, "RegId", int)

        if "Observer" in json and json["Observer"] is not None:
            observer = Observer()
            observer.id = cls._convert(json["Observer"], "ObserverID", int)
            observer.nickname = cls._convert(json["Observer"], "NickName", str)
            observer.competence = cls._convert(json["Observer"], "CompetenceLevelTID", Observer.Competence)
            reg.observer = observer

        reg.danger_signs = cls._apply(json, "DangerObs", lambda x: list(map(lambda y: DangerSign.deserialize(y), x)))
        reg.avalanche_obs = cls._deserialize_to(json, "AvalancheObs", AvalancheObs)
        reg.avalanche_activities = cls._apply(json,
                                              "AvalancheActivityObs2",
                                              lambda x: list(map(lambda y: AvalancheActivity.deserialize(y), x)))
        reg.weather = cls._deserialize_to(json, "WeatherObservation", Weather)
        reg.snow_cover = cls._deserialize_to(json, "SnowSurfaceObservation", SnowCover)
        reg.compression_tests = cls._apply(json,
                                           "CompressionTest",
                                           lambda x: list(map(lambda y: CompressionTest.deserialize(y), x)))
        reg.snow_profile = cls._deserialize_to(json, "SnowProfile2", SnowProfile)
        reg.avalanche_problems = cls._apply(json,
                                            "AvalancheEvalProblem2",
                                            lambda x: list(map(lambda y: AvalancheProblem.deserialize(y), x)))
        reg.danger_assessment = cls._deserialize_to(json, "AvalancheEvaluation3", DangerAssessment)
        reg.incident = cls._deserialize_to(json, "Incident", Incident)
        reg.note = cls._deserialize_to(json, "GeneralObservation", Note)

        reg.images = {}
        if "Attachments" in json and json["Attachments"] is not None:
            for image in json["Attachments"]:
                obs_type = cls._convert(image, "RegistrationTID", cls.ObservationType)
                if obs_type not in reg.images:
                    reg.images[obs_type] = []
                reg.images[obs_type].append(UploadedImage.deserialize(image))

        return reg


class DangerSign(SnowObservation):
    OBSERVATION_TYPE = SnowRegistration.ObservationType.DANGER_SIGN

    class Sign(IntEnum):
        NO_SIGNS = 1
        RECENT_AVALANCHES = 2
        WHUMPF_SOUND = 3
        RECENT_CRACKS = 4
        LARGE_SNOWFALL = 5
        QUICK_TEMP_CHANGE = 7
        WATER_IN_SNOW = 8
        RECENT_SNOWDRIFT = 9
        OTHER = 99

    def __init__(self,
                 sign: Optional[DangerSign.Sign] = None,
                 comment: Optional[str] = None):
        """A danger sign, such as whumpf sounds or quick temperature change.

        @param sign: What kind of danger sign was observed?
        @param comment: Comment regarding the danger sign.
        """
        if all(e is None for e in [sign, comment]):
            raise NoObservationError("No argument passed to danger sign observation.")

        self.sign = sign
        self.comment = comment

    def to_dict(self) -> ObsDict:
        return {
            "sign": self.sign,
            "comment": self.comment,
        }

    def serialize(self) -> ObsJson:
        return self._clean({
            'DangerSignTID': self.sign if self.sign is not None else 0,
            'Comment': self.comment,
        })

    @classmethod
    def deserialize(cls, json: ObsJson):
        danger_sign = object.__new__(cls)
        danger_sign.sign = cls._convert(json, "DangerSignTID", cls.Sign)
        danger_sign.sign = danger_sign.sign if danger_sign.sign != 0 else None
        danger_sign.comment = cls._convert(json, "Comment", str)
        return danger_sign


class AvalancheObs(SnowObservation):
    OBSERVATION_TYPE = SnowRegistration.ObservationType.AVALANCHE_OBS

    class Type(IntEnum):
        LOOSE_SNOW = 10  # DRY_LOOSE or WET_LOOSE should be used if possible
        DRY_LOOSE = 12
        WET_LOOSE = 11
        SLAB = 20  # DRY_SLAB or WET_SLAB should be used if possible
        DRY_SLAB = 22
        WET_SLAB = 21
        GLIDE = 27
        SLUSH_FLOW = 30
        CORNICE = 40
        UNKNOWN = 99

    class Trigger(IntEnum):
        NATURAL = 10
        HUMAN = 26
        SNOWMOBILE = 27
        REMOTE = 22
        TEST_SLOPE = 23
        EXPLOSIVES = 25
        UNKNOWN = 99

    class Terrain(IntEnum):
        STEEP_SLOPE = 10
        LEE_SIDE = 20
        CLOSE_TO_RIDGE = 30
        GULLY = 40
        SLAB = 50
        BOWL = 60
        FOREST = 70
        LOGGING_AREA = 75
        EVERYWHERE = 95
        UNKNOWN = 99

    def __init__(self, release_time: dt.datetime,
                 start: Optional[Position] = None,
                 stop: Optional[Position] = None,
                 exposition: Optional[Direction] = None,
                 size: Optional[DestructiveSize] = None,
                 avalanche_type: Optional[AvalancheObs.Type] = None,
                 trigger: Optional[AvalancheObs.Trigger] = None,
                 terrain: Optional[AvalancheObs.Terrain] = None,
                 weak_layer: Optional[WeakLayer] = None,
                 fracture_height_cm: Optional[int] = None,
                 fracture_width: Optional[int] = None,
                 path_name: Optional[str] = None,
                 comment: Optional[str] = None,
                 ):
        """An observation of a single avalanche. This should be used if you have detailed info regarding an avalanche.

        @param release_time: When was the avalanche triggered?
        @param start: Give the highest position of the fracture line.
        @param stop: Give the lowest position of the avalanche debris.
        @param exposition: In what direction was the avalanche triggered?
        @param size: How large was the avalanche, on the standardized scale between 1-5?
        @param avalanche_type: What kind of avalanche was triggered?
        @param trigger: What triggered the avalanche?
        @param terrain: In what kind of terrain was the avalanche triggered?
        @param weak_layer: What kind of weak layer collapsed to give rise to the avalanche?
        @param fracture_height_cm: How high was the fracture line (in cm)?
        @param fracture_width: How wide was the avalanche (in metres)?
        @param path_name: If the avalanche was observed in a known avalanche track, give its name.
        @param comment: Comment regarding the avalanche observation.
        """

        self.release_time = release_time
        self.start = start
        self.stop = stop
        self.exposition = exposition
        self.size = size
        self.avalanche_type = avalanche_type
        self.trigger = trigger
        self.terrain = terrain
        self.weak_layer = weak_layer
        self.fracture_height_cm = fracture_height_cm
        self.fracture_width = fracture_width
        self.path_name = path_name
        self.comment = comment

    def to_dict(self) -> ObsDict:
        return {
            "release_time": self.release_time,
            "start": self.start,
            "stop": self.stop,
            "exposition": self.exposition,
            "size": self.size,
            "avalanche_type": self.avalanche_type,
            "trigger": self.trigger,
            "terrain": self.terrain,
            "weak_layer": self.weak_layer,
            "fracture_height_cm": self.fracture_height_cm,
            "fracture_width": self.fracture_width,
            "path_name": self.path_name,
            "comment": self.comment,
        }

    def serialize(self) -> ObsJson:
        return self._clean({
            'AvalCauseTID': self.weak_layer,
            'AvalancheTID': self.avalanche_type,
            'AvalancheTriggerTID': self.trigger,
            'Comment': self.comment,
            'DestructiveSizeTID': self.size,
            'DtAvalancheTime': self.release_time.isoformat(),
            'FractureHeight': round(self.fracture_height_cm) if self.fracture_height_cm is not None else None,
            'FractureWidth': round(self.fracture_width) if self.fracture_width is not None else None,
            'StartLat': self.start.lat if self.start is not None else None,
            'StartLong': self.start.lon if self.start is not None else None,
            'StopLat': self.stop.lat if self.stop is not None else None,
            'StopLong': self.stop.lon if self.stop is not None else None,
            'TerrainStartZoneTID': self.terrain,
            'Trajectory': self.path_name,
            'ValidExposition': Expositions([self.exposition]).serialize() if self.exposition is not None else None,
        })

    @classmethod
    def deserialize(cls, json: ObsJson) -> AvalancheObs:
        start_lat = cls._convert(json, "StartLat", float)
        start_lon = cls._convert(json, "StartLong", float)
        stop_lat = cls._convert(json, "StopLat", float)
        stop_lon = cls._convert(json, "StopLong", float)
        start = None
        stop = None
        if start_lat is not None and start_lon is not None:
            start = object.__new__(Position)
            start.lat = start_lat
            start.lon = start_lon
        if stop_lat is not None and stop_lon is not None:
            stop = object.__new__(Position)
            stop.lat = stop_lat
            stop.lon = stop_lon
        try:
            exp = cls._apply(json,
                             "ValidExposition",
                             lambda x: next(iter(Expositions.deserialize(x).expositions), None))
        except ValueError:
            exp = None
        return cls(release_time=cls._apply(json, "DtAvalancheTime", lambda x: dt.datetime.fromisoformat(x)),
                   start=start,
                   stop=stop,
                   exposition=exp,
                   size=cls._convert(json, "DestructiveSizeTID", DestructiveSize),
                   avalanche_type=cls._convert(json, "AvalancheTID", cls.Type),
                   trigger=cls._convert(json, "AvalancheTriggerTID", cls.Trigger),
                   terrain=cls._convert(json, "TerrainStartZoneTID", cls.Terrain),
                   weak_layer=cls._convert(json, "AvalCauseTID", WeakLayer),
                   fracture_height_cm=cls._convert(json, "FractureHeight", int),
                   fracture_width=cls._convert(json, "FractureWidth", int),
                   path_name=cls._convert(json, "Trajectory", str),
                   comment=cls._convert(json, "Comment", str))


class AvalancheActivity(SnowObservation):
    OBSERVATION_TYPE = SnowRegistration.ObservationType.AVALANCHE_ACTIVITY

    class Timeframe(Enum):
        ZERO_TO_SIX = '0-6'
        SIX_TO_TWELVE = '6-12'
        TWELVE_TO_EIGHTEEN = '12-18'
        EIGHTEEN_TO_TWENTY_FOUR = '18-24'

    class Quantity(IntEnum):
        NO_ACTIVITY = 1
        ONE = 2
        FEW = 3
        SEVERAL = 4
        NUMEROUS = 5

    class Type(IntEnum):
        DRY_LOOSE = 10
        WET_LOOSE = 15
        DRY_SLAB = 20
        WET_SLAB = 25
        GLIDE = 27
        SLUSH_FLOW = 30
        CORNICE = 40

    def __init__(self, date: dt.date,
                 timeframe: Optional[AvalancheActivity.Timeframe] = None,
                 quantity: Optional[AvalancheActivity.Quantity] = None,
                 avalanche_type: Optional[AvalancheActivity.Type] = None,
                 sensitivity: Optional[Sensitivity] = None,
                 size: Optional[DestructiveSize] = None,
                 distribution: Optional[Distribution] = None,
                 elevation: Optional[Elevation] = None,
                 expositions: Optional[Expositions] = None,
                 comment: Optional[str] = None):
        """An observation of a group of avalanches.

        @param date: On what day were the avalanches triggered?
        @param timeframe: When during the day were the avalanches triggered?
        @param quantity: How many avalanches were triggered?
        @param avalanche_type: What kind of avalanche was triggered?
        @param sensitivity: The sensitivy to triggering of the avalanche problem.
        @param size: How large was the avalanches, on the standardized scale between 1-5?
        @param distribution: The distribution of the avalanche problem in the terrain.
        @param elevation: The elevation band of the avalanches.
        @param expositions: The expositions of the avalanches.
        @param comment: Comment regarding the avalanche activity.
        """
        avalanche_attributes = [avalanche_type, sensitivity, size, distribution, elevation, expositions]
        if quantity == self.Quantity.NO_ACTIVITY and any(e is not None for e in avalanche_attributes):
            raise NoObservationError("Avalanche attributes specified, but no avalanche activity reported.")

        timeframe_times = {
            None: {'start': dt.time(0), 'end': dt.time(23, 59)},
            '0-6': {'start': dt.time(0), 'end': dt.time(6)},
            '6-12': {'start': dt.time(6), 'end': dt.time(12)},
            '12-18': {'start': dt.time(12), 'end': dt.time(18)},
            '18-24': {'start': dt.time(18), 'end': dt.time(23, 59)},
        }[timeframe.value if timeframe is not None else None]
        self.start = TZ.localize(dt.datetime.combine(date, timeframe_times['start']))
        self.end = TZ.localize(dt.datetime.combine(date, timeframe_times['end']))
        self.quantity = quantity
        self.avalanche_type = avalanche_type
        self.sensitivity = sensitivity
        self.size = size
        self.distribution = distribution
        self.elevation = elevation
        self.expositions = expositions
        self.comment = comment

    def to_dict(self) -> ObsDict:
        return {
            "start": self.start,
            "end": self.end,
            "quantity": self.quantity,
            "avalanche_type": self.avalanche_type,
            "sensitivity": self.sensitivity,
            "size": self.size,
            "distribution": self.distribution,
            "elevation": self.elevation.to_dict() if self.elevation is not None else None,
            "expositions": self.expositions.to_dict() if self.expositions is not None else None,
            "comment": self.comment,
        }

    def serialize(self) -> ObsJson:
        obs = {
            'AvalPropagationTID': self.distribution,
            'AvalTriggerSimpleTID': self.sensitivity,
            'AvalancheExtTID': self.avalanche_type,
            'Comment': self.comment,
            'DestructiveSizeTID': self.size,
            'DtEnd': self.end.isoformat(),
            'DtStart': self.start.isoformat(),
            'EstimatedNumTID': self.quantity,
            'ValidExposition': self.expositions.serialize() if self.expositions is not None else None,
        }
        if self.elevation is not None:
            obs = {**obs, **self.elevation.serialize()}
        return self._clean(obs)

    @classmethod
    def deserialize(cls, json: ObsJson) -> AvalancheActivity:
        elev = None
        if all(x in json for x in ["ExposedHeightComboTID", "ExposedHeight1"]):
            if None not in [json["ExposedHeightComboTID"], json["ExposedHeight1"]]:
                elev = Elevation.deserialize(json)
        activity = object.__new__(cls)
        activity.start = cls._apply(json, "DtStart", lambda x: dt.datetime.fromisoformat(x))
        activity.end = cls._apply(json, "DtEnd", lambda x: dt.datetime.fromisoformat(x))
        activity.quantity = cls._convert(json, "EstimatedNumTID", AvalancheActivity.Quantity)
        activity.avalanche_type = cls._convert(json, "AvalancheExtTID", AvalancheActivity.Type)
        activity.sensitivity = cls._convert(json, "AvalTriggerSimpleTID", Sensitivity)
        activity.size = cls._convert(json, "DestructiveSizeTID", DestructiveSize)
        activity.distribution = cls._convert(json, "AvalPropagationTID", Distribution)
        activity.elevation = elev
        activity.expositions = cls._apply(json, "ValidExposition", lambda x: Expositions.deserialize(x))
        activity.comment = cls._convert(json, "Comment", str)
        return activity


class Weather(SnowObservation):
    OBSERVATION_TYPE = SnowRegistration.ObservationType.WEATHER

    class Precipitation(IntEnum):
        NO_PRECIPITATION = 1
        DRIZZLE = 2
        RAIN = 3
        SLEET = 4
        SNOW = 5
        HAIL = 6
        FREEZING_RAIN = 8

    def __init__(self,
                 precipitation: Optional[Weather.Precipitation] = None,
                 wind_dir: Optional[Direction] = None,
                 air_temp: Optional[float] = None,
                 wind_speed: Optional[float] = None,
                 cloud_cover_percent: Optional[int] = None,
                 comment: Optional[str] = None):
        """Information regarding the weather.

        @param precipitation: The amount and kind of precipitation.
        @param wind_dir: The wind direction.
        @param air_temp: Air temperature.
        @param wind_speed: The wind speed.
        @param cloud_cover_percent: How much of the sky (in percent) is covered by clouds?
        @param comment: Comment regarding the weather.
        """
        if all(e is None for e in [precipitation, air_temp, wind_speed, cloud_cover_percent, wind_dir, comment]):
            raise NoObservationError("No argument passed to weather observation.")
        if cloud_cover_percent is not None and not (0 <= cloud_cover_percent <= 100):
            raise ValueError("Percentage must be within the range 0--100.")

        self.precipitation = precipitation
        self.wind_dir = wind_dir
        self.air_temp = air_temp
        self.wind_speed = wind_speed
        self.cloud_cover_percent = cloud_cover_percent
        self.comment = comment

    def to_dict(self) -> ObsDict:
        return {
            "precipitation": self.precipitation,
            "wind_dir": self.wind_dir,
            "air_temp": self.air_temp,
            "wind_speed": self.wind_speed,
            "cloud_cover_percent": self.cloud_cover_percent,
            "comment": self.comment,
        }

    def serialize(self) -> ObsJson:
        return self._clean({
            'AirTemperature': self.air_temp,
            'CloudCover': round(self.cloud_cover_percent) if self.cloud_cover_percent is not None else None,
            'Comment': self.comment,
            'PrecipitationTID': self.precipitation,
            'WindDirection': self.wind_dir * 45 if self.wind_dir is not None else None,
            'WindSpeed': self.wind_speed
        })

    @classmethod
    def deserialize(cls, json: ObsJson) -> Weather:
        weather = object.__new__(cls)
        weather.precipitation = cls._convert(json, "PrecipitationTID", cls.Precipitation)
        weather.wind_dir = cls._apply(json, "WindDirection", lambda x: Direction(round(x / 45) % 8))
        weather.air_temp = cls._convert(json, "AirTemperature", float)
        weather.wind_speed = cls._convert(json, "WindSpeed", float)
        weather.cloud_cover_percent = cls._convert(json, "CloudCover", int)
        weather.comment = cls._convert(json, "Comment", str)
        return weather


class SnowCover(SnowObservation):
    OBSERVATION_TYPE = SnowRegistration.ObservationType.SNOW_COVER

    class Drift(IntEnum):
        NO_DRIFT = 1
        SOME = 2
        MODERATE = 3
        HEAVY = 4

    class Surface(IntEnum):
        LOOSE_OVER_30_CM = 101
        LOOSE_10_TO_30_CM = 102
        LOOSE_1_TO_10_CM = 103
        SURFACE_HOAR_HARD = 61
        SURFACE_HOAR_SOFT = 62
        NEW_SURFACE_FACETS = 50
        CRUST = 107
        WIND_SLAB_HARD = 105
        STORM_SLAB_SOFT = 106
        WET_LOOSE = 104
        OTHER = 108

    class Moisture(IntEnum):
        NO_SNOW = 1
        DRY = 2
        MOIST = 3
        WET = 4
        VERY_WET = 5
        SLUSH = 6

    def __init__(self,
                 drift: Optional[SnowCover.Drift] = None,
                 surface: Optional[SnowCover.Surface] = None,
                 moisture: Optional[SnowCover.Moisture] = None,
                 hn24_cm: Optional[float] = None,
                 new_snow_line: Optional[int] = None,
                 hs_cm: Optional[float] = None,
                 snow_line: Optional[int] = None,
                 layered_snow_line: Optional[float] = None,
                 comment: Optional[str] = None):
        """Information regarding the top of the snowpack.

        @param drift: Are there any drifting snow?
        @param surface: What is on the surface of the snow cover?
        @param moisture: What is the moisture content of the snow cover?
        @param hn24_cm: How much snow has been accumulated over the last 24 hours (in cm)?
        @param new_snow_line: What is the lowest elevation of new snow (in metres)?
        @param hs_cm: How deep is the snow (in cm)?
        @param snow_line: What is the lowest elevation of snow (in metres)?
        @param layered_snow_line: What is the lowest elevation of layered snow (in metres)?
        @param comment: Comment regarding the snow cover.
        """
        if all(e is None for e in
               [drift, surface, moisture, hn24_cm, new_snow_line, hs_cm, snow_line, layered_snow_line, comment]):
            raise NoObservationError("No argument passed to snow cover observation.")

        self.drift = drift
        self.surface = surface
        self.moisture = moisture
        self.hn24_cm = hn24_cm
        self.new_snow_line = new_snow_line
        self.hs_cm = hs_cm
        self.snow_line = snow_line
        self.layered_snow_line = layered_snow_line
        self.comment = comment

    def to_dict(self) -> ObsDict:
        return {
            "drift": self.drift,
            "surface": self.surface,
            "moisture": self.moisture,
            "hn24_cm": self.hn24_cm,
            "new_snow_line": self.new_snow_line,
            "hs_cm": self.hs_cm,
            "snow_line": self.snow_line,
            "layered_snow_line": self.layered_snow_line,
            "comment": self.comment,
        }

    def serialize(self) -> ObsJson:

        return self._clean({
            'Comment': self.comment,
            'HeightLimitLayeredSnow': self.layered_snow_line,
            'NewSnowDepth24': self.hn24_cm / 100 if self.hn24_cm is not None else None,
            'NewSnowLine': round(self.new_snow_line) if self.new_snow_line is not None else None,
            'SnowDepth': self.hs_cm / 100 if self.hs_cm is not None else None,
            'SnowDriftTID': self.drift,
            'SnowLine': round(self.snow_line) if self.snow_line is not None else None,
            'SnowSurfaceTID': self.surface,
            'SurfaceWaterContentTID': self.moisture,
        })

    @classmethod
    def deserialize(cls, json: ObsJson) -> SnowCover:
        cover = object.__new__(cls)
        cover.drift = cls._convert(json, "SnowDriftTID", cls.Drift)
        cover.surface = cls._convert(json, "SnowSurfaceTID", cls.Surface)
        cover.moisture = cls._convert(json, "SurfaceWaterContentTID", cls.Moisture)
        cover.hn24_cm = cls._apply(json, "NewSnowDepth24", lambda x: x * 100)
        cover.new_snow_line = cls._convert(json, "NewSnowLine", int)
        cover.hs_cm = cls._convert(json, "SnowDepth", lambda x: x * 100)
        cover.snow_line = cls._convert(json, "SnowLine", int)
        cover.layered_snow_line = cls._convert(json, "HeightLimitLayeredSnow", int)
        cover.comment = cls._convert(json, "Comment", str)
        return cover


class CompressionTest(SnowObservation):
    OBSERVATION_TYPE = SnowRegistration.ObservationType.COMPRESSION_TEST

    class TestResult(IntEnum):
        ECTPV = 21
        ECTP = 22
        ECTN = 23
        ECTX = 24
        LBT = 5
        CTV = 11
        CTE = 12
        CTM = 13
        CTH = 14
        CTN = 15

    class FractureQuality(IntEnum):
        Q1 = 1
        Q2 = 2
        Q3 = 3

    class Stability(IntEnum):
        GOOD = 1
        MEDIUM = 2
        POOR = 3

    def __init__(self,
                 test_result: Optional[CompressionTest.TestResult] = None,
                 fracture_quality: Optional[CompressionTest.FractureQuality] = None,
                 stability: Optional[CompressionTest.Stability] = None,
                 number_of_taps: Optional[int] = None,
                 fracture_depth_cm: Optional[float] = None,
                 is_in_profile: Optional[bool] = None,
                 comment: Optional[str] = None):
        """Compression tests, such as CT and ECT.

        @param test_result: The kind of test and the result of that test.
        @param fracture_quality: The fracture quality, i.e. Q1, Q2 or Q3.
        @param stability: The stability of the snowpack according to the test.
        @param number_of_taps: The number of taps before collapse.
        @param fracture_depth_cm: The depth of the fracture (in cm).
        @param is_in_profile: Whether to include the compression test in the snow profile.
        @param comment: Comment regarding the compression test.
        """
        if all(e is None for e in [test_result, fracture_quality, stability, number_of_taps, fracture_depth_cm,
                                   is_in_profile, comment]):
            raise NoObservationError("No argument passed to compression test.")

        no_taps = [self.TestResult.ECTPV, self.TestResult.LBT, self.TestResult.CTV]
        all_taps = [self.TestResult.ECTX, self.TestResult.CTN]
        if number_of_taps is not None:
            if not (0 < number_of_taps <= 30):
                raise ValueError("Test taps must be in the range 1-30.")
            if test_result in no_taps or test_result in all_taps and not (number_of_taps == 0 or number_of_taps == 30):
                raise ValueError("Supplied test result had invalid number of taps.")

        if fracture_depth_cm is not None and test_result in all_taps:
            raise ValueError("Supplied test result must not have any fracture depth.")

        self.test_result = test_result
        self.fracture_quality = fracture_quality
        self.stability = stability
        self.number_of_taps = number_of_taps
        self.fracture_depth_cm = fracture_depth_cm
        self.is_in_profile = is_in_profile
        self.comment = comment

    def to_dict(self) -> ObsDict:
        return {
            "test_result": self.test_result,
            "fracture_quality": self.fracture_quality,
            "stability": self.stability,
            "number_of_taps": self.number_of_taps,
            "fracture_depth_cm": self.fracture_depth_cm,
            "is_in_profile": self.is_in_profile,
            "comment": self.comment,
        }

    def serialize(self) -> ObsJson:
        return self._clean({
            'PropagationTID': self.test_result,
            'ComprTestFractureTID': self.fracture_quality,
            'StabilityEvalTID': self.stability,
            'TapsFracture': round(self.number_of_taps) if self.number_of_taps is not None else None,
            'FractureDepth': self.fracture_depth_cm / 100 if self.fracture_depth_cm is not None else None,
            'IncludeInSnowProfile': self.is_in_profile,
            'Comment': self.comment,
        })

    @classmethod
    def deserialize(cls, json: ObsJson) -> CompressionTest:
        test = object.__new__(cls)
        test.test_result = cls._convert(json, "PropagationTID", cls.TestResult)
        test.fracture_quality = cls._convert(json, "ComprTestFractureTID", cls.FractureQuality)
        test.stability = cls._convert(json, "StabilityEvalTID", cls.Stability)
        test.number_of_taps = cls._convert(json, "TapsFracture", int)
        test.fracture_depth_cm = cls._convert(json, "FractureDepth", lambda x: x * 100)
        test.is_in_profile = cls._convert(json, "IncludeInSnowProfile", bool)
        test.comment = cls._convert(json, "Comment", str)
        return test


class SnowProfile(SnowObservation):
    OBSERVATION_TYPE = SnowRegistration.ObservationType.SNOW_PROFILE

    class Hardness(IntEnum):
        FIST_MINUS = 1
        FIST = 2
        FIST_PLUS = 3
        FIST_TO_FOUR_FINGERS = 4
        FOUR_FINGERS_MINUS = 5
        FOUR_FINGERS = 6
        FOUR_FINGERS_PLUS = 7
        FOUR_FINGERS_TO_ONE_FINGER = 8
        ONE_FINGER_MINUS = 9
        ONE_FINGER = 10
        ONE_FINGER_PLUS = 11
        ONE_FINGER_TO_PEN = 12
        PEN_MINUS = 13
        PEN = 14
        PEN_PLUS = 15
        PEN_TO_KNIFE = 16
        KNIFE_MINUS = 17
        KNIFE = 18
        KNIFE_PLUS = 19
        KNIFE_TO_ICE = 20
        ICE = 21

    class GrainForm(IntEnum):
        PP = 1
        PP_CO = 2
        PP_ND = 3
        PP_PL = 4
        PP_SD = 5
        PP_IR = 6
        PP_GP = 7
        PP_HL = 8
        PP_IP = 9
        PP_RM = 10
        MM = 11
        MM_RP = 12
        MM_CI = 13
        DF = 14
        DF_DC = 15
        DF_BK = 16
        RG = 17
        RG_SR = 18
        RG_LR = 19
        RG_WP = 20
        RG_XF = 21
        FC = 22
        FC_SO = 23
        FC_SF = 24
        FC_XR = 25
        DH = 26
        DH_CP = 27
        DH_PR = 28
        DH_CH = 29
        DH_LA = 30
        DH_XR = 31
        SH = 32
        SH_SU = 33
        SH_CV = 34
        SH_XR = 35
        MF = 36
        MF_CL = 37
        MF_PC = 38
        MF_SL = 29
        MF_CR = 40
        IF = 41
        IF_IL = 42
        IF_IC = 43
        IF_BI = 44
        IF_RC = 45
        IF_SC = 46

    class GrainSize(FloatEnum):
        ZERO_POINT_ONE = 0.1
        ZERO_POINT_THREE = 0.3
        ZERO_POINT_FIVE = 0.3
        ZERO_POINT_SEVEN = 0.3
        ONE = 1.0
        ONE_POINT_FIVE = 1.5
        TWO = 2.0
        TWO_POINT_FIVE = 2.5
        THREE = 3.0
        THREE_POINT_FIVE = 3.5
        FIVE = 5
        FIVE_POINT_FIVE = 5.5
        SIX = 6.0
        EIGHT = 8.0
        TEN = 10.0

    class Wetness(IntEnum):
        D = 1
        D_M = 2
        M = 3
        M_W = 4
        W = 5
        W_V = 6
        V = 7
        V_S = 8
        S = 9

    class CriticalLayer(IntEnum):
        UPPER = 11
        LOWER = 12
        WHOLE = 13

    class Layer(Serializable, Deserializable, Dictable):
        def __init__(self,
                     thickness_cm: float,
                     hardness: SnowProfile.Hardness,
                     grain_form_primary: Optional[SnowProfile.GrainForm] = None,
                     grain_size_mm: Optional[SnowProfile.GrainSize] = None,
                     wetness: Optional[SnowProfile.Wetness] = None,
                     hardness_bottom: Optional[SnowProfile.Hardness] = None,
                     grain_form_sec: Optional[SnowProfile.GrainForm] = None,
                     grain_size_max_mm: Optional[SnowProfile.GrainSize] = None,
                     critical_layer: Optional[SnowProfile.CriticalLayer] = None,
                     comment: Optional[str] = None):
            """A snow layer of a snow profile.

            @param thickness_cm: Layer thickness (in cm).
            @param hardness: Layer hardness (F, 4F, 1F, P, K, I).
            @param grain_form_primary: Primary grain form.
            @param grain_size_mm: Grain size (in mm).
            @param wetness: Moisture content of the layer.
            @param hardness_bottom: Hardness at the bottom of the layer (F, 4F, 1F, P, K, I).
            @param grain_form_sec: Secondary grain form.
            @param grain_size_max_mm: Maximum grain size (in mm).
            @param critical_layer: Is this layer critical, and what part of it?
            @param comment: Comment regarding the snow layer.
            """
            if thickness_cm is not None and thickness_cm < 0:
                raise ValueError("Thickness must be larger than or equal to 0.")

            self.thickness_cm = thickness_cm
            self.hardness = hardness
            self.grain_form_primary = grain_form_primary
            self.grain_size_mm = grain_size_mm
            self.wetness = wetness
            self.hardness_bottom = hardness_bottom
            self.grain_form_sec = grain_form_sec
            self.grain_size_max_mm = grain_size_max_mm
            self.critical_layer = critical_layer
            self.comment = comment

        def to_dict(self) -> ObsDict:
            return {
                "thickness_cm": self.thickness_cm,
                "hardness": self.hardness,
                "grain_form_primary": self.grain_form_primary,
                "grain_size_mm": self.grain_size_mm,
                "wetness": self.wetness,
                "hardness_bottom": self.hardness_bottom,
                "grain_form_sec": self.grain_form_sec,
                "grain_size_max_mm": self.grain_size_max_mm,
                "critical_layer": self.critical_layer,
                "comment": self.comment,
            }

        def serialize(self) -> ObsJson:
            return self._clean({
                'Thickness': self.thickness_cm / 100 if self.thickness_cm is not None else None,
                'HardnessTID': self.hardness,
                'GrainFormPrimaryTID': self.grain_form_primary,
                'GrainSizeAvg': self.grain_size_mm / 100 if self.grain_size_mm is not None else None,
                'WetnessTID': self.wetness,
                'HardnessBottomTID': self.hardness_bottom,
                'GrainFormSecondaryTID': self.grain_form_sec,
                'GrainSizeAvgMax': self.grain_size_max_mm / 100 if self.grain_size_max_mm is not None else None,
                'CriticalLayerTID': self.critical_layer,
                'Comment': self.comment,
            })

        @classmethod
        def deserialize(cls, json: ObsJson) -> SnowProfile.Layer:
            try:
                grain_size_mm = cls._apply(json, "GrainSizeAvg", lambda x: SnowProfile.GrainSize(x * 100))
            except ValueError:
                grain_size_mm = cls._apply(json, "GrainSizeAvg", lambda x: x * 100)
            try:
                grain_size_max_mm = cls._apply(json, "GrainSizeAvgMax", lambda x: SnowProfile.GrainSize(x * 100))
            except ValueError:
                grain_size_max_mm = cls._apply(json, "GrainSizeAvgMax", lambda x: x * 100)
            layer = object.__new__(cls)
            layer.thickness_cm = cls._apply(json, "Thickness", lambda x: x * 100)
            layer.hardness = cls._convert(json, "HardnessTID", SnowProfile.Hardness)
            layer.grain_form_primary = cls._convert(json, "GrainFormPrimaryTID", SnowProfile.GrainForm)
            layer.grain_size_mm = grain_size_mm
            layer.wetness = cls._convert(json, "WetnessTID", SnowProfile.Wetness)
            layer.hardness_bottom = cls._convert(json, "HardnessBottomTID", SnowProfile.Hardness)
            layer.grain_form_sec = cls._convert(json, "GrainFormSecondaryTID", SnowProfile.GrainForm)
            layer.grain_size_max_mm = grain_size_max_mm
            layer.critical_layer = cls._convert(json, "CriticalLayerTID", SnowProfile.CriticalLayer)
            layer.comment = cls._convert(json, "Comment", str)
            return layer

    class SnowTemp(Serializable, Deserializable, Dictable):
        def __init__(self,
                     depth_cm: float,
                     temp_c: float):
            """Snow temperature at a given depth.

            @param depth_cm: The depth measured (in cm from top).
            @param temp_c: The measured temperature (in Celsius).
            """
            if temp_c > 0:
                raise ValueError("Snow temperature must be lower than or equal to 0.")

            self.depth_cm = depth_cm
            self.temp_c = temp_c

        def to_dict(self) -> ObsDict:
            return {
                "depth_cm": self.depth_cm,
                "temp_c": self.temp_c,
            }

        def serialize(self) -> ObsJson:
            return self._clean({
                'Depth': self.depth_cm / 100 if self.depth_cm is not None else None,
                'SnowTemp': self.temp_c,
            })

        @classmethod
        def deserialize(cls, json: ObsJson) -> SnowProfile.SnowTemp:
            temp = object.__new__(cls)
            temp.depth_cm = cls._apply(json, "Depth", lambda x: x * 100)
            temp.temp_c = cls._convert(json, "SnowTemp", float)
            return temp

    class Density(Serializable, Deserializable, Dictable):
        def __init__(self,
                     thickness_cm: float,
                     density_kg_per_cubic_metre: float):
            """Snow density at a given depth.

            @param thickness_cm: The thickness of the sample layer (in cm).
            @param density_kg_per_cubic_metre: The density (in kg/m³).
            """
            if thickness_cm < 0:
                raise ValueError("Thickness must be larger than or equal to 0.")

            self.thickness_cm = thickness_cm
            self.density_kg_per_cubic_metre = density_kg_per_cubic_metre

        def to_dict(self) -> ObsDict:
            return {
                "thickness_cm": self.thickness_cm,
                "density_kg_per_cubic_metre": self.density_kg_per_cubic_metre,
            }

        def serialize(self) -> ObsJson:
            return self._clean({
                'Thickness': self.thickness_cm / 100 if self.thickness_cm is not None else None,
                'Density': self.density_kg_per_cubic_metre,
            })

        @classmethod
        def deserialize(cls, json: ObsJson) -> SnowProfile.Density:
            density = object.__new__(cls)
            density.thickness_cm = cls._apply(json, "Thickness", lambda x: x * 100)
            density.density_kg_per_cubic_metre = cls._convert(json, "Density", float)
            return density

    def __init__(self,
                 layers: List[SnowProfile.Layer] = (),
                 temperatures: List[SnowProfile.SnowTemp] = (),
                 densities: List[SnowProfile.Density] = (),
                 is_profile_to_ground: Optional[bool] = None,
                 comment: Optional[str] = None):
        """A snow profile, including tests, layers, temperatures and densities.

        @param layers: Snow layers included in the profile.
        @param temperatures: Temperatures measured in the snow profile.
        @param densities: Densities measured in the snow.
        @param is_profile_to_ground: Whether the snow profile was dug to the ground.
        @param comment: Comment regarding the snow profile.
        """
        if all(e is None for e in [layers, temperatures, densities, comment]):
            raise NoObservationError("Neither layers, temperatures, densities or comment passed to snow profile.")

        self.layers = layers
        self.temperatures = temperatures
        self.densities = densities
        self.is_profile_to_ground = is_profile_to_ground
        self.comment = comment

    def to_dict(self) -> ObsDict:
        return {
            "layers": list(map(lambda x: x.to_dict(), self.layers)) if self.layers is not None else None,
            "temperatures": list(
                map(lambda x: x.to_dict(), self.temperatures)
            ) if self.temperatures is not None else None,
            "densities": list(map(lambda x: x.to_dict(), self.densities)) if self.densities is not None else None,
            "is_profile_to_ground": self.is_profile_to_ground,
            "comment": self.comment,
        }

    def serialize(self) -> ObsJson:
        return self._clean({
            'StratProfile': self._clean({
                'Layers': list(map(lambda x: x.serialize(), self.layers)),
            }),
            'SnowTemp': self._clean({
                'Layers': list(map(lambda x: x.serialize(), self.temperatures)),
            }),
            'SnowDensity': [self._clean({
                'Layers': list(map(lambda x: x.serialize(), self.densities)),
            })] if len(self.densities) else None,
            'IsProfileToGround': self.is_profile_to_ground,
            'Comment': self.comment,
        })

    @classmethod
    def deserialize(cls, json: ObsJson) -> SnowProfile:
        layers = None
        if "StratProfile" in json and json["StratProfile"] is not None:
            if "Layers" in json["StratProfile"] and json["StratProfile"]["Layers"] is not None:
                layers = list(map(lambda x: SnowProfile.Layer.deserialize(x), json["StratProfile"]["Layers"]))
        temperatures = None
        if "SnowTemp" in json and json["SnowTemp"] is not None:
            if "Layers" in json["SnowTemp"] and json["SnowTemp"]["Layers"] is not None:
                temperatures = list(map(lambda x: SnowProfile.SnowTemp.deserialize(x), json["SnowTemp"]["Layers"]))
        densities = None
        if "SnowDensity" in json and json["SnowDensity"] is not None:
            for d_elem in json["SnowDensity"]:
                if "Layers" in d_elem and d_elem["Layers"] is not None:
                    if densities is None:
                        densities = []
                    densities += list(map(lambda x: SnowProfile.Density.deserialize(x), d_elem["Layers"]))
        profile = object.__new__(cls)
        profile.layers = layers
        profile.temperatures = temperatures
        profile.densities = densities
        profile.is_profile_to_ground = cls._convert(json, "IsProfileToGround", bool)
        profile.comment = cls._convert(json, "Comment", str)
        return profile


class AvalancheProblem(SnowObservation):
    OBSERVATION_TYPE = SnowRegistration.ObservationType.AVALANCHE_PROBLEM

    class LayerDepth(IntEnum):
        LESS_THAN_50_CM = 1
        LESS_THAN_100_CM = 2
        MORE_THAN_100_CM = 3

    class Type(IntEnum):
        DRY_LOOSE = 10
        WET_LOOSE = 15
        DRY_SLAB = 20
        WET_SLAB = 25

    def __init__(self,
                 weak_layer: Optional[WeakLayer] = None,
                 layer_depth: Optional[AvalancheProblem.LayerDepth] = None,
                 avalanche_type: Optional[AvalancheProblem.Type] = None,
                 sensitivity: Optional[Sensitivity] = None,
                 size: Optional[DestructiveSize] = None,
                 distribution: Optional[Distribution] = None,
                 elevation: Optional[Elevation] = None,
                 expositions: Optional[Expositions] = None,
                 is_easy_propagation: Optional[bool] = None,
                 is_layer_thin: Optional[bool] = None,
                 is_soft_slab_above: Optional[bool] = None,
                 is_large_crystals: Optional[bool] = None,
                 comment: Optional[str] = None):
        """An avalanche problem assessed to be in the terrain.

        @param weak_layer: The kind of weak layer causing the avalanche problem.
        @param layer_depth: The depth of the layer of concern.
        @param avalanche_type: The type of avalanche that this problem could cause.
        @param sensitivity: The problems sensitivity to triggers.
        @param size: The size of potential avalanches caused by this problem.
        @param distribution: The distribution in the terrain of this avalanche problem
        @param elevation: The evelation band of the avalanche problem.
        @param expositions: The expositions that the avalanche problem exists in.
        @param is_easy_propagation: Whether a collaps in the layer of concern propagates easy.
        @param is_layer_thin: Whether the layer of concern is thin.
        @param is_soft_slab_above: Whether the layer of concern has a soft slap above it.
        @param is_large_crystals: Whether the layer of concern consists of large crystals.
        @param comment: Comment regarding the avalanche problem.
        """
        if all(e is None for e in
               [weak_layer, layer_depth, avalanche_type, sensitivity, size, distribution, elevation, expositions,
                is_easy_propagation, is_layer_thin, is_soft_slab_above, is_large_crystals, comment]):
            raise NoObservationError("No argument passed to avalanche problem assessment.")

        self.weak_layer = weak_layer
        self.layer_depth = layer_depth
        self.avalanche_type = avalanche_type
        self.sensitivity = sensitivity
        self.size = size
        self.distribution = distribution
        self.elevation = elevation
        self.expositions = expositions
        self.is_easy_propagation = is_easy_propagation
        self.is_layer_thin = is_layer_thin
        self.is_soft_slab_above = is_soft_slab_above
        self.is_large_crystals = is_large_crystals
        self.comment = comment

    def to_dict(self) -> ObsDict:
        return {
            "weak_layer": self.weak_layer,
            "layer_depth": self.layer_depth,
            "avalanche_type": self.avalanche_type,
            "sensitivity": self.sensitivity,
            "size": self.size,
            "distribution": self.distribution,
            "elevation": self.elevation.to_dict() if self.elevation is not None else None,
            "expositions": self.expositions.to_dict() if self.expositions is not None else None,
            "is_easy_propagation": self.is_easy_propagation,
            "is_layer_thin": self.is_layer_thin,
            "is_soft_slab_above": self.is_soft_slab_above,
            "is_large_crystals": self.is_large_crystals,
            "comment": self.comment,
        }

    def serialize(self) -> ObsJson:
        obs = {
            'AvalCauseTID': self.weak_layer,
            'AvalCauseDepthTID': self.layer_depth,
            'AvalCauseAttributeLightTID': 1 if self.is_easy_propagation else None,
            'AvalCauseAttributeThinTID': 2 if self.is_layer_thin else None,
            'AvalCauseAttributeSoftTID': 4 if self.is_soft_slab_above else None,
            'AvalCauseAttributeCrystalTID': 8 if self.is_large_crystals else None,
            'AvalancheExtTID': self.avalanche_type,
            'AvalTriggerSimpleTID': self.sensitivity,
            'DestructiveSizeTID': self.size,
            'AvalPropagationTID': self.distribution,
            'Comment': self.comment,
            'ValidExposition': self.expositions.serialize() if self.expositions is not None else None,
        }
        if self.elevation is not None:
            obs = {**obs, **self.elevation.serialize()}
        return self._clean(obs)

    @classmethod
    def deserialize(cls, json: ObsJson) -> AvalancheProblem:
        elev = None
        if all(x in json for x in ["ExposedHeightComboTID", "ExposedHeight1"]):
            if None not in [json["ExposedHeightComboTID"], json["ExposedHeight1"]]:
                elev = Elevation.deserialize(json)
        problem = object.__new__(cls)
        problem.weak_layer = cls._convert(json, "AvalCauseTID", WeakLayer)
        problem.layer_depth = cls._convert(json, "AvalCauseDepthTID", cls.LayerDepth)
        problem.avalanche_type = cls._convert(json, "AvalancheExtTID", cls.Type)
        problem.sensitivity = cls._convert(json, "AvalTriggerSimpleTID", Sensitivity)
        problem.size = cls._convert(json, "DestructiveSizeTID", DestructiveSize)
        problem.distribution = cls._convert(json, "AvalPropagationTID", Distribution)
        problem.elevation = elev
        problem.expositions = cls._apply(json, "ValidExposition", lambda x: Expositions.deserialize(x))
        problem.is_easy_propagation = cls._convert(json, "AvalCauseAttributeLightTID", bool)
        problem.is_layer_thin = cls._convert(json, "AvalCauseAttributeThinTID", bool)
        problem.is_soft_slab_above = cls._convert(json, "AvalCauseAttributeSoftTID", bool)
        problem.is_large_crystals = cls._convert(json, "AvalCauseAttributeCrystalTID", bool)
        problem.comment = cls._convert(json, "Comment", str)
        return problem


class DangerAssessment(SnowObservation):
    OBSERVATION_TYPE = SnowRegistration.ObservationType.DANGER_ASSESSMENT

    class DangerLevel(IntEnum):
        ONE_LOW = 1
        TWO_MODERATE = 2
        THREE_CONSIDERABLE = 3
        FOUR_HIGH = 4
        FIVE_EXTREME = 5

    class ForecastEvaluation(IntEnum):
        CORRECT = 1
        TOO_LOW = 2
        TOO_HIGH = 3

    def __init__(self,
                 danger_level: Optional[DangerAssessment.DangerLevel] = None,
                 forecast_evaluation: Optional[DangerAssessment.ForecastEvaluation] = None,
                 danger_assessment: Optional[str] = None,
                 danger_development: Optional[str] = None,
                 comment: Optional[str] = None):
        """A danger assessment based on the rest of the registration.

        @param danger_level: The assessed danger level, between 1-5.
        @param forecast_evaluation: An evaluation of the issued forecast for the given day and region.
        @param danger_assessment: An assessment of the current danger in the area of the registration.
        @param danger_development: An assessment of the development of the danger in the area of the registration.
        @param comment: Comment regarding the danger assessment.
        """
        if all(e is None for e in [danger_level, forecast_evaluation, danger_assessment, danger_development, comment]):
            raise NoObservationError("No argument passed to avalanche danger assessment.")

        self.danger_level = danger_level
        self.forecast_evaluation = forecast_evaluation
        self.danger_assessment = danger_assessment
        self.danger_development = danger_development
        self.comment = comment

    def to_dict(self) -> ObsDict:
        return {
            "danger_level": self.danger_level,
            "forecast_evaluation": self.forecast_evaluation,
            "danger_assessment": self.danger_assessment,
            "danger_development": self.danger_development,
            "comment": self.comment,
        }

    def serialize(self) -> ObsJson:
        return self._clean({
            'AvalancheDangerTID': self.danger_level,
            'ForecastCorrectTID': self.forecast_evaluation,
            'AvalancheEvaluation': self.danger_assessment,
            'AvalancheDevelopment': self.danger_development,
            'ForecastComment': self.comment,
        })

    @classmethod
    def deserialize(cls, json: ObsJson) -> DangerAssessment:
        assessment = object.__new__(cls)
        assessment.danger_level = cls._convert(json, "AvalancheDangerTID", cls.DangerLevel)
        assessment.forecast_evaluation = cls._convert(json, "ForecastCorrectTID", cls.ForecastEvaluation)
        assessment.danger_assessment = cls._convert(json, "AvalancheEvaluation", str)
        assessment.danger_development = cls._convert(json, "AvalancheDevelopment", str)
        assessment.comment = cls._convert(json, "ForecastComment", str)
        return assessment


class Incident(SnowObservation):
    OBSERVATION_TYPE = SnowRegistration.ObservationType.INCIDENT

    class Activity(IntEnum):
        BACKCOUNTRY = 111
        OFF_PISTE = 113
        RESORT = 112
        NORDIC = 114
        CROSS_COUNTRY = 115
        CLIMBING = 116
        FOOT = 117
        SNOWMOBILE = 130
        ROAD = 120
        RAILWAY = 140
        BUILDING = 160
        OTHER = 190

    class Extent(IntEnum):
        NO_EFFECT = 10
        SAR = 13
        TRAFFIC = 15
        EVACUATION = 25
        MATERIAL_ONLY = 20
        CLOSE_CALL = 27
        BURIAL_UNHARMED = 28
        PEOPLE_HURT = 30
        FATAL = 40
        OTHER = 99

    def __init__(self,
                 activity: Optional[Incident.Activity] = None,
                 extent: Optional[Incident.Extent] = None,
                 comment: Optional[str] = None):
        """An avalanche incident risking health, property, the environment, or other things of value.

        @param activity: In what setting did the incident occur.
        @param extent: The extent of the damages to health, property, the environment, or other things of value.
        @param comment: Comment regarding the avalanche incident.
        """
        if all(e is None for e in [activity, extent, comment]):
            raise NoObservationError("No argument passed to incident observation.")

        self.activity = activity
        self.extent = extent
        self.comment = comment
        self.urls = []

    def to_dict(self) -> ObsDict:
        return {
            "activity": self.activity,
            "extent": self.extent,
            "comment": self.comment,
            "urls": list(map(lambda x: x.to_dict(), self.urls)),
        }

    def add_url(self, url: Url) -> Incident:
        """Adds an URL to the Incident.

        @param url: The Url object to add to the Incident.
        @return: self, with an added Url object.
        """
        self.urls.append(url)
        return self

    def serialize(self) -> ObsJson:
        return self._clean({
            'ActivityInfluencedTID': self.activity,
            'Comment': self.comment,
            'DamageExtentTID': self.extent,
            'IncidentURLs': list(map(lambda url: url.serialize(), self.urls)),
        })

    @classmethod
    def deserialize(cls, json: ObsJson) -> Incident:
        incident = object.__new__(cls)
        incident.activity = cls._convert(json, "ActivityInfluencedTID", cls.Activity)
        incident.extent = cls._convert(json, "DamageExtentTID", cls.Extent)
        incident.comment = cls._convert(json, "Comment", str)
        incident.urls = list(map(lambda url: Url.deserialize(url), json["IncidentURLs"]))
        return incident


class Note(SnowObservation):
    OBSERVATION_TYPE = SnowRegistration.ObservationType.NOTE

    def __init__(self, comment: str):
        """A general note for a registration.

        @param comment: Comment regarding the registration.
        """
        self.comment = comment
        self.urls = []

    def add_url(self, url: Url) -> Note:
        """Adds an URL to the Note.

        @param url: The Url object to add to the Note.
        @return: self, with an added Url object.
        """
        self.urls.append(url)
        return self

    def to_dict(self) -> ObsDict:
        return {
            "comment": self.comment,
            "urls": list(map(lambda x: x.to_dict(), self.urls)),
        }

    def serialize(self) -> ObsJson:
        return self._clean({
            'ObsComment': self.comment,
            'Urls': list(map(lambda url: url.serialize(), self.urls)),
        })

    @classmethod
    def deserialize(cls, json: ObsJson) -> Note:
        note = cls(comment=cls._convert(json, "ObsComment", str))
        note.urls = list(map(lambda url: Url.deserialize(url), json["Urls"]))
        return note


class ImageInterface:
    mime = None
    direction = None
    photographer = None
    copyright_holder = None
    comment = None


class Image(ImageInterface, Serializable, Dictable):
    def __init__(self,
                 file_path: str,
                 direction: Optional[Direction] = None,
                 photographer: Optional[str] = None,
                 copyright_holder: Optional[str] = None,
                 comment: Optional[str] = None):
        """Add an image to the danger sign schema

        @param file_path: Path to image file to add.
        @param direction: The aspect of the image.
        @param photographer: Name of the photographer.
        @param copyright_holder: Name of person or organisation holding the copyright to the image.
        @param comment: Comment regarding the avalanche observation.
        """
        self.mime, _ = mimetypes.guess_type(file_path, False)
        if self.mime is None or not re.match(r"^image", self.mime):
            raise ValueError("Could not recognize file name as an image.")

        self.uuid = None
        self.file_path = file_path
        self.direction = direction
        self.photographer = photographer
        self.copyright_holder = copyright_holder
        self.comment = comment

    def to_dict(self) -> ObsDict:
        return {
            "uuid": self.uuid,
            "file_path": self.file_path,
            "mime": self.mime,
            "direction": self.direction,
            "photographer": self.photographer,
            "copyright_holder": self.copyright_holder,
            "comment": self.comment,
        }

    def serialize(self) -> ObsJson:
        return self._clean({
            "AttachmentUploadId": self.uuid,
            "Aspect": self.direction * 45 if self.direction is not None else None,
            "AttachmentMimeType": self.mime,
            "Photographer": self.photographer,
            "Copyright": self.copyright_holder,
            "Comment": self.comment,
        })


# This class was created and published as a mistake.
# Just let it be.
class LocalImage(Image):
    pass


class UploadedImage(ImageInterface, Deserializable, Dictable):
    id = None
    url = None

    def to_dict(self) -> ObsDict:
        return {
            "id": self.id,
            "url": self.url,
            "mime": self.mime,
            "direction": self.direction,
            "photographer": self.photographer,
            "copyright_holder": self.copyright_holder,
            "comment": self.comment,
        }

    @classmethod
    def deserialize(cls, json: ObsJson) -> UploadedImage:
        img = cls()
        img.mime = cls._convert(json, "AttachmentMimeType", str)
        img.direction = cls._apply(json, "Aspect", lambda x: Direction(round(x / 45) % 8))
        img.photographer = cls._convert(json, "Photographer", str)
        img.copyright_holder = cls._convert(json, "Copyright", str),
        img.comment = cls._convert(json, "Comment", str)
        img.id = cls._convert(json, "AttachmentId", int),
        img.url = cls._convert(json, "Url", str)
        return img


class Url(Serializable, Deserializable, Dictable):
    def __init__(self, url: str, description: str):
        """Url object, containing an address and a description.

        @param url: The web address to link to.
        @param description: A general description of the provided URL.
        """
        self.description = description
        self.url = url

    def to_dict(self) -> ObsDict:
        return {
            "description": self.description,
            "url": self.url,
        }

    def serialize(self) -> Dict[str, str]:
        return self._clean({
            'UrlDescription': self.description,
            'UrlLine': self.url,
        })

    @classmethod
    def deserialize(cls, json: Dict[str, str]) -> Url:
        return cls(url=cls._convert(json, "UrlLine", str),
                   description=cls._convert(json, "UrlDescription", str))


class DestructiveSize(IntEnum):
    D1 = 1
    D2 = 2
    D3 = 3
    D4 = 4
    D5 = 5
    UNKNOWN = 9


class Sensitivity(IntEnum):
    VERY_DIFFICULT = 30
    DIFFICULT = 40
    EASY = 50
    VERY_EASY = 60
    SPONTANEOUS = 22


class Distribution(IntEnum):
    ISOLATED = 1
    SPECIFIC = 2
    WIDESPREAD = 3


class WeakLayer(IntEnum):
    PP = 10
    SH = 11
    FC_NEAR_SURFACE = 13
    BONDING_ABOVE_MFCR = 14
    DF = 15
    DH = 16
    FC_BELOW_MFCR = 19
    FC_ABOVE_MFCR = 18
    WATER_IN_SNOW = 22
    GROUND_MELT = 20
    LOOSE_SNOW = 24


class Position(Dictable):
    def __init__(self, lat: float, lon: float):
        """A position, in WGS84 (lat/long).

        @param lat: The latitude of the position.
        @param lon: The longitude of the position.
        """
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            raise ValueError("Latitude must be in the range -90--90, longitude -180--180.")

        self.lat = lat
        self.lon = lon

    def __repr__(self):
        rep = [
            f"Latitude: {'{0:.5f}'.format(self.lat)}",
            f"Longitude: {'{0:.5f}'.format(self.lon)}"
        ]
        return f"Position( {', '.join(rep)} )"

    def to_dict(self) -> ObsDict:
        return {
            "lat": self.lat,
            "lon": self.lon,
        }


class Observer(Dictable):
    class Competence(IntEnum):
        UNKNOWN = 0
        SNOW_UNKNOWN = 100
        SNOW_AUTOMATIC = 105
        SNOW_BASIC_SKILLS = 110
        SNOW_EXPERIENCED_NO_COURSE = 115
        SNOW_HAS_BASIC_COURSE = 120
        SNOW_HAS_EXTENDED_COURSE = 130
        SNOW_AVA_FORECASTER = 150

    nickname = None
    id = None
    competence = None

    def to_dict(self) -> ObsDict:
        return {
            "nickname": self.nickname,
            "id": self.id,
            "competence": self.competence,
        }


class Elevation(Serializable, Deserializable, Dictable):
    class Format(IntEnum):
        ABOVE = 1
        BELOW = 2
        SANDWICH = 3
        MIDDLE = 4

    def __init__(self, elev_fmt: Elevation.Format, elev: int,
                 elev_secondary: Optional[int] = None):
        """An elevation band specification.

        - If C{elev_fmt == 1}, then the elevation band represents all elevations above C{elev}
        - If C{elev_fmt == 2}, then the elevation band represents all elevations below C{elev}
        - If C{elev_fmt == 3}, elevations above C{elev} as well as elevations below C{elev_secondary} are represented.
        - If C{elev_fmt == 4}, elevations between C{elev} and C{elev_secondary} are represented.

        @param elev_fmt: The format of the elevation band.
        @param elev: The first elevation of the elevation band.
        @param elev_secondary: The second elevation of the elevation band.
        """
        if not (0 <= elev <= 4808) or (elev_secondary is not None and not (0 <= elev_secondary <= 4808)):
            raise ValueError("Elevations must be in the range 0--4808 m.a.s.l.")
        if (elev_fmt == self.Format.ABOVE or elev_fmt == self.Format.BELOW) and elev_secondary is not None:
            raise ValueError("ABOVE and BELOW elevation formats does not use parameter elev_secondary.")
        elif (elev_fmt == self.Format.SANDWICH or elev_fmt == self.Format.MIDDLE) and elev_secondary is None:
            raise ValueError("SANDWICH and MIDDLE elevation formats must use parameter elev_secondary.")

        if elev_secondary is not None:
            self.elev_max = round(round(max(elev, elev_secondary), -2))
            self.elev_min = round(round(min(elev, elev_secondary), -2))
            self.elev_min -= 100 if self.elev_max == self.elev_min else 0
        else:
            self.elev_max = elev
            self.elev_min = None
        self.format = elev_fmt

    def to_dict(self) -> ObsDict:
        return {
            "format": self.format,
            "elev_max": self.elev_max,
            "elev_min": self.elev_min,
        }

    def serialize(self) -> Dict[str, int]:
        return self._clean({
            'ExposedHeightComboTID': self.format,
            'ExposedHeight1': self.elev_max,
            'ExposedHeight2': self.elev_min,
        })

    @classmethod
    def deserialize(cls, json: Dict[str, int]) -> Elevation:
        elevation = object.__new__(cls)
        elev_fmt = cls._convert(json, "ExposedHeightComboTID", cls.Format)
        elev = cls._convert(json, "ExposedHeight1", int)
        elev_secondary = cls._convert(json, "ExposedHeight2", int)

        if elev_secondary is not None:
            elevation.elev_max = max(elev, elev_secondary)
            elevation.elev_min = min(elev, elev_secondary)
        else:
            elevation.elev_max = elev
            elevation.elev_min = None
        elevation.format = elev_fmt
        return elevation


class Expositions(Serializable, Deserializable, Dictable):
    def __init__(self, expositions: List[Direction]):
        """A collection of directions.

        @param expositions: The directions to include into the collection.
        """
        self.expositions = expositions

    def to_dict(self) -> ObsDict:
        return {
            "expositions": self.expositions
        }

    def serialize(self) -> str:
        exp = "00000000"
        for exposition in self.expositions:
            exp = exp[:exposition] + "1" + exp[exposition + 1:]
        return exp

    @classmethod
    def deserialize(cls, json: str) -> Expositions:
        if len(json) > 8:
            raise ValueError("Exposition string too long.")
        valids = map(lambda x: bool(int(x)), json)
        expositions = []
        for i, valid in enumerate(valids):
            if valid:
                expositions.append(Direction(i))
        return cls(expositions)


class Direction(IntEnum):
    N = 0
    NE = 1
    E = 2
    SE = 3
    S = 4
    SW = 5
    W = 6
    NW = 7
