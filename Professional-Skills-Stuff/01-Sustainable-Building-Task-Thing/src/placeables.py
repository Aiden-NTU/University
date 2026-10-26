"""Reusable, no-code placeable assets defined in ``placeables.json``.

An asset defines its shape, colour, print behaviour and (when relevant) catalogue item once.
A placement then puts that asset in a room or at a site coordinate.  All dimensions are metres.
Only the small set of robust, presentation-model shapes below is deliberately exposed to JSON;
new shape types can be added here without changing any exporter.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

from geom import Manifold, box, union

REGISTRY_FILE = Path(__file__).with_name("placeables.json")
FACING = {"N", "S", "E", "W"}


@dataclass(frozen=True)
class Asset:
    """One reusable asset definition from the JSON registry."""

    key: str
    shape: str
    catalogue_type: str | None
    colour: tuple[float, float, float]
    printable: bool
    print_layer: str | None
    parameters: dict[str, Any]


@dataclass(frozen=True)
class Placement:
    """One enabled use of an asset, in local building/site coordinates."""

    id: str
    asset_key: str
    target: str
    room: str | None
    x_m: float
    y_m: float
    z_m: float
    facing: str
    parameters: dict[str, Any]


def _number(value: Any, name: str, *, minimum: float = 0.0) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a number") from exc
    if result < minimum:
        raise ValueError(f"{name} must be at least {minimum}")
    return result


def _colour(value: Any, name: str) -> tuple[float, float, float]:
    if not isinstance(value, str) or len(value) != 7 or not value.startswith("#"):
        raise ValueError(f"{name} must be a hex colour such as #E8913A")
    try:
        return tuple(int(value[i:i + 2], 16) / 255 for i in (1, 3, 5))
    except ValueError as exc:
        raise ValueError(f"{name} must be a hex colour such as #E8913A") from exc


def _params(defaults: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
    return {**defaults, **overrides}


def _sofa(params: dict[str, Any], facing: str, for_print: bool = False) -> Manifold:
    """Simple solid sofa, centred on x/y and facing the named cardinal direction."""
    width = _number(params.get("width_m", 2.0), "sofa width_m", minimum=0.1)
    depth = _number(params.get("depth_m", 0.9), "sofa depth_m", minimum=0.1)
    height = _number(params.get("height_m", 0.8), "sofa height_m", minimum=0.1)
    seat_h = min(0.42, height * 0.6)
    arm_w, back_d = min(0.2, width / 4), min(0.2, depth / 3)
    x0, x1, y0, y1 = -width / 2, width / 2, -depth / 2, depth / 2
    if facing in ("E", "W"):
        x0, x1, y0, y1 = y0, y1, x0, x1
    solid = box(x0, y0, 0, x1, y1, seat_h)
    if facing in ("N", "S"):
        by0, by1 = (y0, y0 + back_d) if facing == "N" else (y1 - back_d, y1)
        solid += box(x0, by0, seat_h, x1, by1, height)
        solid += box(x0, y0, seat_h, x0 + arm_w, y1, min(height, seat_h + 0.2))
        solid += box(x1 - arm_w, y0, seat_h, x1, y1, min(height, seat_h + 0.2))
    else:
        bx0, bx1 = (x0, x0 + back_d) if facing == "E" else (x1 - back_d, x1)
        solid += box(bx0, y0, seat_h, bx1, y1, height)
        solid += box(x0, y0, seat_h, x1, y0 + arm_w, min(height, seat_h + 0.2))
        solid += box(x0, y1 - arm_w, seat_h, x1, y1, min(height, seat_h + 0.2))
    return solid


def _screen(params: dict[str, Any], facing: str, for_print: bool = False) -> Manifold:
    """Wall-mounted display, centred on the requested wall coordinate."""
    width = _number(params.get("width_m", 1.25), "screen width_m", minimum=0.1)
    height = _number(params.get("height_m", 0.75), "screen height_m", minimum=0.1)
    sill = _number(params.get("sill_m", 1.1), "screen sill_m")
    depth = _number(params.get("depth_m", 0.06), "screen depth_m", minimum=0.01)
    if facing in ("N", "S"):
        return box(-width / 2, -depth / 2, sill, width / 2, depth / 2, sill + height)
    return box(-depth / 2, -width / 2, sill, depth / 2, width / 2, sill + height)


def _swing(params: dict[str, Any], facing: str, for_print: bool = False) -> Manifold:
    """A durable, simplified swing frame for the 1:1000 physical model.

    Members are intentionally thicker than a real swing so they remain printable at 1:1000
    (0.8 m = 0.8 mm = two 0.4 mm nozzle lines). The hanging seat would start in mid-air on
    the printer, so the printed version is the frame only.
    """
    width = _number(params.get("width_m", 3.2), "swing width_m", minimum=0.5)
    depth = _number(params.get("depth_m", 1.7), "swing depth_m", minimum=0.5)
    height = _number(params.get("height_m", 3.2), "swing height_m", minimum=0.5)
    member = _number(params.get("member_m", 0.8), "swing member_m", minimum=0.8)
    seat_w = _number(params.get("seat_width_m", 0.9), "swing seat_width_m", minimum=0.2)
    seat_d = _number(params.get("seat_depth_m", 0.4), "swing seat_depth_m", minimum=0.1)
    seat_h = _number(params.get("seat_height_m", 1.0), "swing seat_height_m", minimum=0.1)
    # The frame runs east-west. A future shape type can add rotated geometry if required.
    posts = [
        box(-width / 2, -depth / 2, 0, -width / 2 + member, -depth / 2 + member, height),
        box(-width / 2, depth / 2 - member, 0, -width / 2 + member, depth / 2, height),
        box(width / 2 - member, -depth / 2, 0, width / 2, -depth / 2 + member, height),
        box(width / 2 - member, depth / 2 - member, 0, width / 2, depth / 2, height),
        box(-width / 2, -member / 2, height - member, width / 2, member / 2, height),
    ]
    if for_print:
        return union(posts)
    posts.append(box(-seat_w / 2, -seat_d / 2, seat_h, seat_w / 2, seat_d / 2, seat_h + 0.1))
    for x in (-seat_w / 2 + 0.05, seat_w / 2 - 0.05):
        posts.append(box(x - 0.025, -0.025, seat_h, x + 0.025, 0.025, height - member))
    return union(posts)


def _box(params: dict[str, Any], facing: str, for_print: bool = False) -> Manifold:
    width = _number(params.get("width_m", 1.0), "box width_m", minimum=0.01)
    depth = _number(params.get("depth_m", 1.0), "box depth_m", minimum=0.01)
    height = _number(params.get("height_m", 1.0), "box height_m", minimum=0.01)
    return box(-width / 2, -depth / 2, 0, width / 2, depth / 2, height)


SHAPES: dict[str, Callable[[dict[str, Any], str], Manifold]] = {
    "sofa": _sofa,
    "screen": _screen,
    "swing": _swing,
    "box": _box,
}


@lru_cache(maxsize=1)
def registry() -> tuple[dict[str, Asset], tuple[Placement, ...]]:
    """Read and validate the teammate-editable JSON registry."""
    try:
        raw = json.loads(REGISTRY_FILE.read_text())
    except json.JSONDecodeError as exc:
        raise ValueError(f"Could not read {REGISTRY_FILE.name}: {exc.msg} on line {exc.lineno}") from exc
    if not isinstance(raw, dict) or not isinstance(raw.get("assets"), dict) or not isinstance(raw.get("placements"), list):
        raise ValueError(f"{REGISTRY_FILE.name} needs an 'assets' object and a 'placements' list")

    assets: dict[str, Asset] = {}
    for key, item in raw["assets"].items():
        if not isinstance(key, str) or not isinstance(item, dict):
            raise ValueError("Every asset needs a text name and an object of settings")
        shape = item.get("shape")
        if shape not in SHAPES:
            raise ValueError(f"asset '{key}' has unsupported shape '{shape}'; choose {', '.join(SHAPES)}")
        parameters = item.get("parameters", {})
        if not isinstance(parameters, dict):
            raise ValueError(f"asset '{key}' parameters must be an object")
        catalogue_type = item.get("catalogue_type")
        if catalogue_type is not None and not isinstance(catalogue_type, str):
            raise ValueError(f"asset '{key}' catalogue_type must be text")
        assets[key] = Asset(
            key=key,
            shape=shape,
            catalogue_type=catalogue_type or None,
            colour=_colour(item.get("colour", "#C9CCCE"), f"asset '{key}' colour"),
            printable=bool(item.get("printable", shape not in {"screen", "swing"})),
            print_layer=item.get("print_layer"),
            parameters=parameters,
        )

    placements: list[Placement] = []
    ids: set[str] = set()
    for i, item in enumerate(raw["placements"], 1):
        if not isinstance(item, dict):
            raise ValueError(f"placement {i} must be an object")
        if not item.get("enabled", True):
            continue
        placement_id = item.get("id")
        asset_key = item.get("asset")
        target = item.get("target")
        if not isinstance(placement_id, str) or not placement_id:
            raise ValueError(f"placement {i} needs an id")
        if placement_id in ids:
            raise ValueError(f"placement id '{placement_id}' is used more than once")
        ids.add(placement_id)
        if asset_key not in assets:
            raise ValueError(f"placement '{placement_id}' refers to unknown asset '{asset_key}'")
        if target not in {"room", "site"}:
            raise ValueError(f"placement '{placement_id}' target must be 'room' or 'site'")
        room = item.get("room")
        if target == "room" and (not isinstance(room, str) or not room):
            raise ValueError(f"room placement '{placement_id}' needs a room code such as F01")
        if target == "site" and assets[asset_key].print_layer not in {None, "proposal"}:
            raise ValueError(f"site asset '{asset_key}' print_layer must be 'proposal' or omitted")
        parameters = item.get("parameters", {})
        if not isinstance(parameters, dict):
            raise ValueError(f"placement '{placement_id}' parameters must be an object")
        facing = str(item.get("facing", "N")).upper()
        if facing not in FACING:
            raise ValueError(f"placement '{placement_id}' facing must be N, S, E or W")
        placements.append(Placement(
            id=placement_id,
            asset_key=asset_key,
            target=target,
            room=room if target == "room" else None,
            x_m=_number(item.get("x_m"), f"placement '{placement_id}' x_m", minimum=-10000),
            y_m=_number(item.get("y_m"), f"placement '{placement_id}' y_m", minimum=-10000),
            z_m=_number(item.get("z_m", 0), f"placement '{placement_id}' z_m", minimum=-10000),
            facing=facing,
            parameters=parameters,
        ))
    return assets, tuple(placements)


def _solid(asset: Asset, placement: Placement, z: float, for_print: bool = False) -> Manifold:
    params = _params(asset.parameters, placement.parameters)
    shape = SHAPES[asset.shape](params, placement.facing, for_print)
    return shape.translate((placement.x_m, placement.y_m, z + placement.z_m))


def room_assets(room_id: str) -> list[tuple[Placement, Asset, Manifold]]:
    """Enabled assets for one room, with z=0 at that room's finished floor."""
    assets, placements = registry()
    return [(p, assets[p.asset_key], _solid(assets[p.asset_key], p, 0.0))
            for p in placements if p.target == "room" and p.room == room_id]


def site_assets(ground_at: Callable[[float, float], float],
                for_print: bool = False) -> list[tuple[Placement, Asset, Manifold]]:
    """Enabled site assets, standing on the lowest terrain under their footprint.

    Using the lowest point (minus a small embed) means nothing hovers above a slope; the uphill
    side simply sinks slightly into the ground.
    """
    embed_m = 0.3
    assets, placements = registry()
    out = []
    for p in placements:
        if p.target != "site":
            continue
        asset = assets[p.asset_key]
        x0, y0, _, x1, y1, _ = _solid(asset, p, 0.0).bounding_box()
        z = min(ground_at(x, y) for x in (x0, (x0 + x1) / 2, x1) for y in (y0, (y0 + y1) / 2, y1)) - embed_m
        out.append((p, asset, _solid(asset, p, z, for_print)))
    return out
