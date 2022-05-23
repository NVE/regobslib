from enum import IntEnum


class Region(IntEnum):
    pass


class SnowRegion(Region):
    SVALBARD_OST = 3001
    SVALBARD_VEST = 3002
    NORDENSKIOLD_LAND = 3003
    SVALBARD_SOR = 3004
    OST_FINNMARK = 3005
    FINNMARKSKYSTEN = 3006
    VEST_FINNMARK = 3007
    FINNMARKSVIDDA = 3008
    NORD_TROMS = 3009
    LYNGEN = 3010
    TROMSO = 3011
    SOR_TROMS = 3012
    INDRE_TROMS = 3013
    LOFOTEN_OG_VESTERALEN = 3014
    OFOTEN = 3015
    SALTEN = 3016
    SVARTISEN = 3017
    HELGELAND = 3018
    NORD_TRONDELAG = 3019
    SOR_TRONDELAG = 3020
    YTRE_NORDMORE = 3021
    TROLLHEIMEN = 3022
    ROMSDAL = 3023
    SUNNMORE = 3024
    NORD_GUDBRANDSDALEN = 3025
    YTRE_FJORDANE = 3026
    INDRE_FJORDANE = 3027
    JOTUNHEIMEN = 3028
    INDRE_SOGN = 3029
    VOSS = 3031
    HALLINGDAL = 3032
    HORDALANDSKYSTEN = 3033
    HARDANGER = 3034
    VEST_TELEMARK = 3035
    ROGALANDSKYSTEN = 3036
    HEIANE = 3037
    AGDER_SOR = 3038
    TELEMARKS_SOR = 3039
    VESTFOLD = 3040
    BUSKERUD_SOR = 3041
    OPPLAND_SOR = 3042
    HEDMARK = 3043
    AKERSHUS = 3044
    OSLO = 3045
    OSTFOLD = 3046


SVALBARD_REGIONS = [
    SnowRegion.SVALBARD_OST,
    SnowRegion.SVALBARD_VEST,
    SnowRegion.NORDENSKIOLD_LAND,
    SnowRegion.SVALBARD_SOR,
]


A_REGIONS = [
    SnowRegion.NORDENSKIOLD_LAND,
    SnowRegion.FINNMARKSKYSTEN,
    SnowRegion.VEST_FINNMARK,
    SnowRegion.NORD_TROMS,
    SnowRegion.LYNGEN,
    SnowRegion.TROMSO,
    SnowRegion.SOR_TROMS,
    SnowRegion.INDRE_TROMS,
    SnowRegion.LOFOTEN_OG_VESTERALEN,
    SnowRegion.OFOTEN,
    SnowRegion.SALTEN,
    SnowRegion.SVARTISEN,
    SnowRegion.HELGELAND,
    SnowRegion.TROLLHEIMEN,
    SnowRegion.ROMSDAL,
    SnowRegion.SUNNMORE,
    SnowRegion.INDRE_FJORDANE,
    SnowRegion.JOTUNHEIMEN,
    SnowRegion.INDRE_SOGN,
    SnowRegion.VOSS,
    SnowRegion.HALLINGDAL,
    SnowRegion.HARDANGER,
    SnowRegion.VEST_TELEMARK,
    SnowRegion.HEIANE,
]


A_REGIONS_MAINLAND = [
    region for region in A_REGIONS if region not in SVALBARD_REGIONS
]

B_REGIONS = [
    region for region in SnowRegion if region not in A_REGIONS
]

B_REGIONS_MAINLAND = [
    region for region in B_REGIONS if region not in SVALBARD_REGIONS
]


REGION_ROOF = {
    SnowRegion.SVALBARD_OST: 1500,
    SnowRegion.SVALBARD_VEST: 1200,
    SnowRegion.NORDENSKIOLD_LAND: 800,
    SnowRegion.SVALBARD_SOR: 800,
    SnowRegion.OST_FINNMARK: 1000,
    SnowRegion.FINNMARKSKYSTEN: 1000,
    SnowRegion.VEST_FINNMARK: 1200,
    SnowRegion.FINNMARKSVIDDA: 1000,
    SnowRegion.NORD_TROMS: 1500,
    SnowRegion.LYNGEN: 1500,
    SnowRegion.TROMSO: 1000,
    SnowRegion.SOR_TROMS: 1000,
    SnowRegion.INDRE_TROMS: 1500,
    SnowRegion.LOFOTEN_OG_VESTERALEN: 1000,
    SnowRegion.OFOTEN: 1500,
    SnowRegion.SALTEN: 1500,
    SnowRegion.SVARTISEN: 1500,
    SnowRegion.HELGELAND: 1500,
    SnowRegion.NORD_TRONDELAG: 1500,
    SnowRegion.SOR_TRONDELAG: 1500,
    SnowRegion.YTRE_NORDMORE: 1000,
    SnowRegion.TROLLHEIMEN: 2000,
    SnowRegion.ROMSDAL: 2000,
    SnowRegion.SUNNMORE: 2000,
    SnowRegion.NORD_GUDBRANDSDALEN: 2000,
    SnowRegion.YTRE_FJORDANE: 1500,
    SnowRegion.INDRE_FJORDANE: 2000,
    SnowRegion.JOTUNHEIMEN: 2500,
    SnowRegion.INDRE_SOGN: 2000,
    SnowRegion.VOSS: 1500,
    SnowRegion.HALLINGDAL: 2000,
    SnowRegion.HORDALANDSKYSTEN: 1000,
    SnowRegion.HARDANGER: 2000,
    SnowRegion.VEST_TELEMARK: 1500,
    SnowRegion.ROGALANDSKYSTEN: 1000,
    SnowRegion.HEIANE: 1500,
    SnowRegion.AGDER_SOR: 1000,
    SnowRegion.TELEMARKS_SOR: 1500,
    SnowRegion.VESTFOLD: 800,
    SnowRegion.BUSKERUD_SOR: 1500,
    SnowRegion.OPPLAND_SOR: 1500,
    SnowRegion.HEDMARK: 2000,
    SnowRegion.AKERSHUS: 800,
    SnowRegion.OSLO: 600,
    SnowRegion.OSTFOLD: 400,
}
