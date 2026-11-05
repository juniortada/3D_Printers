import struct
import sys

import numpy as np

PARAMS = dict(
    half=15.85,
    body_h=19.0,
    top_t=1.5,
    wall=1.20,
    tube_od=12.91,
    tube_id=10.68,
    stud_od=9.36,
    stud_id=6.68,
    stud_top=23.44,
    stud_floor=19.4,
    stud_chamfer=0.4,
    pitch=16.0,
    rib_tip=12.65,
    rib_w=1.0,
    rib_leadin=0.6,
    rib_leadin_h=0.8,
    seg=128,
    overlap=0.1,
)


def signed_volume(t):
    return np.einsum("ij,ij->i", t[:, 0], np.cross(t[:, 1], t[:, 2])).sum() / 6


def outward(triangles):
    t = np.array(triangles)
    return t[:, [0, 2, 1]] if signed_volume(t) < 0 else t


def box(x0, x1, y0, y1, z0, z1):
    v = np.array([[x, y, z] for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)])
    faces = [(0, 2, 1), (1, 2, 3), (4, 5, 6), (5, 7, 6), (0, 1, 4), (1, 5, 4),
             (2, 6, 3), (3, 6, 7), (0, 4, 2), (2, 4, 6), (1, 3, 5), (3, 7, 5)]
    return outward([v[list(f)] for f in faces])


def circle(r, cx, cy, z, n):
    a = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return np.column_stack([cx + r * np.cos(a), cy + r * np.sin(a), np.full(n, z)])


def revolve(profile, cx, cy, n):
    rings = [circle(r, cx, cy, z, n) for r, z in profile]
    tris = []
    for i in range(len(rings)):
        A, B = rings[i], rings[(i + 1) % len(rings)]
        for j in range(n):
            k = (j + 1) % n
            tris += [np.array([A[j], B[j], B[k]]), np.array([A[j], B[k], A[k]])]
    return outward(tris)


def cylinder(r, cx, cy, z0, z1, n):
    lo, hi = circle(r, cx, cy, z0, n), circle(r, cx, cy, z1, n)
    tris = []
    for j in range(n):
        k = (j + 1) % n
        tris += [np.array([[cx, cy, z0], lo[k], lo[j]]), np.array([[cx, cy, z1], hi[j], hi[k]]),
                 np.array([lo[j], lo[k], hi[k]]), np.array([lo[j], hi[k], hi[j]])]
    return outward(tris)


def prism(section, along0, along1, place):
    lo = np.array([place(along0, u, z) for u, z in section])
    hi = np.array([place(along1, u, z) for u, z in section])
    m = len(section)
    tris = []
    for i in range(1, m - 1):
        tris += [np.array([lo[0], lo[i + 1], lo[i]]), np.array([hi[0], hi[i], hi[i + 1]])]
    for i in range(m):
        j = (i + 1) % m
        tris += [np.array([lo[i], lo[j], hi[j]]), np.array([lo[i], hi[j], hi[i]])]
    return outward(tris)


def brick(p):
    h, o, n = p["half"], p["overlap"], int(p["seg"])
    ceiling = p["body_h"] - p["top_t"]
    inner = h - p["wall"]
    shells = [
        box(-h, h, -h, h, ceiling, p["body_h"]),
        box(-h, h, inner, h, 0, ceiling + o),
        box(-h, h, -h, -inner, 0, ceiling + o),
        box(inner, h, -inner - o, inner + o, 0, ceiling + o),
        box(-h, -inner, -inner - o, inner + o, 0, ceiling + o),
    ]
    ri, ro = p["tube_id"] / 2, p["tube_od"] / 2
    shells.append(revolve([(ri, 0), (ro, 0), (ro, ceiling + o), (ri, ceiling + o)], 0, 0, n))

    rib = [(inner + o, 0), (p["rib_tip"] + p["rib_leadin"], 0), (p["rib_tip"], p["rib_leadin_h"]),
           (p["rib_tip"], ceiling + o), (inner + o, ceiling + o)]
    w = p["rib_w"] / 2
    for s in (-1, 1):
        for c in (-p["pitch"] / 2, p["pitch"] / 2):
            shells.append(prism(rib, c - w, c + w, lambda t, u, z, s=s: np.array([t, s * u, z])))
            shells.append(prism(rib, c - w, c + w, lambda t, u, z, s=s: np.array([s * u, t, z])))

    so, si, ch = p["stud_od"] / 2, p["stud_id"] / 2, p["stud_chamfer"]
    top, base = p["stud_top"], p["body_h"] - o
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = sx * p["pitch"] / 2, sy * p["pitch"] / 2
            stud = [(si, base), (so, base), (so, top - ch), (so - ch, top), (si + 0.2, top), (si, top - 0.2)]
            shells.append(revolve(stud, cx, cy, n))
            shells.append(cylinder(si + o, cx, cy, base, p["stud_floor"], n))
    return shells


def write_stl(path, triangles, header):
    normals = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    with open(path, "wb") as f:
        f.write(header.encode().ljust(80, b" "))
        f.write(struct.pack("<I", len(triangles)))
        for t, nn in zip(triangles, normals):
            nn = nn / (np.linalg.norm(nn) or 1)
            f.write(struct.pack("<12fH", *nn, *t.ravel(), 0))


def main():
    params = dict(PARAMS)
    for arg in sys.argv[2:]:
        key, value = arg.split("=")
        if key not in params:
            sys.exit(f"unknown parameter {key}; known: {', '.join(params)}")
        params[key] = float(value)
    shells = brick(params)
    triangles = np.concatenate(shells)
    write_stl(sys.argv[1], triangles, "duplo 2x2 - measured from an original Duplo")
    print(f"{len(triangles)} triangles, {len(shells)} shells, {sum(map(signed_volume, shells)):.0f} mm3 summed over the shells")


if __name__ == "__main__":
    main()
