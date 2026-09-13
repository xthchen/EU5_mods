#!/usr/bin/env python3
"""Dependency-free static checks for the Potential Cities EU5 mod."""

from __future__ import annotations

import json
import re
import struct
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP_MODE = ROOT / "in_game/gfx/map/map_modes/large_settlements_map_mode.txt"
LOCALIZATION = ROOT / "main_menu/localization/english/large_settlements_l_english.yml"
METADATA = ROOT / ".metadata/metadata.json"
ICON = ROOT / "main_menu/gfx/interface/icons/map_modes/large_settlements.dds"
THUMBNAIL = ROOT / ".metadata/thumbnail.png"
RURAL_RANK_ICON = ROOT / "tools/assets/rural_settlement.png"
TOWN_RANK_ICON = ROOT / "tools/assets/town.png"
BOM = b"\xef\xbb\xbf"


def balanced_braces(text: str) -> bool:
    depth = 0
    in_string = False
    escaped = False
    for line in text.splitlines():
        for char in line.split("#", 1)[0]:
            if escaped:
                escaped = False
                continue
            if char == "\\" and in_string:
                escaped = True
                continue
            if char == '"':
                in_string = not in_string
            elif not in_string and char == "{":
                depth += 1
            elif not in_string and char == "}":
                depth -= 1
                if depth < 0:
                    return False
    return depth == 0 and not in_string


def main() -> int:
    errors: list[str] = []

    for path in (MAP_MODE, LOCALIZATION, METADATA):
        if not path.exists():
            errors.append(f"missing file: {path.relative_to(ROOT)}")
        elif not path.read_bytes().startswith(BOM):
            errors.append(f"missing UTF-8 BOM: {path.relative_to(ROOT)}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    metadata = json.loads(METADATA.read_text(encoding="utf-8-sig"))
    for key in ("name", "id", "game_id", "version", "supported_game_version"):
        if not metadata.get(key):
            errors.append(f"metadata field is missing or empty: {key}")
    if metadata.get("game_id") != "eu5":
        errors.append("metadata game_id must be eu5")

    script = MAP_MODE.read_text(encoding="utf-8-sig")
    if not balanced_braces(script):
        errors.append("map-mode script has unbalanced braces or quotes")
    required_script = (
        "large_settlements = {",
        "owner ?= scope:actor",
        "population > 30",
        "location_rank ?= location_rank:rural_settlement",
        "location_rank ?= location_rank:town",
        "small_map_names = raw_material",
        "medium_map_names = raw_material",
        "market_marker = yes",
        "raw_goods_marker = yes",
        "category = economy",
        "LocationPopulationChanged",
        "LocationOwnerChanged",
    )
    for token in required_script:
        if token not in script:
            errors.append(f"map-mode script is missing: {token}")
    if "population >= 30" in script:
        errors.append("threshold must be strictly greater than 30, not greater than or equal")
    if "all = no" in script:
        errors.append("map markers must use an explicit allow-list so raw-goods icons remain visible")

    localization = LOCALIZATION.read_text(encoding="utf-8-sig")
    if not localization.startswith("l_english:\n"):
        errors.append("English localization must begin with l_english:")
    keys = re.findall(r"^\s+([A-Za-z0-9_]+)\s*:", localization, re.MULTILINE)
    if len(keys) != len(set(keys)):
        errors.append("English localization contains duplicate keys")
    required_keys = {
        "mapmode_large_settlements_name",
        "MAPMODE_LARGE_SETTLEMENTS",
        "large_settlements_rural_legend",
        "large_settlements_town_legend",
        "large_settlements_other_owned_legend",
        "large_settlements_foreign_legend",
        "MAPMODE_LARGE_SETTLEMENTS_TT_RURAL",
        "MAPMODE_LARGE_SETTLEMENTS_TT_TOWN",
        "MAPMODE_LARGE_SETTLEMENTS_TT_OTHER_OWNED",
        "MAPMODE_LARGE_SETTLEMENTS_TT_FOREIGN",
        "MAPMODE_LARGE_SETTLEMENTS_TT_UNOWNED",
        "MAPMODE_LARGE_SETTLEMENTS_TT_WATER",
    }
    for key in sorted(required_keys - set(keys)):
        errors.append(f"English localization is missing key: {key}")

    if not ICON.exists() or ICON.read_bytes()[:4] != b"DDS ":
        errors.append("map-mode icon is missing or is not a DDS file")
    else:
        dds = ICON.read_bytes()[:20]
        height, width = struct.unpack_from("<II", dds, 12)
        if (width, height) != (128, 128):
            errors.append(f"map-mode icon must be 128x128, got {width}x{height}")

    png = THUMBNAIL.read_bytes() if THUMBNAIL.exists() else b""
    if not png.startswith(b"\x89PNG\r\n\x1a\n"):
        errors.append("launcher thumbnail is missing or is not a PNG file")
    else:
        width, height = struct.unpack_from(">II", png, 16)
        if (width, height) != (512, 512):
            errors.append(f"launcher thumbnail must be 512x512, got {width}x{height}")

    for label, path in (
        ("rural-settlement rank icon", RURAL_RANK_ICON),
        ("town rank icon", TOWN_RANK_ICON),
    ):
        rank_icon = path.read_bytes() if path.exists() else b""
        if not rank_icon.startswith(b"\x89PNG\r\n\x1a\n"):
            errors.append(f"{label} is missing or is not a PNG file")
        else:
            width, height = struct.unpack_from(">II", rank_icon, 16)
            if (width, height) != (100, 100):
                errors.append(f"{label} must be 100x100, got {width}x{height}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("All static checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
