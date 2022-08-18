# To enable postponed evaluation of annotations (default for 3.10)
from __future__ import annotations

import datetime as dt
from enum import Enum, IntEnum

import pandas as pd
from collections import OrderedDict
from typing import Union, Type, List, Dict, Optional, cast, Iterator, TypeVar, Callable

from . import types
from .misc import Container, Ordered, OrderedElements
from .region import SnowRegion, REGION_ROOF
from .submit import Dictable, Expositions, Elevation, Deserializable
from .types import DangerLevel, DestructiveSize, Distribution, Direction

VarsomJsonProb = Dict[str, Union[int, str]]
VarsomJsonReg = Dict[str, Union[int, str, List['VarsomJsonReg'], 'VarsomJsonReg']]
VarsomJsonFull = List[VarsomJsonReg]
VarsomJson = Union[VarsomJsonFull, VarsomJsonReg, VarsomJsonProb]
VarsomDict = dict


T = TypeVar('T')
U = TypeVar('U')


class Frameable:
    def to_problem_frame(self) -> pd.DataFrame:
        raise NotImplementedError()

    def to_problem_csv(self, filename: str) -> Optional[str]:
        return self.to_problem_frame().to_csv(filename, sep=";")

    @staticmethod
    def read_csv(filename: str) -> pd.DataFrame:
        raise NotImplementedError()


class VarsomDeserializable(Deserializable):
    @classmethod
    def deserialize(cls, json: VarsomJson) -> VarsomDeserializable:
        raise NotImplementedError()

    @staticmethod
    def _convert(json: VarsomJson, idx: str, target: Type[T], target_sec: Optional[Type[U]] = int) -> Union[T, U]:
        elem = json[idx] if idx in json else None
        try:
            return target(elem) if elem else None
        except ValueError:
            return target_sec(elem)

    @staticmethod
    def _apply(json: VarsomJson, idx: str, apply: Callable[[Union[str, int, float]], T] = None) -> Optional[T]:
        elem = json[idx] if idx in json else None
        return apply(elem) if elem else None


class SnowVarsom(Container, VarsomDeserializable, Dictable, Frameable):
    """A collection of regions with timelines of Varsom avalanche forecasts

    The object is indexable and iterable.

    Structure:
    Aps -> {SnowRegion: Timeline} -> {dt.Date: Day} -> [Level] -> Data
    """
    _elems: OrderedDict[SnowRegion, Timeline]

    def to_problem_frame(self, with_priorities: bool = False) -> pd.Frame:
        df = pd.concat({
            timeline.get_region(): timeline.to_problem_frame(with_priorities)
            for timeline in self
        }, names=["region", "date"])
        df.name = "snow_varsom"
        df = df.astype('float')
        df.index = df.index.set_levels([
            df.index.levels[0],
            pd.to_datetime(df.index.levels[1]),
        ])
        return df

    def to_danger_level_series(self):
        series = pd.concat({
            timeline.get_region(): timeline.to_danger_level_series()
            for timeline in self
        }, names=["region", "date"])
        series.name = "danger_level"
        series = series.astype('float')
        series.index = series.index.set_levels([
            series.index.levels[0],
            pd.to_datetime(series.index.levels[1]),
        ])
        return series

    def to_dict(self) -> VarsomDict:
        return {
            timeline.get_region(): timeline.to_dict()
            for timeline in self._sort()._filter_empty() if timeline
        }

    @staticmethod
    def read_csv(filename: str) -> pd.DataFrame:
        df = pd.read_csv(filename, sep=";", header=[0, 1], index_col=[0, 1])
        df.index = df.index.set_levels([
            df.index.levels[0],
            pd.to_datetime(df.index.levels[1]),
        ])
        return df

    @classmethod
    def deserialize(cls, json: VarsomJsonFull) -> SnowVarsom:
        varsom = cls()
        for region in SnowRegion:
            forecasts = [f for f in json if f["RegionId"] == region]
            timeline = Timeline.deserialize(forecasts)
            if timeline:
                varsom._elems[region] = timeline
        return varsom

    def _sort(self) -> SnowVarsom:
        return cast(SnowVarsom, super()._sort())

    def _filter_empty(self) -> SnowVarsom:
        return cast(SnowVarsom, super()._filter_empty())

    def __getitem__(self,
                    key: Union[dt.date,
                               SnowRegion,
                               slice,
                               List[dt.date],
                               List[SnowRegion]]) -> Union[Timeline, SnowVarsom]:
        if isinstance(key, dt.date) \
                or isinstance(key, slice) and (isinstance(key.start, dt.date) or isinstance(key.stop, dt.date)) \
                or isinstance(key, list) and len(key) and isinstance(key[0], dt.date):
            varsom = type(self)()
            for timeline in self:
                varsom[timeline.get_region()] = timeline[key]
            return varsom
        return cast(Union[Timeline, SnowVarsom], super().__getitem__(key))

    def __setitem__(self, key: SnowRegion, elem: Timeline) -> None:
        return super().__setitem__(key, elem)

    def __iter__(self) -> Iterator[Timeline]:
        return cast(Iterator[Timeline], super().__iter__())


