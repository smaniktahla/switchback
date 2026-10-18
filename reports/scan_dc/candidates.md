# US-211-like stretches within ~2 h of DC (VA, MD, WV)


**How to read this.** Matching is strict on purpose: 4 measured features must all sit near the US-211 climb's own values for at least 3 km. Only 9 stretches in VA/MD/WV pass the strict test and 48 the relaxed one (this list, relaxed +/-40%). Distance from DC is straight-line; 110 miles stands in for 'two hours'. Rows marked *suburban, check* are within 30 km of DC and probably low-speed with many intersections; geometry alone cannot tell. Surface is only assumed paved for trunk/primary/secondary/tertiary roads with no explicit unpaved tag; Up/Down is from 10 m elevation data and may be off on bridges. Visibility (sight distance) has not been applied to these yet.

Template: the US-211 climb (Sperryville to Thornton Gap), 4.8 km. A stretch is 3-10 km of paved public road whose 1 km windows all sit inside the climb's own range (+/-25%): heading change 241-799 deg/km, median radius 69-217 m, 2.3-7.5 turns >= 45 deg/km, 7-39% straight. Ranked by closeness to the centre of that range (fit 100 = dead centre, 0 = edge).

| # | Road | Where | Len km | Fit | Turns>=45/km | Radius m | Straight | Up/Down m | Grade | From DC | Map |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Skyline Drive (secondary) | VA, <bound method NDFrame.where of chain_idx                                                                    1577
road_key                                                            Skyline Drive
highway                                                                 secondary
state                                                                          VA
s0                                                                   97554.066312
s1                                                                  106054.066312
length_m                                                                   8500.0
score                                                                    0.463449
match_share                                                                   1.0
deg_per_km                                                             350.853555
radius_p50                                                             137.814966
turns_per_km_45                                                          3.650147
turns_per_km_15                                                           4.59212
frac_straight                                                            0.234179
frac_R_lt_50                                                                  0.0
straight_max_m                                                         209.925858
lon                             [-78.349183, -78.34907, -78.348957, -78.348846...
lat                             [38.615612, 38.615628, 38.615646, 38.615665, 3...
mid_lon                                                                -78.322581
mid_lat                                                                 38.622493
rank                                                                            1
dist_to_us211_ref_km                                                     5.300722
where                                                      9 km SW of Sperryville
from_dc                                                                  116 km W
gain_m                                                                 115.433043
loss_m                                                                 275.811748
net_m                                                                 -160.378705
mean_abs_grade_pct                                                       4.677082
max_sustained_grade_250m_pct                                             7.329666
gmaps                           https://www.google.com/maps/dir/?api=1&origin=...
osm                             https://www.openstreetmap.org/?mlat=38.622493&...
fit                                                                          54.0
Name: 0, dtype: object> | 8.5 | 54 | 3.7 | 138 | 23% | +115/-276 | 4.7% | 116 km W | [Google](https://www.google.com/maps/dir/?api=1&origin=38.615612,-78.349183&destination=38.650168,-78.310561&waypoints=38.619255,-78.342439%7C38.62588,-78.34007%7C38.62356,-78.332683%7C38.624801,-78.325481%7C38.625652,-78.322247%7C38.633301,-78.322168%7C38.636609,-78.314283%7C38.643439,-78.309401&travelmode=driving) / [OSM](https://www.openstreetmap.org/?mlat=38.622493&mlon=-78.322581#map=13/38.622493/-78.322581) |
| 2 | Williams Road Southeast (tertiary) | MD, <bound method NDFrame.where of chain_idx                                                                    3294
road_key                                                  Williams Road Southeast
highway                                                                  tertiary
state                                                                          MD
s0                                                                    3054.192951
s1                                                                    6554.192951
length_m                                                                   3500.0
score                                                                    0.468371
match_share                                                                   1.0
deg_per_km                                                             398.364735
radius_p50                                                             154.761418
turns_per_km_45                                                          3.998088
turns_per_km_15                                                          5.711555
frac_straight                                                            0.282292
frac_R_lt_50                                                              0.07155
straight_max_m                                                         379.947096
lon                             [-78.703705, -78.703602, -78.703496, -78.70338...
lat                             [39.638069, 39.63811, 39.638147, 39.638181, 39...
mid_lon                                                                -78.687284
mid_lat                                                                 39.636328
rank                                                                            2
dist_to_us211_ref_km                                                   112.744049
where                                                    5 km S of Pleasant Grove
from_dc                                                                 164 km NW
gain_m                                                                  112.74123
loss_m                                                                 181.310639
net_m                                                                   -68.56941
mean_abs_grade_pct                                                       8.719591
max_sustained_grade_250m_pct                                             10.88042
gmaps                           https://www.google.com/maps/dir/?api=1&origin=...
osm                             https://www.openstreetmap.org/?mlat=39.636328&...
fit                                                                          53.0
Name: 1, dtype: object> | 3.5 | 53 | 4.0 | 155 | 28% | +113/-181 | 8.7% | 164 km NW | [Google](https://www.google.com/maps/dir/?api=1&origin=39.638069,-78.703705&destination=39.642254,-78.672569&waypoints=39.635931,-78.694401%7C39.636328,-78.687284%7C39.640072,-78.681096&travelmode=driving) / [OSM](https://www.openstreetmap.org/?mlat=39.636328&mlon=-78.687284#map=13/39.636328/-78.687284) |
| 3 | US 211 (trunk) | VA, <bound method NDFrame.where of chain_idx                                                                    1779
road_key                                                                   US 211
highway                                                                     trunk
state                                                                          VA
s0                                                                       54.19237
s1                                                                     4554.19237
length_m                                                                   4500.0
score                                                                    0.480976
match_share                                                                   1.0
deg_per_km                                                             403.372287
radius_p50                                                             141.120832
turns_per_km_45                                                          3.555566
turns_per_km_15                                                          4.888903
frac_straight                                                             0.23978
frac_R_lt_50                                                             0.056172
straight_max_m                                                         109.962724
lon                             [-78.313855, -78.313747, -78.313639, -78.31353...
lat                             [38.662125, 38.662155, 38.662184, 38.662215, 3...
mid_lon                                                                -78.300086
mid_lat                                                                 38.663716
rank                                                                            3
dist_to_us211_ref_km                                                     0.605156
where                                                       6 km W of Sperryville
from_dc                                                                  113 km W
gain_m                                                                   0.075183
loss_m                                                                 273.189444
net_m                                                                 -273.114261
mean_abs_grade_pct                                                       6.253159
max_sustained_grade_250m_pct                                             7.531494
gmaps                           https://www.google.com/maps/dir/?api=1&origin=...
osm                             https://www.openstreetmap.org/?mlat=38.663716&...
fit                                                                          52.0
Name: 2, dtype: object> | 4.5 | 52 | 3.6 | 141 | 24% | +0/-273 | 6.3% | 113 km W | [Google](https://www.google.com/maps/dir/?api=1&origin=38.662125,-78.313855&destination=38.661762,-78.290064&waypoints=38.661579,-78.310866%7C38.66163,-78.304005%7C38.664346,-78.295606%7C38.668824,-78.290809&travelmode=driving) / [OSM](https://www.openstreetmap.org/?mlat=38.663716&mlon=-78.300086#map=13/38.663716/-78.300086) |
| 4 | Bonnie Branch Road (tertiary) | MD, <bound method NDFrame.where of chain_idx                                                                    2293
road_key                                                       Bonnie Branch Road
highway                                                                  tertiary
state                                                                          MD
s0                                                                      54.189787
s1                                                                    3054.189787
length_m                                                                   3000.0
score                                                                    0.481329
match_share                                                                   1.0
deg_per_km                                                             335.906384
radius_p50                                                             161.353437
turns_per_km_45                                                          2.999216
turns_per_km_15                                                          5.998431
frac_straight                                                            0.246242
frac_R_lt_50                                                             0.021561
straight_max_m                                                         109.973489
lon                             [-76.765951, -76.766058, -76.766166, -76.76627...
lat                             [39.24959, 39.249624, 39.249655, 39.249682, 39...
mid_lon                                                                -76.776364
mid_lat                                                                 39.241689
rank                                                                            4
dist_to_us211_ref_km                                                   146.071759
where                                                                at Ilchester
from_dc                                                                  43 km NE
gain_m                                                                  83.188285
loss_m                                                                   1.355945
net_m                                                                    81.83234
mean_abs_grade_pct                                                       2.959114
max_sustained_grade_250m_pct                                             5.013801
gmaps                           https://www.google.com/maps/dir/?api=1&origin=...
osm                             https://www.openstreetmap.org/?mlat=39.241689&...
fit                                                                          52.0
Name: 3, dtype: object> | 3.0 | 52 | 3.0 | 161 | 25% | +83/-1 | 3.0% | 43 km NE | [Google](https://www.google.com/maps/dir/?api=1&origin=39.24959,-76.765951&destination=39.231916,-76.785425&waypoints=39.246682,-76.772346%7C39.241689,-76.776364%7C39.236956,-76.781995&travelmode=driving) / [OSM](https://www.openstreetmap.org/?mlat=39.241689&mlon=-76.776364#map=13/39.241689/-76.776364) |
| 5 | CR 50/2 (tertiary) | WV, <bound method NDFrame.where of chain_idx                                                                    4074
road_key                                                                  CR 50/2
highway                                                                  tertiary
state                                                                          WV
s0                                                                    3554.065866
s1                                                                    6554.065866
length_m                                                                   3000.0
score                                                                    0.481702
match_share                                                                   1.0
deg_per_km                                                             324.303108
radius_p50                                                             145.746445
turns_per_km_45                                                          3.339716
turns_per_km_15                                                          4.675603
frac_straight                                                            0.320244
frac_R_lt_50                                                             0.031038
straight_max_m                                                         149.894403
lon                             [-78.846731, -78.846839, -78.846946, -78.84704...
lat                             [39.33479, 39.33476, 39.334726, 39.334687, 39....
mid_lon                                                                -78.859382
mid_lat                                                                 39.328544
rank                                                                            5
dist_to_us211_ref_km                                                    88.295259
where                                                            9 km W of Romney
from_dc                                                                  165 km W
gain_m                                                                  35.419405
loss_m                                                                  69.988137
net_m                                                                  -34.568732
mean_abs_grade_pct                                                       3.677206
max_sustained_grade_250m_pct                                            10.493055
gmaps                           https://www.google.com/maps/dir/?api=1&origin=...
osm                             https://www.openstreetmap.org/?mlat=39.328544&...
fit                                                                          52.0
Name: 4, dtype: object> | 3.0 | 52 | 3.3 | 146 | 32% | +35/-70 | 3.7% | 165 km W | [Google](https://www.google.com/maps/dir/?api=1&origin=39.33479,-78.846731&destination=39.326674,-78.873528&waypoints=39.329975,-78.852284%7C39.328544,-78.859382%7C39.326165,-78.865893&travelmode=driving) / [OSM](https://www.openstreetmap.org/?mlat=39.328544&mlon=-78.859382#map=13/39.328544/-78.859382) |
| 6 | Scenic Drive (unclassified) | VA, <bound method NDFrame.where of chain_idx                                                                    1992
road_key                                                             Scenic Drive
highway                                                              unclassified
state                                                                          VA
s0                                                                     552.261191
s1                                                                    4552.261191
length_m                                                                   4000.0
score                                                                    0.530333
match_share                                                                   1.0
deg_per_km                                                             293.603611
radius_p50                                                             149.400236
turns_per_km_45                                                           3.00221
turns_per_km_15                                                          5.003683
frac_straight                                                            0.245066
frac_R_lt_50                                                                  0.0
straight_max_m                                                          149.97302
lon                             [-77.371316, -77.371427, -77.371535, -77.37163...
lat                             [38.578189, 38.578175, 38.57815, 38.578116, 38...
mid_lon                                                                -77.389822
mid_lat                                                                 38.579239
rank                                                                            6
dist_to_us211_ref_km                                                    78.819814
where                                                        4 km SW of Montclair
from_dc                                                                  47 km SW
gain_m                                                                  76.908839
loss_m                                                                  39.752116
net_m                                                                   37.156723
mean_abs_grade_pct                                                       3.020111
max_sustained_grade_250m_pct                                             9.615512
gmaps                           https://www.google.com/maps/dir/?api=1&origin=...
osm                             https://www.openstreetmap.org/?mlat=38.579239&...
fit                                                                          47.0
Name: 5, dtype: object> | 4.0 | 47 | 3.0 | 149 | 25% | +77/-40 | 3.0% | 47 km SW | [Google](https://www.google.com/maps/dir/?api=1&origin=38.578189,-77.371316&destination=38.588432,-77.406745&waypoints=38.576613,-77.379475%7C38.579184,-77.389732%7C38.583415,-77.398525&travelmode=driving) / [OSM](https://www.openstreetmap.org/?mlat=38.579239&mlon=-77.389822#map=13/38.579239/-77.389822) |
| 7 | Town Creek Road Northeast (tertiary) | MD, <bound method NDFrame.where of chain_idx                                                                    3303
road_key                                                Town Creek Road Northeast
highway                                                                  tertiary
state                                                                          MD
s0                                                                      53.184619
s1                                                                    3053.184619
length_m                                                                   3000.0
score                                                                    0.541949
match_share                                                                   1.0
deg_per_km                                                              324.83394
radius_p50                                                             176.853693
turns_per_km_45                                                          3.001258
turns_per_km_15                                                          5.669044
frac_straight                                                            0.283265
frac_R_lt_50                                                             0.029339
straight_max_m                                                         170.004196
lon                             [-78.560575, -78.560555, -78.560528, -78.56049...
lat                             [39.696987, 39.696899, 39.696812, 39.696725, 3...
mid_lon                                                                -78.563529
mid_lat                                                                 39.684932
rank                                                                            7
dist_to_us211_ref_km                                                   115.230078
where                                                        2 km S of Flintstone
from_dc                                                                 158 km NW
gain_m                                                                  40.584728
loss_m                                                                  49.781983
net_m                                                                   -9.197254
mean_abs_grade_pct                                                       3.133035
max_sustained_grade_250m_pct                                             5.132738
gmaps                           https://www.google.com/maps/dir/?api=1&origin=...
osm                             https://www.openstreetmap.org/?mlat=39.684932&...
fit                                                                          46.0
Name: 6, dtype: object> | 3.0 | 46 | 3.0 | 177 | 28% | +41/-50 | 3.1% | 158 km NW | [Google](https://www.google.com/maps/dir/?api=1&origin=39.696987,-78.560575&destination=39.677436,-78.568671&waypoints=39.690844,-78.560548%7C39.684932,-78.563529%7C39.683881,-78.567417&travelmode=driving) / [OSM](https://www.openstreetmap.org/?mlat=39.684932&mlon=-78.563529#map=13/39.684932/-78.563529) |
| 8 | CR 3 (secondary) | WV, <bound method NDFrame.where of chain_idx                                                                    4063
road_key                                                                     CR 3
highway                                                                 secondary
state                                                                          WV
s0                                                                    6553.763838
s1                                                                   10053.763838
length_m                                                                   3500.0
score                                                                    0.577717
match_share                                                                   1.0
deg_per_km                                                             351.394477
radius_p50                                                             171.153057
turns_per_km_45                                                          2.575542
turns_per_km_15                                                          4.292569
frac_straight                                                            0.294554
frac_R_lt_50                                                             0.059568
straight_max_m                                                         139.984363
lon                             [-78.635191, -78.635098, -78.635007, -78.63491...
lat                             [39.452238, 39.452184, 39.452129, 39.452072, 3...
mid_lon                                                                -78.619369
mid_lat                                                                 39.447728
rank                                                                            8
dist_to_us211_ref_km                                                    91.090866
where                                                      9 km S of Green Spring
from_dc                                                                 150 km NW
gain_m                                                                 183.801516
loss_m                                                                  34.056687
net_m                                                                  149.744829
mean_abs_grade_pct                                                       6.473355
max_sustained_grade_250m_pct                                             8.475974
gmaps                           https://www.google.com/maps/dir/?api=1&origin=...
osm                             https://www.openstreetmap.org/?mlat=39.447728&...
fit                                                                          42.0
Name: 7, dtype: object> | 3.5 | 42 | 2.6 | 171 | 29% | +184/-34 | 6.5% | 150 km NW | [Google](https://www.google.com/maps/dir/?api=1&origin=39.452238,-78.635191&destination=39.445916,-78.61003&waypoints=39.449277,-78.626877%7C39.447721,-78.619483%7C39.450619,-78.612913&travelmode=driving) / [OSM](https://www.openstreetmap.org/?mlat=39.447728&mlon=-78.619369#map=13/39.447728/-78.619369) |
| 9 | Skyline Drive (secondary) | VA, <bound method NDFrame.where of chain_idx                                                                    1577
road_key                                                            Skyline Drive
highway                                                                 secondary
state                                                                          VA
s0                                                                      54.066312
s1                                                                    4554.066312
length_m                                                                   4500.0
score                                                                    0.596232
match_share                                                                 0.875
deg_per_km                                                             288.275254
radius_p50                                                             153.583224
turns_per_km_45                                                          2.664841
turns_per_km_15                                                          4.219331
frac_straight                                                            0.292997
frac_R_lt_50                                                                  0.0
straight_max_m                                                         319.973729
lon                             [-78.801407, -78.801294, -78.80118, -78.801067...
lat                             [38.078285, 38.078294, 38.078302, 38.078312, 3...
mid_lon                                                                -78.784881
mid_lat                                                                 38.089488
rank                                                                            9
dist_to_us211_ref_km                                                    76.531311
where                                                             7 km E of Dooms
from_dc                                                                 176 km SW
gain_m                                                                   9.304957
loss_m                                                                  97.960122
net_m                                                                  -88.655164
mean_abs_grade_pct                                                       2.445002
max_sustained_grade_250m_pct                                             5.178221
gmaps                           https://www.google.com/maps/dir/?api=1&origin=...
osm                             https://www.openstreetmap.org/?mlat=38.089488&...
fit                                                                          40.0
Name: 8, dtype: object> | 4.5 | 40 | 2.7 | 154 | 29% | +9/-98 | 2.4% | 176 km SW | [Google](https://www.google.com/maps/dir/?api=1&origin=38.078285,-78.801407&destination=38.106053,-78.781192&waypoints=38.08293,-78.793864%7C38.088989,-78.789212%7C38.092838,-78.782313%7C38.09983,-78.781627&travelmode=driving) / [OSM](https://www.openstreetmap.org/?mlat=38.089488&mlon=-78.784881#map=13/38.089488/-78.784881) |
| 10 | SR 675 (unclassified) | VA, <bound method NDFrame.where of chain_idx                                                                     425
road_key                                                                   SR 675
highway                                                              unclassified
state                                                                          VA
s0                                                                      53.862553
s1                                                                    3053.862553
length_m                                                                   3000.0
score                                                                    0.601557
match_share                                                                   0.8
deg_per_km                                                              363.95309
radius_p50                                                             130.152177
turns_per_km_45                                                          3.333555
turns_per_km_15                                                          5.667044
frac_straight                                                            0.336297
frac_R_lt_50                                                             0.035673
straight_max_m                                                         179.904714
lon                             [-78.689086, -78.688978, -78.688868, -78.68875...
lat                             [38.923415, 38.923385, 38.92336, 38.92334, 38....
mid_lon                                                                -78.691102
mid_lat                                                                 38.913345
rank                                                                           10
dist_to_us211_ref_km                                                    44.102562
where                                                          3 km S of Rockland
from_dc                                                                  143 km W
gain_m                                                                        0.0
loss_m                                                                 233.120993
net_m                                                                 -233.120993
mean_abs_grade_pct                                                        8.11649
max_sustained_grade_250m_pct                                             9.465487
gmaps                           https://www.google.com/maps/dir/?api=1&origin=...
osm                             https://www.openstreetmap.org/?mlat=38.913345&...
fit                                                                          40.0
Name: 9, dtype: object> | 3.0 | 40 | 3.3 | 130 | 34% | +0/-233 | 8.1% | 143 km W | [Google](https://www.google.com/maps/dir/?api=1&origin=38.923415,-78.689086&destination=38.902644,-78.688489&waypoints=38.919142,-78.689165%7C38.913345,-78.691102%7C38.906904,-78.691263&travelmode=driving) / [OSM](https://www.openstreetmap.org/?mlat=38.913345&mlon=-78.691102#map=13/38.913345/-78.691102) |
| 11 (suburban, check) | Lake Braddock Drive (tertiary) | VA, <bound method NDFrame.where of chain_idx                                                                    2147
road_key                                                      Lake Braddock Drive
highway                                                                  tertiary
state                                                                          VA
s0                                                                      53.861063
s1                                                                    3553.861063
length_m                                                                   3500.0
score                                                                    0.612281
match_share                                                                   1.0
deg_per_km                                                             296.317779
radius_p50                                                             154.324648
turns_per_km_45                                                          2.286038
turns_per_km_15                                                          2.857547
frac_straight                                                            0.313958
frac_R_lt_50                                                             0.005702
straight_max_m                                                         139.839512
lon                             [-77.265577, -77.265669, -77.265761, -77.26585...
lat                             [38.800266, 38.80032, 38.800375, 38.800429, 38...
mid_lon                                                                -77.274985
mid_lat                                                                 38.801748
rank                                                                           11
dist_to_us211_ref_km                                                    89.496614
where                                                  2 km SE of Kings Park West
from_dc                                                                  24 km SW
gain_m                                                                  38.009772
loss_m                                                                  39.381216
net_m                                                                   -1.371444
mean_abs_grade_pct                                                       2.284064
max_sustained_grade_250m_pct                                             3.020451
gmaps                           https://www.google.com/maps/dir/?api=1&origin=...
osm                             https://www.openstreetmap.org/?mlat=38.801748&...
fit                                                                          39.0
Name: 10, dtype: object> | 3.5 | 39 | 2.3 | 154 | 31% | +38/-39 | 2.3% | 24 km SW | [Google](https://www.google.com/maps/dir/?api=1&origin=38.800266,-77.265577&destination=38.802645,-77.267696&waypoints=38.805711,-77.269464%7C38.801792,-77.274885%7C38.805981,-77.273133&travelmode=driving) / [OSM](https://www.openstreetmap.org/?mlat=38.801748&mlon=-77.274985#map=13/38.801748/-77.274985) |
| 12 | CR 3/3 (tertiary) | WV, <bound method NDFrame.where of chain_idx                                                                    4066
road_key                                                                   CR 3/3
highway                                                                  tertiary
state                                                                          WV
s0                                                                      54.267676
s1                                                                    4554.267676
length_m                                                                   4500.0
score                                                                    0.621125
match_share                                                                  0.75
deg_per_km                                                             361.138857
radius_p50                                                             148.742663
turns_per_km_45                                                          3.559286
turns_per_km_15                                                          5.783839
frac_straight                                                            0.337925
frac_R_lt_50                                                             0.043722
straight_max_m                                                         140.044693
lon                             [-78.553069, -78.553048, -78.553028, -78.55300...
lat                             [39.483776, 39.483688, 39.483599, 39.48351, 39...
mid_lon                                                                -78.548746
mid_lat                                                                 39.465633
rank                                                                           12
dist_to_us211_ref_km                                                    91.301955
where                                                     9 km SE of Green Spring
from_dc                                                                 145 km NW
gain_m                                                                  55.187222
loss_m                                                                 199.732902
net_m                                                                 -144.545681
mean_abs_grade_pct                                                       5.827416
max_sustained_grade_250m_pct                                            10.759435
gmaps                           https://www.google.com/maps/dir/?api=1&origin=...
osm                             https://www.openstreetmap.org/?mlat=39.465633&...
fit                                                                          38.0
Name: 11, dtype: object> | 4.5 | 38 | 3.6 | 149 | 34% | +55/-200 | 5.8% | 145 km NW | [Google](https://www.google.com/maps/dir/?api=1&origin=39.483776,-78.553069&destination=39.45043,-78.541109&waypoints=39.476334,-78.55152%7C39.469009,-78.549093%7C39.462684,-78.546852%7C39.455873,-78.543444&travelmode=driving) / [OSM](https://www.openstreetmap.org/?mlat=39.465633&mlon=-78.548746#map=13/39.465633/-78.548746) |
| 13 (suburban, check) | Park Central Road (unclassified) | MD, <bound method NDFrame.where of chain_idx                                                                    2660
road_key                                                        Park Central Road
highway                                                              unclassified
state                                                                          MD
s0                                                                    1554.134943
s1                                                                    4554.134943
length_m                                                                   3000.0
score                                                                     0.62279
match_share                                                                   1.0
deg_per_km                                                             294.832921
radius_p50                                                             153.560072
turns_per_km_45                                                          2.999464
turns_per_km_15                                                          4.332559
frac_straight                                                            0.239722
frac_R_lt_50                                                                  0.0
straight_max_m                                                         239.856687
lon                             [-76.895712, -76.895827, -76.895942, -76.89605...
lat                             [38.994876, 38.994881, 38.994882, 38.994881, 3...
mid_lon                                                                -76.895466
mid_lat                                                                 38.983105
rank                                                                           13
dist_to_us211_ref_km                                                   126.096927
where                                                   2 km SE of Berwyn Heights
from_dc                                                                  15 km NE
gain_m                                                                  57.440478
loss_m                                                                   52.10457
net_m                                                                    5.335908
mean_abs_grade_pct                                                       3.814984
max_sustained_grade_250m_pct                                             7.652736
gmaps                           https://www.google.com/maps/dir/?api=1&origin=...
osm                             https://www.openstreetmap.org/?mlat=38.983105&...
fit                                                                          38.0
Name: 12, dtype: object> | 3.0 | 38 | 3.0 | 154 | 24% | +57/-52 | 3.8% | 15 km NE | [Google](https://www.google.com/maps/dir/?api=1&origin=38.994876,-76.895712&destination=38.972787,-76.90266&waypoints=38.989229,-76.896886%7C38.983171,-76.895387%7C38.977094,-76.897388&travelmode=driving) / [OSM](https://www.openstreetmap.org/?mlat=38.983105&mlon=-76.895466#map=13/38.983105/-76.895466) |
| 14 | SR 638 (tertiary) | VA, <bound method NDFrame.where of chain_idx                                                                     735
road_key                                                                   SR 638
highway                                                                  tertiary
state                                                                          VA
s0                                                                   10554.226982
s1                                                                   17054.226982
length_m                                                                   6500.0
score                                                                    0.632394
match_share                                                                  0.75
deg_per_km                                                             352.512272
radius_p50                                                             156.559644
turns_per_km_45                                                          2.618667
turns_per_km_15                                                          5.391374
frac_straight                                                            0.343225
frac_R_lt_50                                                             0.035251
straight_max_m                                                         199.962352
lon                             [-78.071613, -78.071504, -78.071395, -78.07128...
lat                             [38.976124, 38.976095, 38.976065, 38.976032, 3...
mid_lon                                                                -78.050625
mid_lat                                                                 38.971937
rank                                                                           14
dist_to_us211_ref_km                                                    39.959315
where                                                  2 km E of Shenandoah Farms
from_dc                                                                   88 km W
gain_m                                                                 391.669472
loss_m                                                                  35.413832
net_m                                                                  356.255639
mean_abs_grade_pct                                                       6.700181
max_sustained_grade_250m_pct                                             9.874413
gmaps                           https://www.google.com/maps/dir/?api=1&origin=...
osm                             https://www.openstreetmap.org/?mlat=38.971937&...
fit                                                                          37.0
Name: 13, dtype: object> | 6.5 | 37 | 2.6 | 157 | 34% | +392/-35 | 6.7% | 88 km W | [Google](https://www.google.com/maps/dir/?api=1&origin=38.976124,-78.071613&destination=38.959425,-78.030323&waypoints=38.974306,-78.061705%7C38.977805,-78.052685%7C38.974629,-78.048715%7C38.96879,-78.048953%7C38.963289,-78.042596%7C38.956906,-78.038065&travelmode=driving) / [OSM](https://www.openstreetmap.org/?mlat=38.971937&mlon=-78.050625#map=13/38.971937/-78.050625) |
| 15 | Shanghai Road (tertiary) | WV, <bound method NDFrame.where of chain_idx                                                                    4135
road_key                                                            Shanghai Road
highway                                                                  tertiary
state                                                                          WV
s0                                                                    1047.548284
s1                                                                    4047.548284
length_m                                                                   3000.0
score                                                                    0.646001
match_share                                                                   0.8
deg_per_km                                                             354.232817
radius_p50                                                             178.691012
turns_per_km_45                                                          2.334529
turns_per_km_15                                                          4.669059
frac_straight                                                            0.310273
frac_R_lt_50                                                              0.03575
straight_max_m                                                          140.07947
lon                             [-78.206053, -78.206115, -78.206175, -78.20623...
lat                             [39.439848, 39.439771, 39.439695, 39.439618, 3...
mid_lon                                                                -78.216981
mid_lat                                                                 39.438667
rank                                                                           15
dist_to_us211_ref_km                                                    85.849758
where                                                  10 km NE of Reynolds Store
from_dc                                                                 118 km NW
gain_m                                                                  38.929282
loss_m                                                                 175.713567
net_m                                                                 -136.784285
mean_abs_grade_pct                                                        7.48442
max_sustained_grade_250m_pct                                            10.840764
gmaps                           https://www.google.com/maps/dir/?api=1&origin=...
osm                             https://www.openstreetmap.org/?mlat=39.438667&...
fit                                                                          35.0
Name: 14, dtype: object> | 3.0 | 35 | 2.3 | 179 | 31% | +39/-176 | 7.5% | 118 km NW | [Google](https://www.google.com/maps/dir/?api=1&origin=39.439848,-78.206053&destination=39.442126,-78.231275&waypoints=39.440239,-78.209021%7C39.438667,-78.216981%7C39.442213,-78.223716&travelmode=driving) / [OSM](https://www.openstreetmap.org/?mlat=39.438667&mlon=-78.216981#map=13/39.438667/-78.216981) |
| 16 | CR 18 (tertiary) | WV, <bound method NDFrame.where of chain_idx                                                                    1515
road_key                                                                    CR 18
highway                                                                  tertiary
state                                                                          WV
s0                                                                    8554.243103
s1                                                                   17054.243103
length_m                                                                   8500.0
score                                                                    0.651695
match_share                                                                0.8125
deg_per_km                                                             522.094574
radius_p50                                                             112.922011
turns_per_km_45                                                          5.190711
turns_per_km_15                                                          7.078242
frac_straight                                                            0.231664
frac_R_lt_50                                                             0.115716
straight_max_m                                                         159.978626
lon                             [-78.388644, -78.388731, -78.388819, -78.38890...
lat                             [39.55873, 39.55867, 39.558611, 39.558553, 39....
mid_lon                                                                -78.403459
mid_lat                                                                  39.53153
rank                                                                           16
dist_to_us211_ref_km                                                    96.338309
where                                                           5 km E of Paw Paw
from_dc                                                                 137 km NW
gain_m                                                                  93.551686
loss_m                                                                 378.949262
net_m                                                                 -285.397575
mean_abs_grade_pct                                                       5.636824
max_sustained_grade_250m_pct                                            11.469077
gmaps                           https://www.google.com/maps/dir/?api=1&origin=...
osm                             https://www.openstreetmap.org/?mlat=39.53153&m...
fit                                                                          35.0
Name: 15, dtype: object> | 8.5 | 35 | 5.2 | 113 | 23% | +94/-379 | 5.6% | 137 km NW | [Google](https://www.google.com/maps/dir/?api=1&origin=39.55873,-78.388644&destination=39.521166,-78.437187&waypoints=39.552893,-78.396324%7C39.546734,-78.401626%7C39.540205,-78.406152%7C39.534954,-78.403128%7C39.528834,-78.406506%7C39.527941,-78.414438%7C39.527411,-78.420885%7C39.524315,-78.430089&travelmode=driving) / [OSM](https://www.openstreetmap.org/?mlat=39.53153&mlon=-78.403459#map=13/39.53153/-78.403459) |
| 17 | CR 10/1 (tertiary) | WV, <bound method NDFrame.where of chain_idx                                                                    3998
road_key                                                                  CR 10/1
highway                                                                  tertiary
state                                                                          WV
s0                                                                      51.255384
s1                                                                    3051.255384
length_m                                                                   3000.0
score                                                                     0.67566
match_share                                                                   0.6
deg_per_km                                                             503.405015
radius_p50                                                             104.673612
turns_per_km_45                                                          5.668886
turns_per_km_15                                                          6.669278
frac_straight                                                            0.329422
frac_R_lt_50                                                             0.097918
straight_max_m                                                         169.887042
lon                             [-78.751472, -78.751569, -78.751672, -78.75177...
lat                             [39.287312, 39.287357, 39.287394, 39.287427, 3...
mid_lon                                                                 -78.74226
mid_lat                                                                 39.297229
rank                                                                           17
dist_to_us211_ref_km                                                     80.04564
where                                                            5 km S of Romney
from_dc                                                                  154 km W
gain_m                                                                  94.141969
loss_m                                                                    44.9805
net_m                                                                   49.161469
mean_abs_grade_pct                                                       4.789715
max_sustained_grade_250m_pct                                             7.188721
gmaps                           https://www.google.com/maps/dir/?api=1&origin=...
osm                             https://www.openstreetmap.org/?mlat=39.297229&...
fit                                                                          32.0
Name: 16, dtype: object> | 3.0 | 32 | 5.7 | 105 | 33% | +94/-45 | 4.8% | 154 km W | [Google](https://www.google.com/maps/dir/?api=1&origin=39.287312,-78.751472&destination=39.306567,-78.735505&waypoints=39.292309,-78.747332%7C39.297175,-78.74235%7C39.300896,-78.738967&travelmode=driving) / [OSM](https://www.openstreetmap.org/?mlat=39.297229&mlon=-78.74226#map=13/39.297229/-78.74226) |
| 18 (suburban, check) | Beach Drive (tertiary) | MD, <bound method NDFrame.where of chain_idx                                                                    2505
road_key                                                              Beach Drive
highway                                                                  tertiary
state                                                                          MD
s0                                                                      54.257368
s1                                                                    6054.257368
length_m                                                                   6000.0
score                                                                    0.677283
match_share                                                                   1.0
deg_per_km                                                             264.236591
radius_p50                                                              183.87945
turns_per_km_45                                                          2.498743
turns_per_km_15                                                          4.164572
frac_straight                                                            0.253184
frac_R_lt_50                                                                  0.0
straight_max_m                                                         120.026352
lon                             [-77.06451, -77.064623, -77.064737, -77.064851...
lat                             [39.012478, 39.012461, 39.012446, 39.012434, 3...
mid_lon                                                                -77.090113
mid_lat                                                                 39.011936
rank                                                                           18
dist_to_us211_ref_km                                                   111.069487
where                                                         at Chevy Chase View
from_dc                                                                   12 km N
gain_m                                                                  23.514427
loss_m                                                                  15.272986
net_m                                                                    8.241441
mean_abs_grade_pct                                                       0.649954
max_sustained_grade_250m_pct                                             1.338315
gmaps                           https://www.google.com/maps/dir/?api=1&origin=...
osm                             https://www.openstreetmap.org/?mlat=39.011936&...
fit                                                                          32.0
Name: 17, dtype: object> | 6.0 | 32 | 2.5 | 184 | 25% | +24/-15 | 0.6% | 12 km N | [Google](https://www.google.com/maps/dir/?api=1&origin=39.012478,-77.06451&destination=39.027438,-77.090184&waypoints=39.00813,-77.069291%7C39.009301,-77.077896%7C39.009629,-77.086328%7C39.014934,-77.09221%7C39.020228,-77.098504%7C39.025463,-77.099278&travelmode=driving) / [OSM](https://www.openstreetmap.org/?mlat=39.011936&mlon=-77.090113#map=13/39.011936/-77.090113) |
| 19 | US 211 (trunk) | VA, <bound method NDFrame.where of chain_idx                                                                    1778
road_key                                                                   US 211
highway                                                                     trunk
state                                                                          VA
s0                                                                      54.234782
s1                                                                    4554.234782
length_m                                                                   4500.0
score                                                                     0.68387
match_share                                                                 0.875
deg_per_km                                                              297.30798
radius_p50                                                             170.990872
turns_per_km_45                                                          2.223539
turns_per_km_15                                                          2.668247
frac_straight                                                             0.33339
frac_R_lt_50                                                                  0.0
straight_max_m                                                         239.945078
lon                             [-78.63836, -78.63825, -78.638141, -78.638032,...
lat                             [38.642455, 38.642427, 38.6424, 38.642372, 38....
mid_lon                                                                -78.620367
mid_lat                                                                 38.641693
rank                                                                           19
dist_to_us211_ref_km                                                    28.455061
where                                                        4 km E of New Market
from_dc                                                                  140 km W
gain_m                                                                 219.496921
loss_m                                                                  85.834408
net_m                                                                  133.662513
mean_abs_grade_pct                                                       6.987192
max_sustained_grade_250m_pct                                             8.195224
gmaps                           https://www.google.com/maps/dir/?api=1&origin=...
osm                             https://www.openstreetmap.org/?mlat=38.641693&...
fit                                                                          32.0
Name: 18, dtype: object> | 4.5 | 32 | 2.2 | 171 | 33% | +219/-86 | 7.0% | 140 km W | [Google](https://www.google.com/maps/dir/?api=1&origin=38.642455,-78.63836&destination=38.639611,-78.606616&waypoints=38.644418,-78.630689%7C38.644599,-78.623462%7C38.642429,-78.615405%7C38.643203,-78.608989&travelmode=driving) / [OSM](https://www.openstreetmap.org/?mlat=38.641693&mlon=-78.620367#map=13/38.641693/-78.620367) |
| 20 | Skyline Drive (secondary) | VA, <bound method NDFrame.where of chain_idx                                                                    1578
road_key                                                            Skyline Drive
highway                                                                 secondary
state                                                                          VA
s0                                                                   29054.246923
s1                                                                   32054.246923
length_m                                                                   3000.0
score                                                                    0.701029
match_share                                                                   1.0
deg_per_km                                                             232.763681
radius_p50                                                             172.448215
turns_per_km_45                                                          3.001818
turns_per_km_15                                                          4.002424
frac_straight                                                            0.386853
frac_R_lt_50                                                                  0.0
straight_max_m                                                         209.992599
lon                             [-78.250067, -78.250148, -78.250227, -78.25030...
lat                             [38.759694, 38.75963, 38.759565, 38.759498, 38...
mid_lon                                                                -78.262272
mid_lat                                                                 38.758475
rank                                                                           20
dist_to_us211_ref_km                                                     10.72631
where                                                      10 km NW of Washington
from_dc                                                                  107 km W
gain_m                                                                 154.369585
loss_m                                                                   0.195352
net_m                                                                  154.174234
mean_abs_grade_pct                                                       5.390333
max_sustained_grade_250m_pct                                             7.095418
gmaps                           https://www.google.com/maps/dir/?api=1&origin=...
osm                             https://www.openstreetmap.org/?mlat=38.758475&...
fit                                                                          30.0
Name: 19, dtype: object> | 3.0 | 30 | 3.0 | 172 | 39% | +154/-0 | 5.4% | 107 km W | [Google](https://www.google.com/maps/dir/?api=1&origin=38.759694,-78.250067&destination=38.760251,-78.275988&waypoints=38.75685,-78.25475%7C38.758475,-78.262272%7C38.756692,-78.26942&travelmode=driving) / [OSM](https://www.openstreetmap.org/?mlat=38.758475&mlon=-78.262272#map=13/38.758475/-78.262272) |
| 21 | Oliver Beltz Road Southeast (tertiary) | MD, <bound method NDFrame.where of chain_idx                                                                    3246
road_key                                              Oliver Beltz Road Southeast
highway                                                                  tertiary
state                                                                          MD
s0                                                                    4050.937208
s1                                                                    8550.937208
length_m                                                                   4500.0
score                                                                    0.720656
match_share                                                                  0.75
deg_per_km                                                             346.600649
radius_p50                                                              160.49536
turns_per_km_45                                                          2.669243
turns_per_km_15                                                          4.671175
frac_straight                                                            0.331028
frac_R_lt_50                                                             0.040782
straight_max_m                                                         319.881727
lon                             [-78.611498, -78.611398, -78.611298, -78.61119...
lat                             [39.638539, 39.638585, 39.63863, 39.638673, 39...
mid_lon                                                                -78.605174
mid_lat                                                                 39.628249
rank                                                                           21
dist_to_us211_ref_km                                                   109.931732
where                                                   9 km SE of Pleasant Grove
from_dc                                                                 158 km NW
gain_m                                                                  86.016681
loss_m                                                                 320.980292
net_m                                                                 -234.963612
mean_abs_grade_pct                                                       9.308416
max_sustained_grade_250m_pct                                            16.059461
gmaps                           https://www.google.com/maps/dir/?api=1&origin=...
osm                             https://www.openstreetmap.org/?mlat=39.628249&...
fit                                                                          28.0
Name: 20, dtype: object> | 4.5 | 28 | 2.7 | 160 | 33% | +86/-321 | 9.3% | 158 km NW | [Google](https://www.google.com/maps/dir/?api=1&origin=39.638539,-78.611498&destination=39.615752,-78.593101&waypoints=39.638542,-78.602895%7C39.631715,-78.604943%7C39.624971,-78.602211%7C39.619949,-78.600613&travelmode=driving) / [OSM](https://www.openstreetmap.org/?mlat=39.628249&mlon=-78.605174#map=13/39.628249/-78.605174) |
| 22 | SR 629 (tertiary) | VA, <bound method NDFrame.where of chain_idx                                                                     307
road_key                                                                   SR 629
highway                                                                  tertiary
state                                                                          VA
s0                                                                    5054.250508
s1                                                                    8554.250508
length_m                                                                   3500.0
score                                                                    0.727123
match_share                                                              0.833333
deg_per_km                                                             310.718965
radius_p50                                                              185.85655
turns_per_km_45                                                          2.856596
turns_per_km_15                                                          4.284894
frac_straight                                                            0.379739
frac_R_lt_50                                                             0.049518
straight_max_m                                                         259.960501
lon                             [-78.313998, -78.314114, -78.314229, -78.31434...
lat                             [39.128193, 39.128187, 39.128181, 39.128174, 3...
mid_lon                                                                -78.330392
mid_lat                                                                 39.131626
rank                                                                           22
dist_to_us211_ref_km                                                    51.746613
where                                                       7 km S of Shawneeland
from_dc                                                                  115 km W
gain_m                                                                 126.968489
loss_m                                                                  42.797102
net_m                                                                   84.171387
mean_abs_grade_pct                                                       5.018451
max_sustained_grade_250m_pct                                             9.507791
gmaps                           https://www.google.com/maps/dir/?api=1&origin=...
osm                             https://www.openstreetmap.org/?mlat=39.131626&...
fit                                                                          27.0
Name: 21, dtype: object> | 3.5 | 27 | 2.9 | 186 | 38% | +127/-43 | 5.0% | 115 km W | [Google](https://www.google.com/maps/dir/?api=1&origin=39.128193,-78.313998&destination=39.138358,-78.34524&waypoints=39.129677,-78.322028%7C39.131619,-78.330277%7C39.133968,-78.339357&travelmode=driving) / [OSM](https://www.openstreetmap.org/?mlat=39.131626&mlon=-78.330392#map=13/39.131626/-78.330392) |
| 23 | SR 600 (tertiary) | VA, <bound method NDFrame.where of chain_idx                                                                    1184
road_key                                                                   SR 600
highway                                                                  tertiary
state                                                                          VA
s0                                                                    2054.230826
s1                                                                    5554.230826
length_m                                                                   3500.0
score                                                                    0.731859
match_share                                                              0.666667
deg_per_km                                                             327.766301
radius_p50                                                             171.476261
turns_per_km_45                                                          2.857675
turns_per_km_15                                                           5.71535
frac_straight                                                            0.342559
frac_R_lt_50                                                             0.055068
straight_max_m                                                         239.894867
lon                             [-78.252788, -78.252704, -78.252615, -78.25252...
lat                             [39.295022, 39.295083, 39.29514, 39.295189, 39...
mid_lon                                                                 -78.25296
mid_lat                                                                 39.307231
rank                                                                           23
dist_to_us211_ref_km                                                    71.148106
where                                                      6 km E of Lake Holiday
from_dc                                                                 114 km NW
gain_m                                                                 110.199849
loss_m                                                                  58.794468
net_m                                                                   51.405381
mean_abs_grade_pct                                                       5.018948
max_sustained_grade_250m_pct                                             9.235675
gmaps                           https://www.google.com/maps/dir/?api=1&origin=...
osm                             https://www.openstreetmap.org/?mlat=39.307231&...
fit                                                                          27.0
Name: 22, dtype: object> | 3.5 | 27 | 2.9 | 171 | 34% | +110/-59 | 5.0% | 114 km NW | [Google](https://www.google.com/maps/dir/?api=1&origin=39.295022,-78.252788&destination=39.318129,-78.242195&waypoints=39.301075,-78.252242%7C39.307149,-78.253009%7C39.311782,-78.246371&travelmode=driving) / [OSM](https://www.openstreetmap.org/?mlat=39.307231&mlon=-78.25296#map=13/39.307231/-78.25296) |
| 24 | CR 55/20 (tertiary) | WV, <bound method NDFrame.where of chain_idx                                                                    4105
road_key                                                                 CR 55/20
highway                                                                  tertiary
state                                                                          WV
s0                                                                    8554.235436
s1                                                                   13054.235436
length_m                                                                   4500.0
score                                                                    0.751209
match_share                                                                  0.75
deg_per_km                                                             314.122011
radius_p50                                                             159.747012
turns_per_km_45                                                            3.1167
turns_per_km_15                                                          4.452428
frac_straight                                                            0.387116
frac_R_lt_50                                                             0.043425
straight_max_m                                                         409.920752
lon                             [-78.893856, -78.893748, -78.89364, -78.893532...
lat                             [39.088559, 39.08859, 39.088622, 39.088654, 39...
mid_lon                                                                -78.874462
mid_lat                                                                 39.087747
rank                                                                           24
dist_to_us211_ref_km                                                    68.740234
where                                                        9 km E of Moorefield
from_dc                                                                  160 km W
gain_m                                                                 192.897958
loss_m                                                                 101.325909
net_m                                                                    91.57205
mean_abs_grade_pct                                                       6.737652
max_sustained_grade_250m_pct                                            10.266216
gmaps                           https://www.google.com/maps/dir/?api=1&origin=...
osm                             https://www.openstreetmap.org/?mlat=39.087747&...
fit                                                                          25.0
Name: 23, dtype: object> | 4.5 | 25 | 3.1 | 160 | 39% | +193/-101 | 6.7% | 160 km W | [Google](https://www.google.com/maps/dir/?api=1&origin=39.088559,-78.893856&destination=39.097845,-78.856898&waypoints=39.08837,-78.885024%7C39.089913,-78.876779%7C39.087568,-78.869538%7C39.094409,-78.86465&travelmode=driving) / [OSM](https://www.openstreetmap.org/?mlat=39.087747&mlon=-78.874462#map=13/39.087747/-78.874462) |
| 25 | SR 602 (secondary) | VA, <bound method NDFrame.where of chain_idx                                                                    1109
road_key                                                                   SR 602
highway                                                                 secondary
state                                                                          VA
s0                                                                   17554.177803
s1                                                                   20554.177803
length_m                                                                   3000.0
score                                                                    0.760834
match_share                                                                   1.0
deg_per_km                                                             250.643495
radius_p50                                                             183.984535
turns_per_km_45                                                           2.00492
turns_per_km_15                                                            5.0123
frac_straight                                                            0.387306
frac_R_lt_50                                                             0.011186
straight_max_m                                                         269.893088
lon                             [-78.58473, -78.584687, -78.584643, -78.5846, ...
lat                             [38.50165, 38.501733, 38.501817, 38.5019, 38.5...
mid_lon                                                                 -78.58083
mid_lat                                                                 38.512855
rank                                                                           25
dist_to_us211_ref_km                                                    30.036287
where                                                       5 km NE of Shenandoah
from_dc                                                                  141 km W
gain_m                                                                  35.313196
loss_m                                                                 105.658563
net_m                                                                  -70.345367
mean_abs_grade_pct                                                       4.913323
max_sustained_grade_250m_pct                                            11.451838
gmaps                           https://www.google.com/maps/dir/?api=1&origin=...
osm                             https://www.openstreetmap.org/?mlat=38.512855&...
fit                                                                          24.0
Name: 24, dtype: object> | 3.0 | 24 | 2.0 | 184 | 39% | +35/-106 | 4.9% | 141 km W | [Google](https://www.google.com/maps/dir/?api=1&origin=38.50165,-78.58473&destination=38.524788,-78.585821&waypoints=38.507567,-78.583801%7C38.512781,-78.580895%7C38.51919,-78.581575&travelmode=driving) / [OSM](https://www.openstreetmap.org/?mlat=38.512855&mlon=-78.58083#map=13/38.512855/-78.58083) |
| 26 | US 211 (trunk) | VA, <bound method NDFrame.where of chain_idx                                                                    1775
road_key                                                                   US 211
highway                                                                     trunk
state                                                                          VA
s0                                                                      54.273683
s1                                                                    4554.273683
length_m                                                                   4500.0
score                                                                    0.805872
match_share                                                                  0.75
deg_per_km                                                             287.852578
radius_p50                                                             182.410799
turns_per_km_45                                                          2.000778
turns_per_km_15                                                          5.557718
frac_straight                                                            0.320175
frac_R_lt_50                                                             0.041858
straight_max_m                                                         150.074351
lon                             [-78.325121, -78.325232, -78.325344, -78.32545...
lat                             [38.661365, 38.661387, 38.661408, 38.661429, 3...
mid_lon                                                                -78.338008
mid_lat                                                                 38.656542
rank                                                                           26
dist_to_us211_ref_km                                                     3.982654
where                                                      10 km W of Sperryville
from_dc                                                                  116 km W
gain_m                                                                        0.0
loss_m                                                                 267.483343
net_m                                                                 -267.483343
mean_abs_grade_pct                                                       6.122547
max_sustained_grade_250m_pct                                             7.107935
gmaps                           https://www.google.com/maps/dir/?api=1&origin=...
osm                             https://www.openstreetmap.org/?mlat=38.656542&...
fit                                                                          19.0
Name: 25, dtype: object> | 4.5 | 19 | 2.0 | 182 | 32% | +0/-267 | 6.1% | 116 km W | [Google](https://www.google.com/maps/dir/?api=1&origin=38.661365,-78.325121&destination=38.657846,-78.359645&waypoints=38.662461,-78.330999%7C38.659089,-78.334044%7C38.655603,-78.342899%7C38.653298,-78.351918&travelmode=driving) / [OSM](https://www.openstreetmap.org/?mlat=38.656542&mlon=-78.338008#map=13/38.656542/-78.338008) |
| 27 | CR 8 (tertiary) | WV, <bound method NDFrame.where of chain_idx                                                                    3992
road_key                                                                     CR 8
highway                                                                  tertiary
state                                                                          WV
s0                                                                    9054.222308
s1                                                                   13054.222308
length_m                                                                   4000.0
score                                                                    0.810838
match_share                                                              0.571429
deg_per_km                                                             295.912709
radius_p50                                                             204.830248
turns_per_km_45                                                          2.000256
turns_per_km_15                                                          5.750736
frac_straight                                                            0.329687
frac_R_lt_50                                                             0.029522
straight_max_m                                                         209.971044
lon                             [-78.188657, -78.188618, -78.188574, -78.18852...
lat                             [39.564162, 39.564247, 39.56433, 39.564412, 39...
mid_lon                                                                -78.189983
mid_lat                                                                 39.578689
rank                                                                           27
dist_to_us211_ref_km                                                   101.472396
where                                                 6 km SE of Berkeley Springs
from_dc                                                                 124 km NW
gain_m                                                                  47.808611
loss_m                                                                 138.451604
net_m                                                                  -90.642993
mean_abs_grade_pct                                                       4.796787
max_sustained_grade_250m_pct                                            12.858067
gmaps                           https://www.google.com/maps/dir/?api=1&origin=...
osm                             https://www.openstreetmap.org/?mlat=39.578689&...
fit                                                                          19.0
Name: 26, dtype: object> | 4.0 | 19 | 2.0 | 205 | 33% | +48/-138 | 4.8% | 124 km NW | [Google](https://www.google.com/maps/dir/?api=1&origin=39.564162,-78.188657&destination=39.591442,-78.182793&waypoints=39.570377,-78.185648%7C39.576934,-78.186707%7C39.58053,-78.1928%7C39.585936,-78.187588&travelmode=driving) / [OSM](https://www.openstreetmap.org/?mlat=39.578689&mlon=-78.189983#map=13/39.578689/-78.189983) |
| 28 | Harpers Ferry Road (secondary) | MD, <bound method NDFrame.where of chain_idx                                                                    3157
road_key                                                       Harpers Ferry Road
highway                                                                 secondary
state                                                                          MD
s0                                                                   11053.883803
s1                                                                   14553.883803
length_m                                                                   3500.0
score                                                                    0.811248
match_share                                                              0.833333
deg_per_km                                                             266.892166
radius_p50                                                             177.311273
turns_per_km_45                                                          2.288582
turns_per_km_15                                                          5.721456
frac_straight                                                            0.366036
frac_R_lt_50                                                             0.023873
straight_max_m                                                         190.015619
lon                             [-77.720184, -77.720249, -77.720315, -77.72038...
lat                             [39.409909, 39.409983, 39.410057, 39.410131, 3...
mid_lon                                                                 -77.73761
mid_lat                                                                 39.416032
rank                                                                           28
dist_to_us211_ref_km                                                    96.023785
where                                                        5 km S of Sharpsburg
from_dc                                                                  83 km NW
gain_m                                                                  61.103524
loss_m                                                                  62.916775
net_m                                                                   -1.813251
mean_abs_grade_pct                                                       3.660517
max_sustained_grade_250m_pct                                             9.232831
gmaps                           https://www.google.com/maps/dir/?api=1&origin=...
osm                             https://www.openstreetmap.org/?mlat=39.416032&...
fit                                                                          19.0
Name: 27, dtype: object> | 3.5 | 19 | 2.3 | 177 | 37% | +61/-63 | 3.7% | 83 km NW | [Google](https://www.google.com/maps/dir/?api=1&origin=39.409909,-77.720184&destination=39.427149,-77.744456&waypoints=39.413536,-77.728623%7C39.416032,-77.73761%7C39.419992,-77.744244&travelmode=driving) / [OSM](https://www.openstreetmap.org/?mlat=39.416032&mlon=-77.73761#map=13/39.416032/-77.73761) |
| 29 | Riverside Drive (tertiary) | VA, <bound method NDFrame.where of chain_idx                                                                     122
road_key                                                          Riverside Drive
highway                                                                  tertiary
state                                                                          VA
s0                                                                      52.473633
s1                                                                    3052.473633
length_m                                                                   3000.0
score                                                                    0.815102
match_share                                                                   0.8
deg_per_km                                                             478.442245
radius_p50                                                             125.215623
turns_per_km_45                                                           4.33372
turns_per_km_15                                                          6.333899
frac_straight                                                            0.313313
frac_R_lt_50                                                             0.113087
straight_max_m                                                         200.235651
lon                             [-77.484567, -77.484466, -77.484372, -77.48429...
lat                             [37.529166, 37.529125, 37.529079, 37.529024, 3...
mid_lon                                                                -77.473987
mid_lat                                                                 37.523993
rank                                                                           29
dist_to_us211_ref_km                                                   144.704546
where                                                         4 km SW of Richmond
from_dc                                                                  158 km S
gain_m                                                                  37.560965
loss_m                                                                  59.554797
net_m                                                                  -21.993833
mean_abs_grade_pct                                                       3.369743
max_sustained_grade_250m_pct                                             6.670423
gmaps                           https://www.google.com/maps/dir/?api=1&origin=...
osm                             https://www.openstreetmap.org/?mlat=37.523993&...
fit                                                                          18.0
Name: 28, dtype: object> | 3.0 | 18 | 4.3 | 125 | 31% | +38/-60 | 3.4% | 158 km S | [Google](https://www.google.com/maps/dir/?api=1&origin=37.529166,-77.484567&destination=37.523587,-77.457525&waypoints=37.526118,-77.479926%7C37.523993,-77.473987%7C37.523411,-77.465911&travelmode=driving) / [OSM](https://www.openstreetmap.org/?mlat=37.523993&mlon=-77.473987#map=13/37.523993/-77.473987) |
| 30 | CR 8 (tertiary) | WV, <bound method NDFrame.where of chain_idx                                                                    3991
road_key                                                                     CR 8
highway                                                                  tertiary
state                                                                          WV
s0                                                                    1053.519716
s1                                                                    7553.519716
length_m                                                                   6500.0
score                                                                    0.830701
match_share                                                                  0.75
deg_per_km                                                             292.621176
radius_p50                                                             177.199669
turns_per_km_45                                                          3.082011
turns_per_km_15                                                          5.239419
frac_straight                                                            0.380303
frac_R_lt_50                                                             0.026661
straight_max_m                                                         369.864936
lon                             [-78.952804, -78.952805, -78.952812, -78.95282...
lat                             [39.444571, 39.444661, 39.444751, 39.44484, 39...
mid_lon                                                                -78.935416
mid_lat                                                                 39.464078
rank                                                                           30
dist_to_us211_ref_km                                                   104.453992
where                                                           2 km SE of Dawson
from_dc                                                                  176 km W
gain_m                                                                  357.27436
loss_m                                                                  31.331862
net_m                                                                  325.942498
mean_abs_grade_pct                                                       6.101381
max_sustained_grade_250m_pct                                            12.793901
gmaps                           https://www.google.com/maps/dir/?api=1&origin=...
osm                             https://www.openstreetmap.org/?mlat=39.464078&...
fit                                                                          17.0
Name: 29, dtype: object> | 6.5 | 17 | 3.1 | 177 | 38% | +357/-31 | 6.1% | 176 km W | [Google](https://www.google.com/maps/dir/?api=1&origin=39.444571,-78.952804&destination=39.468894,-78.907983&waypoints=39.451561,-78.952676%7C39.457733,-78.94631%7C39.460372,-78.937574%7C39.467144,-78.932096%7C39.467504,-78.925677%7C39.466245,-78.916534&travelmode=driving) / [OSM](https://www.openstreetmap.org/?mlat=39.464078&mlon=-78.935416#map=13/39.464078/-78.935416) |
| 31 | Aquia Drive (tertiary) | VA, <bound method NDFrame.where of chain_idx                                                                    2061
road_key                                                              Aquia Drive
highway                                                                  tertiary
state                                                                          VA
s0                                                                    1053.917613
s1                                                                    4053.917613
length_m                                                                   3000.0
score                                                                    0.855101
match_share                                                                   0.6
deg_per_km                                                              311.01428
radius_p50                                                             145.314212
turns_per_km_45                                                          3.004709
turns_per_km_15                                                          4.006279
frac_straight                                                            0.403943
frac_R_lt_50                                                             0.047588
straight_max_m                                                         560.238672
lon                             [-77.375419, -77.375506, -77.375607, -77.37571...
lat                             [38.465198, 38.465246, 38.465275, 38.465287, 3...
mid_lon                                                                -77.383561
mid_lat                                                                  38.47281
rank                                                                           31
dist_to_us211_ref_km                                                    81.597768
where                                                            at Aquia Harbour
from_dc                                                                  57 km SW
gain_m                                                                  29.922789
loss_m                                                                  38.838298
net_m                                                                    -8.91551
mean_abs_grade_pct                                                       2.389999
max_sustained_grade_250m_pct                                             5.375426
gmaps                           https://www.google.com/maps/dir/?api=1&origin=...
osm                             https://www.openstreetmap.org/?mlat=38.47281&m...
fit                                                                          14.0
Name: 30, dtype: object> | 3.0 | 14 | 3.0 | 145 | 40% | +30/-39 | 2.4% | 57 km SW | [Google](https://www.google.com/maps/dir/?api=1&origin=38.465198,-77.375419&destination=38.463715,-77.389764&waypoints=38.467601,-77.379156%7C38.47281,-77.383561%7C38.467671,-77.385152&travelmode=driving) / [OSM](https://www.openstreetmap.org/?mlat=38.47281&mlon=-77.383561#map=13/38.47281/-77.383561) |
| 32 | Skyline Drive (secondary) | VA, <bound method NDFrame.where of chain_idx                                                                    1577
road_key                                                            Skyline Drive
highway                                                                 secondary
state                                                                          VA
s0                                                                   14054.066312
s1                                                                   21554.066312
length_m                                                                   7500.0
score                                                                    0.859829
match_share                                                              0.642857
deg_per_km                                                              256.33583
radius_p50                                                             183.774155
turns_per_km_45                                                          2.266502
turns_per_km_15                                                          3.199768
frac_straight                                                            0.350545
frac_R_lt_50                                                                  0.0
straight_max_m                                                         359.968878
lon                             [-78.767091, -78.766978, -78.766864, -78.76675...
lat                             [38.176863, 38.176868, 38.176877, 38.176889, 3...
mid_lon                                                                -78.753789
mid_lat                                                                 38.202227
rank                                                                           32
dist_to_us211_ref_km                                                    64.846349
where                                                         7 km E of Harriston
from_dc                                                                 168 km SW
gain_m                                                                  172.95108
loss_m                                                                 122.810105
net_m                                                                   50.140975
mean_abs_grade_pct                                                       4.010068
max_sustained_grade_250m_pct                                             7.500798
gmaps                           https://www.google.com/maps/dir/?api=1&origin=...
osm                             https://www.openstreetmap.org/?mlat=38.202227&...
fit                                                                          14.0
Name: 31, dtype: object> | 7.5 | 14 | 2.3 | 184 | 35% | +173/-123 | 4.0% | 168 km SW | [Google](https://www.google.com/maps/dir/?api=1&origin=38.176863,-78.767091&destination=38.213929,-78.737787&waypoints=38.181146,-78.759462%7C38.188393,-78.756127%7C38.194915,-78.753242%7C38.202142,-78.753825%7C38.209163,-78.748349%7C38.207228,-78.742786%7C38.209916,-78.73436&travelmode=driving) / [OSM](https://www.openstreetmap.org/?mlat=38.202227&mlon=-78.753789#map=13/38.202227/-78.753789) |
| 33 | SR 641 (tertiary) | VA, <bound method NDFrame.where of chain_idx                                                                     758
road_key                                                                   SR 641
highway                                                                  tertiary
state                                                                          VA
s0                                                                    6053.468919
s1                                                                   12553.468919
length_m                                                                   6500.0
score                                                                    0.873785
match_share                                                              0.666667
deg_per_km                                                             360.938051
radius_p50                                                             131.665996
turns_per_km_45                                                          3.235824
turns_per_km_15                                                          4.930779
frac_straight                                                            0.400221
frac_R_lt_50                                                             0.060465
straight_max_m                                                         519.926334
lon                             [-78.385119, -78.385068, -78.385021, -78.38497...
lat                             [38.180687, 38.180606, 38.180524, 38.180442, 3...
mid_lon                                                                -78.356075
mid_lat                                                                 38.167651
rank                                                                           33
dist_to_us211_ref_km                                                    55.210101
where                                                    5 km E of Piney Mountain
from_dc                                                                 141 km SW
gain_m                                                                  99.826986
loss_m                                                                 115.851873
net_m                                                                  -16.024887
mean_abs_grade_pct                                                       3.376733
max_sustained_grade_250m_pct                                             6.290795
gmaps                           https://www.google.com/maps/dir/?api=1&origin=...
osm                             https://www.openstreetmap.org/?mlat=38.167651&...
fit                                                                          13.0
Name: 32, dtype: object> | 6.5 | 13 | 3.2 | 132 | 40% | +100/-116 | 3.4% | 141 km SW | [Google](https://www.google.com/maps/dir/?api=1&origin=38.180687,-78.385119&destination=38.163821,-78.33385&waypoints=38.179722,-78.376225%7C38.174009,-78.368591%7C38.169692,-78.360476%7C38.170171,-78.353886%7C38.172451,-78.344977%7C38.167562,-78.33902&travelmode=driving) / [OSM](https://www.openstreetmap.org/?mlat=38.167651&mlon=-78.356075#map=13/38.167651/-78.356075) |
| 34 | Bentley Road (tertiary) | MD, <bound method NDFrame.where of chain_idx                                                                    2388
road_key                                                             Bentley Road
highway                                                                  tertiary
state                                                                          MD
s0                                                                    1053.644928
s1                                                                    4053.644928
length_m                                                                   3000.0
score                                                                    0.880883
match_share                                                                   0.8
deg_per_km                                                             263.069766
radius_p50                                                             179.208923
turns_per_km_45                                                          2.002811
turns_per_km_15                                                          5.674632
frac_straight                                                            0.336744
frac_R_lt_50                                                             0.012141
straight_max_m                                                         209.866043
lon                             [-76.655249, -76.655315, -76.655387, -76.65546...
lat                             [39.681401, 39.681327, 39.681257, 39.68119, 39...
mid_lon                                                                -76.669765
mid_lat                                                                 39.675227
rank                                                                           34
dist_to_us211_ref_km                                                   179.624433
where                                                           4 km N of Parkton
from_dc                                                                   91 km N
gain_m                                                                  50.134073
loss_m                                                                  87.334776
net_m                                                                  -37.200703
mean_abs_grade_pct                                                       4.782177
max_sustained_grade_250m_pct                                             9.959109
gmaps                           https://www.google.com/maps/dir/?api=1&origin=...
osm                             https://www.openstreetmap.org/?mlat=39.675227&...
fit                                                                          12.0
Name: 33, dtype: object> | 3.0 | 12 | 2.0 | 179 | 34% | +50/-87 | 4.8% | 91 km N | [Google](https://www.google.com/maps/dir/?api=1&origin=39.681401,-76.655249&destination=39.677175,-76.682097&waypoints=39.678757,-76.662616%7C39.67527,-76.669663%7C39.672627,-76.676832&travelmode=driving) / [OSM](https://www.openstreetmap.org/?mlat=39.675227&mlon=-76.669765#map=13/39.675227/-76.669765) |
| 35 | Park Central Road (unclassified) | MD, <bound method NDFrame.where of chain_idx                                                                    2661
road_key                                                        Park Central Road
highway                                                              unclassified
state                                                                          MD
s0                                                                       53.44934
s1                                                                     5053.44934
length_m                                                                   5000.0
score                                                                    0.882068
match_share                                                              0.666667
deg_per_km                                                             239.718612
radius_p50                                                             210.746879
turns_per_km_45                                                          1.798065
turns_per_km_15                                                          4.195486
frac_straight                                                             0.30735
frac_R_lt_50                                                                  0.0
straight_max_m                                                         189.883572
lon                             [-77.482868, -77.482756, -77.482646, -77.48254...
lat                             [39.645484, 39.6455, 39.645526, 39.645562, 39....
mid_lon                                                                -77.459723
mid_lat                                                                 39.645053
rank                                                                           35
dist_to_us211_ref_km                                                   130.255784
where                                                         5 km NW of Thurmont
from_dc                                                                  89 km NW
gain_m                                                                  64.567718
loss_m                                                                 210.737549
net_m                                                                 -146.169831
mean_abs_grade_pct                                                       5.643239
max_sustained_grade_250m_pct                                            14.229073
gmaps                           https://www.google.com/maps/dir/?api=1&origin=...
osm                             https://www.openstreetmap.org/?mlat=39.645053&...
fit                                                                          12.0
Name: 34, dtype: object> | 5.0 | 12 | 1.8 | 211 | 31% | +65/-211 | 5.6% | 89 km NW | [Google](https://www.google.com/maps/dir/?api=1&origin=39.645484,-77.482868&destination=39.640049,-77.445966&waypoints=39.646481,-77.474335%7C39.642012,-77.468216%7C39.645053,-77.459723%7C39.645584,-77.45131%7C39.647319,-77.444236&travelmode=driving) / [OSM](https://www.openstreetmap.org/?mlat=39.645053&mlon=-77.459723#map=13/39.645053/-77.459723) |
| 36 | Skyline Drive (secondary) | VA, <bound method NDFrame.where of chain_idx                                                                    1577
road_key                                                            Skyline Drive
highway                                                                 secondary
state                                                                          VA
s0                                                                   79054.066312
s1                                                                   82554.066312
length_m                                                                   3500.0
score                                                                    0.884203
match_share                                                              0.666667
deg_per_km                                                             255.566949
radius_p50                                                              178.86861
turns_per_km_45                                                          2.000426
turns_per_km_15                                                          3.429303
frac_straight                                                            0.337079
frac_R_lt_50                                                                  0.0
straight_max_m                                                         209.979156
lon                             [-78.420451, -78.420337, -78.420223, -78.42011...
lat                             [38.533502, 38.533502, 38.533506, 38.533517, 3...
mid_lon                                                                -78.415029
mid_lat                                                                 38.546409
rank                                                                           36
dist_to_us211_ref_km                                                    16.793229
where                                                          8 km SE of Stanley
from_dc                                                                  126 km W
gain_m                                                                 137.422528
loss_m                                                                  11.283535
net_m                                                                  126.138993
mean_abs_grade_pct                                                       4.416024
max_sustained_grade_250m_pct                                             6.506901
gmaps                           https://www.google.com/maps/dir/?api=1&origin=...
osm                             https://www.openstreetmap.org/?mlat=38.546409&...
fit                                                                          12.0
Name: 35, dtype: object> | 3.5 | 12 | 2.0 | 179 | 34% | +137/-11 | 4.4% | 126 km W | [Google](https://www.google.com/maps/dir/?api=1&origin=38.533502,-78.420451&destination=38.544834,-78.400972&waypoints=38.539978,-78.416389%7C38.546409,-78.415029%7C38.54913,-78.406962&travelmode=driving) / [OSM](https://www.openstreetmap.org/?mlat=38.546409&mlon=-78.415029#map=13/38.546409/-78.415029) |
| 37 | Skyline Drive (secondary) | VA, <bound method NDFrame.where of chain_idx                                                                    1577
road_key                                                            Skyline Drive
highway                                                                 secondary
state                                                                          VA
s0                                                                   32554.066312
s1                                                                   42554.066312
length_m                                                                  10000.0
score                                                                    0.889493
match_share                                                              0.684211
deg_per_km                                                             243.956719
radius_p50                                                             171.842507
turns_per_km_45                                                          2.101736
turns_per_km_15                                                          3.703059
frac_straight                                                            0.385206
frac_R_lt_50                                                                  0.0
straight_max_m                                                          569.95963
lon                             [-78.663988, -78.664037, -78.664086, -78.66413...
lat                             [38.273978, 38.27406, 38.274141, 38.274223, 38...
mid_lon                                                                 -78.64378
mid_lat                                                                 38.292762
rank                                                                           37
dist_to_us211_ref_km                                                    51.109527
where                                                   12 km SE of McGaheysville
from_dc                                                                 155 km SW
gain_m                                                                  79.980348
loss_m                                                                 215.195312
net_m                                                                 -135.214964
mean_abs_grade_pct                                                       2.988819
max_sustained_grade_250m_pct                                             6.710475
gmaps                           https://www.google.com/maps/dir/?api=1&origin=...
osm                             https://www.openstreetmap.org/?mlat=38.292762&...
fit                                                                          11.0
Name: 36, dtype: object> | 10.0 | 11 | 2.1 | 172 | 39% | +80/-215 | 3.0% | 155 km SW | [Google](https://www.google.com/maps/dir/?api=1&origin=38.273978,-78.663988&destination=38.311632,-78.617951&waypoints=38.28129,-78.661908%7C38.289505,-78.658203%7C38.296002,-78.65133%7C38.295079,-78.648963%7C38.289493,-78.640303%7C38.287162,-78.628403%7C38.294138,-78.625205%7C38.303837,-78.62285&travelmode=driving) / [OSM](https://www.openstreetmap.org/?mlat=38.292762&mlon=-78.64378#map=13/38.292762/-78.64378) |
| 38 | CR 38/3 (tertiary) | WV, <bound method NDFrame.where of chain_idx                                                                    4134
road_key                                                                  CR 38/3
highway                                                                  tertiary
state                                                                          WV
s0                                                                     554.246064
s1                                                                    4554.246064
length_m                                                                   4000.0
score                                                                    0.897315
match_share                                                              0.714286
deg_per_km                                                             232.297221
radius_p50                                                             176.205817
turns_per_km_45                                                          2.500984
turns_per_km_15                                                          4.251674
frac_straight                                                            0.447639
frac_R_lt_50                                                             0.002355
straight_max_m                                                         300.017638
lon                             [-78.20681, -78.206768, -78.206726, -78.206684...
lat                             [39.59468, 39.594764, 39.594848, 39.594932, 39...
mid_lon                                                                -78.220039
mid_lat                                                                 39.605456
rank                                                                           38
dist_to_us211_ref_km                                                   104.230233
where                                                  2 km S of Berkeley Springs
from_dc                                                                 128 km NW
gain_m                                                                   96.54681
loss_m                                                                 113.089015
net_m                                                                  -16.542205
mean_abs_grade_pct                                                       5.405826
max_sustained_grade_250m_pct                                             9.668461
gmaps                           https://www.google.com/maps/dir/?api=1&origin=...
osm                             https://www.openstreetmap.org/?mlat=39.605456&...
fit                                                                          10.0
Name: 37, dtype: object> | 4.0 | 10 | 2.5 | 176 | 45% | +97/-113 | 5.4% | 128 km NW | [Google](https://www.google.com/maps/dir/?api=1&origin=39.59468,-78.20681&destination=39.620385,-78.228092&waypoints=39.599505,-78.209837%7C39.603954,-78.216269%7C39.608118,-78.222081%7C39.6143,-78.22485&travelmode=driving) / [OSM](https://www.openstreetmap.org/?mlat=39.605456&mlon=-78.220039#map=13/39.605456/-78.220039) |
| 39 | SR 625 (tertiary) | VA, <bound method NDFrame.where of chain_idx                                                                     352
road_key                                                                   SR 625
highway                                                                  tertiary
state                                                                          VA
s0                                                                   12554.217298
s1                                                                   17054.217298
length_m                                                                   4500.0
score                                                                    0.930647
match_share                                                                 0.625
deg_per_km                                                             243.792809
radius_p50                                                             183.963394
turns_per_km_45                                                          2.003025
turns_per_km_15                                                          4.896283
frac_straight                                                            0.391435
frac_R_lt_50                                                             0.002102
straight_max_m                                                         349.919046
lon                             [-77.167117, -77.167189, -77.167258, -77.16732...
lat                             [38.067224, 38.067293, 38.067365, 38.067438, 3...
mid_lon                                                                -77.163744
mid_lat                                                                 38.083797
rank                                                                           39
dist_to_us211_ref_km                                                   117.027421
where                                                       10 km S of Port Royal
from_dc                                                                   92 km S
gain_m                                                                  32.426666
loss_m                                                                  27.144666
net_m                                                                    5.281999
mean_abs_grade_pct                                                       1.353804
max_sustained_grade_250m_pct                                             2.500544
gmaps                           https://www.google.com/maps/dir/?api=1&origin=...
osm                             https://www.openstreetmap.org/?mlat=38.083797&...
fit                                                                           7.0
Name: 38, dtype: object> | 4.5 | 7 | 2.0 | 184 | 39% | +32/-27 | 1.4% | 92 km S | [Google](https://www.google.com/maps/dir/?api=1&origin=38.067224,-77.167117&destination=38.089849,-77.142818&waypoints=38.074501,-77.169819%7C38.081203,-77.16695%7C38.087078,-77.160761%7C38.087188,-77.151597&travelmode=driving) / [OSM](https://www.openstreetmap.org/?mlat=38.083797&mlon=-77.163744#map=13/38.083797/-77.163744) |
| 40 | North Franklintown Road (tertiary) | MD, <bound method NDFrame.where of chain_idx                                                                    2625
road_key                                                  North Franklintown Road
highway                                                                  tertiary
state                                                                          MD
s0                                                                    1554.130159
s1                                                                    4554.130159
length_m                                                                   3000.0
score                                                                    0.932656
match_share                                                                   0.8
deg_per_km                                                             267.794153
radius_p50                                                             180.316817
turns_per_km_45                                                          2.001402
turns_per_km_15                                                          4.336372
frac_straight                                                            0.363159
frac_R_lt_50                                                             0.012516
straight_max_m                                                         269.762346
lon                             [-76.68074, -76.68085, -76.680962, -76.681076,...
lat                             [39.305898, 39.305925, 39.305946, 39.305963, 3...
mid_lon                                                                -76.694935
mid_lat                                                                 39.301794
rank                                                                           40
dist_to_us211_ref_km                                                   155.347221
where                                                          4 km E of Woodlawn
from_dc                                                                  53 km NE
gain_m                                                                  51.112993
loss_m                                                                   11.73811
net_m                                                                   39.374883
mean_abs_grade_pct                                                       2.182886
max_sustained_grade_250m_pct                                             3.675109
gmaps                           https://www.google.com/maps/dir/?api=1&origin=...
osm                             https://www.openstreetmap.org/?mlat=39.301794&...
fit                                                                           7.0
Name: 39, dtype: object> | 3.0 | 7 | 2.0 | 180 | 36% | +51/-12 | 2.2% | 53 km NE | [Google](https://www.google.com/maps/dir/?api=1&origin=39.305898,-76.68074&destination=39.303324,-76.707028&waypoints=39.304407,-76.688858%7C39.30184,-76.694836%7C39.300651,-76.703132&travelmode=driving) / [OSM](https://www.openstreetmap.org/?mlat=39.301794&mlon=-76.694935#map=13/39.301794/-76.694935) |
