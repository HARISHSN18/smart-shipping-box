"""3D packing heuristic: tries every rotation of every item at candidate corner points."""
from itertools import permutations


def _overlap(a, b):
    ax, ay, az, al, aw, ah = a
    bx, by, bz, bl, bw, bh = b
    return not (ax + al <= bx or bx + bl <= ax or
                ay + aw <= by or by + bw <= ay or
                az + ah <= bz or bz + bh <= az)


def pack(items, box_dims):
    """
    items: list of (l, w, h) tuples (one entry per physical unit)
    box_dims: (L, W, H)
    Returns list of placements [(x,y,z,l,w,h), ...] or None if it doesn't fit.
    """
    L, W, H = box_dims
    placed = []
    points = [(0.0, 0.0, 0.0)]
    for dims in sorted(items, key=lambda d: d[0] * d[1] * d[2], reverse=True):
        spot = None
        for (px, py, pz) in sorted(points, key=lambda p: (p[2], p[1], p[0])):
            for (l, w, h) in sorted(set(permutations(dims)), key=lambda o: o[2]):
                if px + l > L or py + w > W or pz + h > H:
                    continue
                cand = (px, py, pz, l, w, h)
                if any(_overlap(cand, p) for p in placed):
                    continue
                spot = cand
                break
            if spot:
                break
        if not spot:
            return None
        placed.append(spot)
        x, y, z, l, w, h = spot
        points.extend([(x + l, y, z), (x, y + w, z), (x, y, z + h)])
    return placed
