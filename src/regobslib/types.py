"""Enums and types used in Regobs
"""
from enum import IntEnum, Enum

from .misc import FloatEnum

__author__ = 'arwi'


class DangerLevel(IntEnum):
    ONE_LOW = 1
    TWO_MODERATE = 2
    THREE_CONSIDERABLE = 3
    FOUR_HIGH = 4
    FIVE_EXTREME = 5


class VarsomAvalancheProblem:
    class Sensitivity(IntEnum):
        HIGH_LOAD = 10
        LOW_LOAD = 21
        SPONTANEOUS = 22

    class Probability(IntEnum):
        UNLIKELY = 2
        POSSIBLE = 3
        LIKELY = 5

    class Type(IntEnum):
        NEW_LOOSE = 3
        WET_LOOSE = 5
        NEW_SLAB = 7
        WIND_SLAB = 10
        PWL_SLAB = 30
        WET_SLAB = 45
        GLIDE_SLAB = 50


class Registration:
    GEO_HAZARD = None


class Observation:
    OBSERVATION_TYPE = None


class SnowObservation(Observation):
    pass


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


class DangerAssessment(SnowObservation):
    OBSERVATION_TYPE = SnowRegistration.ObservationType.DANGER_ASSESSMENT

    DangerLevel = DangerLevel

    class ForecastEvaluation(IntEnum):
        CORRECT = 1
        TOO_LOW = 2
        TOO_HIGH = 3


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


class Note(SnowObservation):
    OBSERVATION_TYPE = SnowRegistration.ObservationType.NOTE


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


class Observer:
    class Competence(IntEnum):
        UNKNOWN = 0
        SNOW_UNKNOWN = 100
        SNOW_AUTOMATIC = 105
        SNOW_BASIC_SKILLS = 110
        SNOW_EXPERIENCED_NO_COURSE = 115
        SNOW_HAS_BASIC_COURSE = 120
        SNOW_HAS_EXTENDED_COURSE = 130
        SNOW_AVA_FORECASTER = 150


class Elevation:
    class Format(IntEnum):
        ABOVE = 1
        BELOW = 2
        SANDWICH = 3
        MIDDLE = 4


class Direction(IntEnum):
    N = 0
    NE = 1
    E = 2
    SE = 3
    S = 4
    SW = 5
    W = 6
    NW = 7