class Timeline(Container, VarsomDeserializable, Dictable, Frameable):
    """A collection of Days with APS data

    The object is indexable and iterable.

    Structure:
    Timeline -> {dt.Date: Day} -> [Level] -> Data
    """

    def to_problem_frame(self, with_priorities: bool = False) -> pd.Frame:
        df = pd.concat({
            forecast.date.isoformat(): forecast.to_problem_series(with_priorities)
            for forecast in self
        }, axis=1).T
        df.index.name = "date"
        df.columns.set_names(["problem", "attr"])
        df.name = self.get_region()
        df.index = pd.to_datetime(df.index)
        return df

    def to_danger_level_series(self):
        return pd.Series({
            forecast.date.isoformat(): forecast.danger_level
            for forecast in self
        }, name="danger_level")

    def to_dict(self) -> VarsomDict:
        return {
            forecast.date.isoformat(): forecast.to_dict()
            for forecast in self._sort()._filter_empty() if forecast
        }

    def get_region(self) -> SnowRegion:
        if not self:
            raise ValueError("No forecasts to find region from")
        return next(iter(self)).region

    @staticmethod
    def read_csv(filename: str) -> pd.DataFrame:
        df = pd.read_csv(filename, sep=";", header=[0, 1], index_col=[0])
        df.index = pd.to_datetime(df.index)
        return df

    @classmethod
    def deserialize(cls, json: VarsomJsonFull) -> Timeline:
        timeline = cls()
        for forecast_json in filter(lambda f: int(f["DangerLevel"]), json):
            forecast = AvalancheForecast.deserialize(forecast_json)
            timeline[forecast.date] = forecast
        return timeline

    def _sort(self) -> Timeline:
        return cast(Timeline, super()._sort())

    def _filter_empty(self) -> Timeline:
        return cast(Timeline, super()._filter_empty())

    def __getitem__(self, key: Union[dt.date, slice, List[dt.date]]) -> Union[AvalancheForecast, Timeline]:
        return cast(Union[AvalancheForecast, Timeline], super().__getitem__(key))

    def __setitem__(self, key: Ordered, elem: OrderedElements):
        return super().__setitem__(key, elem)

    def __iter__(self) -> Iterator[AvalancheForecast]:
        return cast(Iterator[AvalancheForecast], super().__iter__())


class AvalancheForecast(Dictable, VarsomDeserializable):
    def __init__(self):
        self.region = None
        self.primary_region = None
        self.date = None

        self.danger_level = None
        self.emergency_warning = None
        self.problems = []

    def to_problem_series(self, with_priorities: bool = False) -> pd.Series:
        serieses = {}
        for priority, problem in enumerate(self.problems):
            try:
                name = problem.type.name.lower()
            except AttributeError:
                # There is at least one forecast with an unspecified
                # avalanche problem. That does not fit into the format
                # we use.
                if problem.type is None:
                    continue
                name = problem.type
            priority = priority + 1 if with_priorities else None
            serieses[name] = problem.to_series(REGION_ROOF[self.region], priority)
        if self.problems and serieses:
            series = pd.concat(serieses)
        else:
            series = pd.Series(dtype=float)
        problems = [p.name.lower() for p in AvalancheProblem.Type]
        attrs = ["priority"] if with_priorities else []
        attrs += ["size", "sensitivity", "distribution", "probability", "elevation_min", "elevation_max"]
        attrs += [f"exposition_{e}" for e in ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]]
        index = pd.MultiIndex.from_product([problems, attrs], names=["problem", "attr"])
        series = series.reindex(index)
        series.name = "forecast"
        return series


    def to_dict(self) -> VarsomDict:
        return {
            "danger_level": self.danger_level,
            "emergency_warning": self.emergency_warning,
            "problems": [p.to_dict() for p in self.problems]
        }

    @classmethod
    def deserialize(cls, json: VarsomJsonReg) -> AvalancheForecast:
        forecast = cls()
        forecast.region = cls._convert(json, "RegionId", SnowRegion)
        forecast.primary_region = cls._apply(json, "RegionTypeName", lambda t: t == "A")
        forecast.date = cls._apply(json, "ValidFrom", lambda d: dt.date.fromisoformat(d[:10]))
        forecast.danger_level = cls._convert(json, "DangerLevel", DangerLevel)
        forecast.emergency_warning = cls._apply(json,
                                                "EmergencyWarning",
                                                lambda w: w == "Naturlig utløste skred")
        forecast.problems = [AvalancheProblem.deserialize(p) for p in json["AvalancheProblems"]]
        return forecast


