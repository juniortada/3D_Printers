import argparse
import json

import numpy as np

import delta_model as dm

PILLAR_ANGLES = np.radians([210.0, 270.0, 330.0, 30.0, 90.0, 150.0])
PILLAR_NAMES = ["A", "far_C", "B", "far_A", "C", "far_B"]
PILLAR_RADIUS = 65.0
RIDGE_RADIUS = 4.5
CENTER_WIDTH_INDEX = [0, 2, 1, 0, 2, 1]
SIGMA_DISTANCE = 0.25
SIGMA_FIRST_LAYER = 0.1


def measurement_segments():
    u = np.column_stack([np.cos(PILLAR_ANGLES), np.sin(PILLAR_ANGLES)])
    toward_next = np.roll(u, -2, axis=0)
    center = [(RIDGE_RADIUS * u[k], (PILLAR_RADIUS + RIDGE_RADIUS) * u[k]) for k in range(6)]
    outer = [
        (PILLAR_RADIUS * u[k] + RIDGE_RADIUS * toward_next[k], PILLAR_RADIUS * u[k] + (PILLAR_RADIUS + RIDGE_RADIUS) * toward_next[k])
        for k in range(6)
    ]
    labels = [f"center->{n}" for n in PILLAR_NAMES] + [f"{PILLAR_NAMES[k]}->{PILLAR_NAMES[(k + 1) % 6]}" for k in range(6)]
    return center + outer, labels


def measured_distances(data):
    center_widths = np.asarray(data["center_pillar_widths"])[CENTER_WIDTH_INDEX]
    center = np.asarray(data["center_dists"]) - center_widths
    outer = np.asarray(data["outer_dists"]) - np.asarray(data["outer_pillar_widths"])
    return np.concatenate([center, outer])


class Fit:
    def __init__(self, data, fit_rods=False, keep=None):
        self.fw = dm.from_marlin(data["printed_with"]["M665"], data["printed_with"]["M666"])
        segments, self.labels = measurement_segments()
        distances = measured_distances(data)
        keep = np.ones(len(segments), bool) if keep is None else keep
        self.travels = [
            (dm.travel_from_home([*a, 0.0], self.fw), dm.travel_from_home([*b, 0.0], self.fw))
            for (a, b), k in zip(segments, keep)
            if k
        ]
        self.distances = distances[keep]
        pads = data.get("first_layer", [])
        self.pad_travels = [dm.travel_from_home([p["x"], p["y"], 0.0], self.fw) for p in pads]
        self.pad_errors = np.array([p["nozzle_error_mm"] for p in pads])
        self.fit_rods = fit_rods
        self.endstops = dm.endstop_heights(self.fw)

    def machine(self, v):
        rod = np.asarray(self.fw["rod"], float) + (v[6:9] if self.fit_rods else 0.0)
        ang = (self.fw["ang"][0] + v[0], self.fw["ang"][1] + v[1], self.fw["ang"][2])
        return dict(L=self.fw["L"], R=self.fw["R"] + v[2], ang=ang, rod=tuple(rod), E=self.endstops + v[3:6])

    def residuals(self, v):
        m = self.machine(v)
        d = np.array([np.linalg.norm(dm.nozzle_at(a, m) - dm.nozzle_at(b, m)) for a, b in self.travels])
        z = np.array([dm.nozzle_at(t, m)[2] for t in self.pad_travels])
        return np.concatenate([(d - self.distances) / SIGMA_DISTANCE, (z - self.pad_errors) / SIGMA_FIRST_LAYER])

    def solve(self):
        n = 9 if self.fit_rods else 6
        v = np.zeros(n)
        for _ in range(40):
            r = self.residuals(v)
            J = np.empty((len(r), n))
            for i in range(n):
                dv = v.copy()
                dv[i] += 1e-5
                J[:, i] = (self.residuals(dv) - r) / 1e-5
            step = np.linalg.lstsq(J, -r, rcond=None)[0]
            v += step
            if np.abs(step).max() < 1e-8:
                break
        sigma = np.sqrt(np.diag(np.linalg.pinv(J.T @ J)))
        return v, sigma, self.residuals(v)[: len(self.distances)] * SIGMA_DISTANCE


def main():
    parser = argparse.ArgumentParser(description="Tower angle and radius fit from the Klipper delta calibration object")
    parser.add_argument("measurements")
    parser.add_argument("--rods", action="store_true", help="also fit the per-tower rod trims (A B C)")
    parser.add_argument("--leave-one-out", action="store_true")
    args = parser.parse_args()
    data = json.load(open(args.measurements))

    fit = Fit(data, fit_rods=args.rods)
    v, sigma, residual = fit.solve()
    names = ["angle X", "angle Y", "radius", "endstop X", "endstop Y", "endstop Z", "rod A", "rod B", "rod C"]
    for name, value, s in zip(names, v, sigma):
        print(f"{name:10s} {value:+.3f} +- {s:.3f}")
    print(f"distance residual rms {np.sqrt((residual ** 2).mean()):.3f} mm")
    for label, r in zip(fit.labels, residual):
        print(f"  {label:14s} {r:+.2f}")
    print(dm.marlin_gcode(dm.to_marlin(fit.machine(v))))

    if args.leave_one_out:
        for k, label in enumerate(fit.labels):
            keep = np.ones(len(fit.labels), bool)
            keep[k] = False
            w, _, _ = Fit(data, fit_rods=args.rods, keep=keep).solve()
            print(f"without {label:14s} angle X {w[0]:+.2f}  angle Y {w[1]:+.2f}  radius {w[2]:+.2f}")


if __name__ == "__main__":
    main()
