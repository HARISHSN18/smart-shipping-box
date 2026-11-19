"""
Box recommendation logic (kept out of views on purpose).

ALGORITHM (simple 3D first-fit heuristic)
  1. Expand the order into single units (3 x mug -> 3 items).
  2. Reject boxes whose weight capacity or total volume is too small (cheap filters).
  3. For the rest, try to place every item inside the box:
       - largest items first,
       - candidate positions = the origin plus the three corners created by each placed item,
       - for each position try all 6 rotations and take the first that is inside the box
         and overlaps nothing.
  4. Among boxes where everything fits: smallest volume wins, lowest cost breaks ties.

LIMITATIONS (initial version)
  - It is a heuristic, not an optimal solver: it can say "does not fit" for a tight
    arrangement that does exist. It never says "fits" wrongly.
  - Only 90-degree, axis-aligned rotations. No padding, no fragile / "this side up" rules.
  - Weight is only checked as a total, not distribution or stacking strength.
  - One parcel only: it does not split an order across several boxes.
"""
from dataclasses import dataclass
from itertools import permutations
from typing import Optional

from .models import Box, Order


@dataclass
class Recommendation:
    box: Optional[Box]
    reason: str
    plan: Optional[dict]
    total_weight: float

    @property
    def fits(self):
        return self.box is not None


def _overlap(a, b):
    ax, ay, az, al, aw, ah = a
    bx, by, bz, bl, bw, bh = b
    return not (ax + al <= bx or bx + bl <= ax or ay + aw <= by or by + bw <= ay or az + ah <= bz or bz + bh <= az)


def pack(units, box_dims):
    """Return placements [(x, y, z, l, w, h)] for all units, or None if they don't fit."""
    L, W, H = box_dims
    placed, points = [], [(0.0, 0.0, 0.0)]
    for dims in sorted(units, key=lambda d: d[0] * d[1] * d[2], reverse=True):
        spot = None
        for px, py, pz in sorted(points, key=lambda p: (p[2], p[1], p[0])):
            for l, w, h in sorted(set(permutations(dims)), key=lambda o: o[2]):
                if px + l > L or py + w > W or pz + h > H:
                    continue
                cand = (px, py, pz, l, w, h)
                if not any(_overlap(cand, p) for p in placed):
                    spot = cand
                    break
            if spot:
                break
        if not spot:
            return None
        placed.append(spot)
        x, y, z, l, w, h = spot
        points += [(x + l, y, z), (x, y + w, z), (x, y, z + h)]
    return placed


def _fits_alone(unit, box):
    return all(u <= b for u, b in zip(sorted(unit), sorted((box.length, box.width, box.height))))


def _explain_failure(units, total_weight, volume, boxes):
    strongest = max(b.max_weight for b in boxes)
    if total_weight > strongest:
        return (f"No box can carry {total_weight:.2f} kg: the strongest box holds {strongest:g} kg. "
                "Split the order into several parcels.")
    too_big = [u for u in set(units) if not any(_fits_alone(u, b) for b in boxes)]
    if too_big:
        l, w, h = too_big[0]
        return f"A product of {l:g} x {w:g} x {h:g} cm is larger than every box in any rotation. Add a bigger box."
    if volume > max(b.volume for b in boxes):
        return "The items together are larger than the biggest box. Split the order into several parcels."
    return ("Every item fits on its own, but no single box can hold them all together "
            "(according to the packing heuristic). Split the order into several parcels.")


def recommend_box(items, boxes=None):
    """items: iterable of (length, width, height, weight, quantity)."""
    boxes = list(Box.objects.all() if boxes is None else boxes)
    units, total_weight = [], 0.0
    for l, w, h, weight, qty in items:
        units += [(l, w, h)] * qty
        total_weight += weight * qty
    if not units:
        return Recommendation(None, "The order has no items.", None, 0.0)
    if not boxes:
        return Recommendation(None, "No shipping boxes exist yet. Add boxes first.", None, total_weight)

    volume = sum(l * w * h for l, w, h in units)
    suitable = []
    for box in boxes:
        if total_weight > box.max_weight or volume > box.volume:
            continue
        placements = pack(units, (box.length, box.width, box.height))
        if placements:
            suitable.append((box, placements))
    if not suitable:
        return Recommendation(None, _explain_failure(units, total_weight, volume, boxes), None, total_weight)

    suitable.sort(key=lambda bp: (bp[0].volume, bp[0].cost))
    box, placements = suitable[0]
    reason = (f"{len(suitable)} of {len(boxes)} boxes can hold all {len(units)} item(s) "
              f"({total_weight:.2f} kg). '{box.name}' is the smallest of them by volume.")
    if sum(1 for b, _ in suitable if b.volume == box.volume) > 1:
        reason += " Several boxes had the same size, so the cheapest was chosen."
    plan = {
        "dimensions_cm": [box.length, box.width, box.height],
        "fill_rate": round(volume / box.volume, 3),
        "placements": [dict(zip("xyzlwh", p)) for p in placements],
    }
    return Recommendation(box, reason, plan, total_weight)


def recommend_for_order(order):
    """Run the recommendation for a saved order and store the result on it."""
    items = [(i.product.length, i.product.width, i.product.height, i.product.weight, i.quantity)
             for i in order.items.select_related("product")]
    rec = recommend_box(items)
    order.recommended_box = rec.box
    order.reason = rec.reason
    order.packing_plan = rec.plan
    order.packing_status = Order.Status.PACKED if rec.fits else Order.Status.NO_BOX
    order.save()
    return order