class AvalancheProblem(types.VarsomAvalancheProblem, Dictable, VarsomDeserializable):
    def __init__(self):
        self.type = None
        self.size = None
        self.sensitivity = None
        self.distribution = None
        self.probability = None
        self.expositions = None
        self.elevation = None

    def to_series(self, roof: int = 2500, with_priority: int = None) -> pd.Series:
        elev_min, elev_max = {
            Elevation.Format.ABOVE: lambda e: (e.elev_max, roof),
            Elevation.Format.BELOW: lambda e: (0, e.elev_max),
            Elevation.Format.SANDWICH: lambda e: (0, roof),
            Elevation.Format.MIDDLE: lambda e: (e.elev_min, e.elev_max),
        }.get(self.elevation.format, lambda e: (None, None))(self.elevation)

        dictionary = {}
        if with_priority is not None:
            dictionary["priority"] = with_priority
        dictionary["size"] = self.size
        dictionary["sensitivity"] = self.sensitivity
        dictionary["distribution"] = self.distribution
        dictionary["probability"] = self.probability
        dictionary["elevation_min"] = elev_min
        dictionary["elevation_max"] = elev_max
        dictionary["exposition_N"] = Direction.N in self.expositions if self.expositions else None
        dictionary["exposition_NE"] = Direction.NE in self.expositions if self.expositions else None
        dictionary["exposition_E"] = Direction.E in self.expositions if self.expositions else None
        dictionary["exposition_SE"] = Direction.SE in self.expositions if self.expositions else None
        dictionary["exposition_S"] = Direction.S in self.expositions if self.expositions else None
        dictionary["exposition_SW"] = Direction.SW in self.expositions if self.expositions else None
        dictionary["exposition_W"] = Direction.W in self.expositions if self.expositions else None
        dictionary["exposition_NW"] = Direction.NW in self.expositions if self.expositions else None

        series = pd.Series(dictionary)
        series.index.set_names("attr")
        try:
            series.name = self.type.name.lower()
        except AttributeError:
            series.name = self.type
        return series

    def to_dict(self) -> VarsomDict:
        return {
            "type": self.type,
            "size": self.size,
            "sensitivity": self.sensitivity,
            "distribution": self.distribution,
            "probability": self.probability,
            "expositions": self.expositions.to_dict(),
            "elevation": self.elevation.to_dict(),
        }

    @classmethod
    def deserialize(cls, json: VarsomJsonProb) -> AvalancheProblem:
        problem = cls()
        type = cls._convert(json, "AvalancheProblemTypeId", cls.Type)
        # Handling for old problem DEEP_PWL_SLAB
        problem.type = type if type != 37 else cls.Type.PWL_SLAB
        problem.size = cls._convert(json, "DestructiveSizeId", DestructiveSize)
        problem.sensitivity = cls._convert(json, "AvalTriggerSimpleId", cls.Sensitivity)
        problem.distribution = cls._convert(json, "AvalPropagationId", Distribution)
        problem.probability = cls._convert(json, "AvalProbabilityId", cls.Probability)
        problem.expositions = cls._deserialize_to(json, "ValidExpositions", Expositions)

        elevation = {
            "ExposedHeight1": json["ExposedHeight1"],
            "ExposedHeight2": json["ExposedHeight2"],
            "ExposedHeightComboTID": json["ExposedHeightFill"],
        }
        problem.elevation = Elevation.deserialize(elevation)
        return problem
