from regobslib import *
import datetime as dt


# Contact regobs@nve.no to get a client ID.
CLIENT_ID = "00000000-0000-0000-0000-000000000000"

# Create a user at https://test-konto.nve.no/ or https://konto.nve.no/
USERNAME = "ola.nordmann@example.com"
PASSWORD = "P4ssw0rd"


reg = SnowRegistration(REGOBS_TZ.localize(dt.datetime(2021, 10, 6, 10, 15)),
                       Position(lat=68.4293, lon=18.2572),
                       SnowRegistration.SpatialPrecision.ONE_HUNDRED,
                       SnowRegistration.Source.SEEN)

reg.add_danger_sign(DangerSign(DangerSign.Sign.WHUMPF_SOUND))
reg.add_danger_sign(DangerSign(DangerSign.Sign.QUICK_TEMP_CHANGE, "Very quick!"))
reg.add_danger_sign(DangerSign(comment="It just felt dangerous."))

reg.add_image(Image("img/apollo.jpg",
                    Direction.NE,
                    photographer="Apollo",
                    copyright_holder="NASA",
                    comment="There's no snow on the moon."),
              DangerSign)

reg.set_avalanche_obs(AvalancheObs(REGOBS_TZ.localize(dt.datetime(2021, 3, 21, 16, 5)),
                                   Position(lat=61.1955, lon=10.3711),
                                   Position(lat=60.8071, lon=7.9102),
                                   Direction.NE,
                                   DestructiveSize.D3,
                                   AvalancheObs.Type.DRY_SLAB,
                                   AvalancheObs.Trigger.NATURAL,
                                   AvalancheObs.Terrain.CLOSE_TO_RIDGE,
                                   WeakLayer.GROUND_MELT,
                                   fracture_height_cm=225,
                                   fracture_width=700,
                                   path_name="Path A",
                                   comment="Extremely long path."))

reg.add_avalanche_activity(AvalancheActivity(dt.date(2021, 2, 25),
                                             AvalancheActivity.Timeframe.SIX_TO_TWELVE,
                                             AvalancheActivity.Quantity.FEW,
                                             AvalancheActivity.Type.DRY_SLAB,
                                             Sensitivity.SPONTANEOUS,
                                             DestructiveSize.D4,
                                             Distribution.SPECIFIC,
                                             Elevation(Elevation.Format.ABOVE, 500),
                                             Expositions([Direction.NE, Direction.S]),
                                             "Avalanche activity above 500 masl"))

reg.set_weather(Weather(Weather.Precipitation.DRIZZLE,
                        Direction.NE,
                        wind_speed=2.2,
                        cloud_cover_percent=15))

reg.set_snow_cover(SnowCover(SnowCover.Drift.MODERATE,
                             SnowCover.Surface.WIND_SLAB_HARD,
                             hn24_cm=9.2,
                             new_snow_line=101,
                             hs_cm=243.7,
                             snow_line=2300,
                             layered_snow_line=203.6))

reg.add_compression_test(CompressionTest(CompressionTest.TestResult.ECTP,
                                         CompressionTest.FractureQuality.Q1,
                                         CompressionTest.Stability.POOR,
                                         number_of_taps=3,
                                         fracture_depth_cm=15.355,
                                         is_in_profile=True,
                                         comment="This is a comment."))

reg.add_compression_test(CompressionTest(CompressionTest.TestResult.ECTN,
                                         CompressionTest.FractureQuality.Q3,
                                         CompressionTest.Stability.GOOD,
                                         number_of_taps=26,
                                         fracture_depth_cm=55.54,
                                         is_in_profile=False))

reg.set_snow_profile(SnowProfile(layers=[SnowProfile.Layer(15,
                                                           SnowProfile.Hardness.ONE_FINGER,
                                                           SnowProfile.GrainForm.PP,
                                                           SnowProfile.GrainSize.TWO,
                                                           SnowProfile.Wetness.D,
                                                           SnowProfile.Hardness.FOUR_FINGERS,
                                                           SnowProfile.GrainForm.DF,
                                                           SnowProfile.GrainSize.ONE),
                                         SnowProfile.Layer(0.5,
                                                           SnowProfile.Hardness.FIST,
                                                           SnowProfile.GrainForm.SH,
                                                           SnowProfile.GrainSize.FIVE,
                                                           critical_layer=SnowProfile.CriticalLayer.WHOLE,
                                                           comment="This is what I'm worried about"),
                                         SnowProfile.Layer(2,
                                                           SnowProfile.Hardness.ICE,
                                                           SnowProfile.GrainForm.MF_CR)
                                        ],
                                 temperatures=[SnowProfile.SnowTemp(10, -4)],
                                 densities=[SnowProfile.Density(50, 300)],
                                 is_profile_to_ground=False,
                                 comment="SH above MFcr. Very PWL. Much dangerous."))

reg.add_avalanche_problem(AvalancheProblem(WeakLayer.FC_ABOVE_MFCR,
                                           AvalancheProblem.LayerDepth.LESS_THAN_50_CM,
                                           AvalancheProblem.Type.DRY_SLAB,
                                           Sensitivity.VERY_EASY,
                                           DestructiveSize.D3,
                                           Distribution.SPECIFIC,
                                           Elevation(Elevation.Format.ABOVE, 500),
                                           Expositions([Direction.N, Direction.NE]),
                                           is_easy_propagation=True,
                                           is_layer_thin=True,
                                           is_soft_slab_above=False,
                                           is_large_crystals=False,
                                           comment="A sketchy persistent weak slab."))

reg.set_danger_assessment(DangerAssessment(DangerAssessment.DangerLevel.FOUR_HIGH,
                                           DangerAssessment.ForecastEvaluation.TOO_LOW,
                                           "It's very dangerous out there.",
                                           "I hope tomorrow is better.",
                                           "This is a comment."))

reg.set_incident(Incident(Incident.Activity.CLIMBING,
                          Incident.Extent.CLOSE_CALL,
                          "Scary."
                          ).add_url(Url("https://nve.no", "NVE")))

reg.set_note(Note("Demo registration via Python client API."
                  ).add_url(Url("https://varsom.no", "Varsom")))

connection = Connection(prod=False).authenticate(USERNAME, PASSWORD, CLIENT_ID)
stored_reg = connection.submit(reg)
print(stored_reg)
