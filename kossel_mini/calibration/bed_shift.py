import argparse
import json
import re

import numpy as np

import delta_model as dm

PROBE_POINTS = np.array([(0, 0), (-69.28, -40), (67.55, -39), (0, 80), (60.62, 35), (-69.28, 40), (0, -80)])
POINT_NAMES = ["center", "tower X", "tower Y", "tower Z", "Y-Z", "Z-X", "front"]
TOUCHES_PER_ROUND = 8


def rounds_from_log(path):
    touches = [float(m[1]) for m in re.finditer(r"Bed X: \S+ Y: \S+ Z: (\S+)", open(path).read())]
    rounds = [touches[i : i + TOUCHES_PER_ROUND] for i in range(0, len(touches) - TOUCHES_PER_ROUND + 1, TOUCHES_PER_ROUND)]
    return np.array([[(r[0] + r[1]) / 2, *r[2:]] for r in rounds])


def firmware(entry):
    return dm.from_marlin(entry["M665"], entry["M666"])


def readings(machine, fw):
    return np.array([dm.probe_reading(machine, fw, q) for q in PROBE_POINTS])


def shift(fw_from, fw_to):
    machine = dm.machine_like(fw_from)
    return readings(machine, fw_to) - readings(machine, fw_from)


def with_endstops(fw, E):
    return dm.to_marlin(dict(L=fw["L"], R=fw["R"], ang=fw["ang"], rod=fw["rod"], E=E))


def compensate(reference, measured):
    fw_ref = firmware(reference)
    target = np.asarray(reference["readings"])
    bed_change = np.asarray(measured["readings"]) + shift(firmware(measured), fw_ref) - target
    E0 = dm.endstop_heights(fw_ref)
    dE = np.zeros(3)
    for _ in range(4):
        base = shift(fw_ref, with_endstops(fw_ref, E0 + dE))
        B = np.empty((len(PROBE_POINTS), 3))
        for i in range(3):
            e = dE.copy()
            e[i] += 0.05
            B[:, i] = (shift(fw_ref, with_endstops(fw_ref, E0 + e)) - base) / 0.05
        dE += np.linalg.lstsq(B, -bed_change - base, rcond=None)[0]
    fw_new = with_endstops(fw_ref, E0 + dE)
    predicted = target + bed_change + shift(fw_ref, fw_new)
    return bed_change, fw_new, predicted


def main():
    parser = argparse.ArgumentParser(description="H and M666 that bring the probe readings back to a reference after the bed moved")
    parser.add_argument("data", help="JSON with 'reference' and 'measured', or a serial log with --parse")
    parser.add_argument("--parse", action="store_true", help="print the 7 readings of each probing round in a serial log")
    args = parser.parse_args()

    if args.parse:
        rounds = rounds_from_log(args.data)
        for r in rounds:
            print(json.dumps(np.round(r, 3).tolist()))
        print("mean", json.dumps(np.round(rounds.mean(0), 3).tolist()))
        return

    data = json.load(open(args.data))
    bed_change, fw_new, predicted = compensate(data["reference"], data["measured"])
    print(f"{'point':8s} {'bed change':>10s} {'predicted':>10s} {'reference':>10s}")
    for name, c, p, r in zip(POINT_NAMES, bed_change, predicted, data["reference"]["readings"]):
        print(f"{name:8s} {c:+10.2f} {p:+10.2f} {r:+10.2f}")
    print(dm.marlin_gcode(fw_new))


if __name__ == "__main__":
    main()
