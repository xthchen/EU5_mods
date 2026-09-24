"""Build culture and religion advance tooltips from an installed EU5 game directory.

Usage: python3 build_catalogue.py '/path/to/Europa Universalis V'
The generated GUI files are vanilla copies with tooltip additions.
"""

from collections import defaultdict
from pathlib import Path
import re
import sys


MOD = Path(__file__).resolve().parent
GAME = Path(sys.argv[1]).resolve() / "game"
VIEW = GAME / "in_game/gui/culture_lateral_view.gui"
OUTPUT = MOD / "in_game/gui/culture_lateral_view.gui"


def blocks(source):
    """Yield named top-level Clausewitz blocks without parsing their contents."""
    source = re.sub(r"#.*", "", source.lstrip("\ufeff"))
    header = re.compile(r"(?m)^\s*([A-Za-z_][\w.-]*)\s*=\s*\{")
    for match in header.finditer(source):
        position = match.start()
        # Determine the depth at each candidate by scanning from the last one.
        # This intentionally ignores braces in quoted strings, which are rare in
        # the culture/advance definitions and checked below after extraction.
        depth = source[:position].count("{") - source[:position].count("}")
        if depth != 0:
            continue
        name = match.group(1)
        start = match.end()
        cursor = match.end()
        level = 1
        while level and cursor < len(source):
            if source[cursor] == "{":
                level += 1
            elif source[cursor] == "}":
                level -= 1
            cursor += 1
        if level:
            raise ValueError(f"Unclosed block {name}")
        yield name, source[start:cursor - 1]


def first(pattern, text):
    match = re.search(pattern, text)
    return match.group(1) if match else None


def field_block(body, field):
    match = re.search(r"\b" + re.escape(field) + r"\s*=\s*\{", body)
    if not match:
        return None
    start = match.end()
    level = 1
    cursor = start
    while level and cursor < len(body):
        if body[cursor] == "{":
            level += 1
        elif body[cursor] == "}":
            level -= 1
        cursor += 1
    return body[start:cursor - 1] if level == 0 else None


def make_catalogue():
    dialects = {}
    for path in (GAME / "in_game/common/languages").glob("*.txt"):
        for language, body in blocks(path.read_text(encoding="utf-8-sig")):
            for dialect in re.findall(r"(?m)^\s*([\w.-]+_dialect)\s*=\s*\{", body):
                dialects[dialect] = language

    cultures = {}
    for path in (GAME / "in_game/common/cultures").glob("*.txt"):
        for culture, body in blocks(path.read_text(encoding="utf-8-sig")):
            language = first(r"\blanguage\s*=\s*([\w.-]+)", body)
            groups_body = field_block(body, "culture_groups") or ""
            groups = set(re.findall(r"[\w.-]+", groups_body))
            cultures[culture] = (dialects.get(language, language), groups)

    catalogue = defaultdict(dict)
    for path in sorted((GAME / "in_game/common/advances").glob("*.txt")):
        for advance, body in blocks(path.read_text(encoding="utf-8-sig")):
            potential = field_block(body, "potential")
            if not potential:
                continue
            named = set(re.findall(r"\bculture\s*=\s*culture:([\w.-]+)", potential))
            named.update(re.findall(r"\bmerged_culture_group_contains_culture\s*=\s*culture:([\w.-]+)", potential))
            languages = set(re.findall(r"\bculture\.language\s*=\s*language:([\w.-]+)", potential))
            groups = set(re.findall(r"\bhas_culture_group\s*=\s*culture_group:([\w.-]+)", potential))
            if not (named or languages or groups):
                continue
            icon = first(r"(?m)^\s*icon\s*=\s*([\w.-]+)", body) or advance
            age = first(r"(?m)^\s*age\s*=\s*([\w.-]+)", body) or "age_9"
            for culture, (language, culture_groups) in cultures.items():
                if culture in named or language in languages or groups & culture_groups:
                    catalogue[culture][advance] = (age, icon)
    return catalogue


