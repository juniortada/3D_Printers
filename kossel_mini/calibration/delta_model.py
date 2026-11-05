import numpy as np

TOWER_ANGLES = np.radians([210.0, 330.0, 90.0])
PROBE_XY = np.array([-33.24, -10.88])
PROBE_TRIGGER_Z = 3.3


def from_marlin(m665, m666):
    return dict(
        L=m665["L"],
        R=m665["R"],
        H=m665["H"],
        ang=tuple(m665.get(k, 0.0) for k in "XYZ"),
        rod=tuple(m665.get(k, 0.0) for k in "ABC"),
        adj=tuple(m666.get(k, 0.0) for k in "XYZ"),
    )


def marlin_gcode(fw):
    return (
        "M665 L%.2f R%.2f H%.2f X%.2f Y%.2f Z%.2f A%.2f B%.2f C%.2f\nM666 X%.2f Y%.2f Z%.2f"
        % (fw["L"], fw["R"], fw["H"], *fw["ang"], *fw["rod"], *fw["adj"])
    )


def towers(R, ang):
    a = TOWER_ANGLES + np.radians(ang)
    return np.stack([R * np.cos(a), R * np.sin(a)], axis=1)


def rods(g):
    return g["L"] + np.asarray(g["rod"])


def carriage_heights(p, g):
    T = towers(g["R"], g["ang"])
    L = rods(g)
    return p[2] + np.sqrt(L**2 - ((p[0] - T[:, 0]) ** 2 + (p[1] - T[:, 1]) ** 2))


def endstop_heights(fw):
    T = towers(fw["R"], fw["ang"])
    return fw["H"] + np.sqrt(rods(fw) ** 2 - (T**2).sum(1)) - np.asarray(fw["adj"])


def travel_from_home(p, fw):
    return endstop_heights(fw) - carriage_heights(np.asarray(p, float), fw)


def trilaterate(c, T, L):
    P = np.column_stack([T, c])
    ex = P[1] - P[0]
    d = np.linalg.norm(ex)
    ex /= d
    v = P[2] - P[0]
    i = ex @ v
    ey = v - i * ex
    ey /= np.linalg.norm(ey)
    ez = np.cross(ex, ey)
    j = ey @ v
    x = (L[0] ** 2 - L[1] ** 2 + d * d) / (2 * d)
    y = (L[0] ** 2 - L[2] ** 2 + i * i + j * j) / (2 * j) - (i / j) * x
    z = -np.sqrt(L[0] ** 2 - x * x - y * y)
    return P[0] + x * ex + y * ey + z * ez


def machine_like(fw):
    return dict(L=fw["L"], R=fw["R"], ang=fw["ang"], rod=fw["rod"], E=endstop_heights(fw))


def nozzle_at(travel, machine):
    T = towers(machine["R"], machine["ang"])
    return trilaterate(machine["E"] - travel, T, rods(machine))


def printed_point(p, fw, machine):
    return nozzle_at(travel_from_home(p, fw), machine)


def to_marlin(machine):
    T = towers(machine["R"], machine["ang"])
    k = machine["E"] - np.sqrt(rods(machine) ** 2 - (T**2).sum(1))
    H = k.min()
    return dict(L=machine["L"], R=machine["R"], H=H, ang=tuple(machine["ang"]), rod=tuple(machine["rod"]), adj=tuple(H - k))


def probe_reading(machine, fw, probe_xy):
    nozzle = np.asarray(probe_xy, float) - PROBE_XY
    real = printed_point([*nozzle, PROBE_TRIGGER_Z], fw, machine)
    return PROBE_TRIGGER_Z - real[2]
