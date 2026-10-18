import sys
sys.path.insert(0, "src")
import numpy as np
from switchback.geometry import Params, analyze, calibrate_radius


def test_radius_recovered_within_10pct_at_default():
    cal = calibrate_radius(Params())
    for R in (50, 100, 200, 500):
        assert abs(cal[R] - 1) < 0.1, (R, cal[R])


def test_straight_line_has_no_corners():
    x = np.linspace(0, 3000, 300)
    lon0, lat0 = -78.0, 38.0
    ser, corners, straights, wins, road = analyze(lon0 + x / 87000, np.full_like(x, lat0), Params())
    assert len(corners) == 0 and road["deg_per_km"] < 1


def test_known_number_of_90deg_turns():
    # 4 alternating 90 degree arcs of R=60 m separated by 300 m straights
    pts, ang, x, y = [], 0.0, 0.0, 0.0
    for sign in (1, -1, 1, -1):
        for _ in range(30):
            x += 10 * np.cos(ang); y += 10 * np.sin(ang); pts.append((x, y))
        n = 38
        for _ in range(n):
            ang += sign * (np.pi / 2) / n
            x += (np.pi / 2 * 60 / n) * np.cos(ang); y += (np.pi / 2 * 60 / n) * np.sin(ang); pts.append((x, y))
    for _ in range(30):
        x += 10 * np.cos(ang); y += 10 * np.sin(ang); pts.append((x, y))
    a = np.array(pts)
    lon, lat = -78 + a[:, 0] / 87000, 38 + a[:, 1] / 111000
    _, corners, _, _, _ = analyze(lon, lat, Params())
    big = corners[(~corners.partial) & (corners.angle_deg >= 60)]
    assert len(big) == 4, corners