def make_gui(catalogue):
    sections = []
    for culture, advances in sorted(catalogue.items()):
        rows = []
        for advance, (age, icon) in sorted(advances.items(), key=lambda item: (item[1][0], item[0])):
            icon_path = GAME / f"main_menu/gfx/interface/advance/{icon}.dds"
            if not icon_path.exists():
                icon = "_default"
            rows.append(f'''\t\t\t\t\t\thbox = {{
\t\t\t\t\t\t\ticon = {{ size = {{ 22 22 }} texture = "gfx/interface/advance/{icon}.dds" }}
\t\t\t\t\t\t\ttext_single = {{ minimumsize = {{ 240 22 }} autoresize = yes text = "{advance}" }}
\t\t\t\t\t\t}}''')
        contents = f'''\t\t\t\t\t\tvbox = {{
\t\t\t\t\t\t\tignoreinvisible = yes
{chr(10).join(rows)}
\t\t\t\t\t\t}}'''
        if len(rows) > 10:
            contents = f'''\t\t\t\t\t\tscrollarea = {{
\t\t\t\t\t\t\tsize = {{ 400 320 }}
\t\t\t\t\t\t\tscrollbarpolicy_horizontal = always_off
\t\t\t\t\t\t\tscrollbarpolicy_vertical = as_needed
\t\t\t\t\t\t\tscrollbar_vertical = {{ using = Scrollbar_Vertical }}
\t\t\t\t\t\t\tscrollwidget = {{
{contents}
\t\t\t\t\t\t\t}}
\t\t\t\t\t\t}}'''
        # Vanilla GUI uses localized-name comparisons for fixed definitions.
        # Unlike GetCultureByKey / culture-variable promotion, both helpers in
        # this expression have working examples in the shipped GUI files.
        matches = f"EqualTo_string(Culture.GetNameWithNoTooltip, Localize('{culture}'))"
        sections.append(f'''\t\t\t\t\tTooltipListBase = {{
\t\t\t\t\t\tvisible = "[{matches}]"
\t\t\t\t\t\tblockoverride "block_title" {{ text = "POSSIBLE_ADVANCES_FOR_FORMABLE" }}
{contents}
\t\t\t\t\t}}''')
    insertion = "\n" + "\n".join(sections) + "\n"
    vanilla = VIEW.read_text(encoding="utf-8-sig")
    needle = '''\t\t\t\t\t\t\t\ttooltipwidget = {
\t\t\t\t\t\t\t\t\tusing = culture_list_tooltip
\t\t\t\t\t\t\t\t}'''
    replacement = '''\t\t\t\t\t\t\t\ttooltipwidget = {
\t\t\t\t\t\t\t\t\tusing = culture_list_tooltip
\t\t\t\t\t\t\t\t\tblockoverride "culture_list_tooltip_content_extra" {''' + insertion + '''\t\t\t\t\t\t\t\t\t}
\t\t\t\t\t\t\t\t}'''
    if vanilla.count(needle) != 1:
        raise ValueError("Expected exactly one Culture Breakdown hover tooltip")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(vanilla.replace(needle, replacement), encoding="utf-8-sig")
    return len(sections)


if __name__ == "__main__":
    if not VIEW.is_file():
        raise SystemExit(f"Cannot find {VIEW}")
    catalogue = make_catalogue()
    sections = make_gui(catalogue)
    from optimized_catalogue import write_assets, write_age_icons, compact_gui
    write_assets({culture: sorted(
        ((advance, age) for advance, (age, _icon) in advances.items()),
        key=lambda item: (item[1], item[0])
    ) for culture, advances in catalogue.items()})
    write_age_icons()
    compact_gui()
    from religion_catalogue import make_catalogue as make_religion_catalogue, write_assets as write_religion_assets, write_gui as write_religion_gui
    religion_catalogue = make_religion_catalogue(GAME, blocks, field_block, first)
    write_religion_assets(religion_catalogue)
    write_religion_gui(GAME, religion_catalogue)
    print(f"Generated one tooltip widget, {sections} culture lists and "
          f"{sum(map(len, catalogue.values()))} culture–advance entries; "
          f"{len(religion_catalogue)} religion lists and "
          f"{sum(map(len, religion_catalogue.values()))} religion–advance entries")
