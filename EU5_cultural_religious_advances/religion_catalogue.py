"""Prebuild religion-specific advance rows for EU5's religion tooltip."""

from collections import defaultdict
from pathlib import Path
import re

from optimized_catalogue import AGES


MOD = Path(__file__).resolve().parent
LOCALIZATION = MOD / "main_menu/localization/english/hca_religion_advances_l_english.yml"
GUI = MOD / "in_game/gui/shared/religion_tooltips.gui"


def make_catalogue(game, blocks, field_block, first):
    religions = {}
    for path in (game / "in_game/common/religions").glob("*.txt"):
        for religion, body in blocks(path.read_text(encoding="utf-8-sig")):
            religions[religion] = first(r"(?m)^\s*group\s*=\s*([\w.-]+)", body)

    catalogue = defaultdict(dict)
    for path in sorted((game / "in_game/common/advances").glob("*.txt")):
        for advance, body in blocks(path.read_text(encoding="utf-8-sig")):
            potential = field_block(body, "potential") or ""
            if not re.search(r"\breligion(?:\.group)?\s*=", potential):
                continue
            # A religion on its own must suffice; mixed country/culture gates are
            # deliberately not advertised as religion-specific possibilities.
            if re.search(r"\b(has_or_had_tag|culture|country|original_country)\b", potential):
                continue
            excluded = field_block(potential, "NOT") or ""
            allowed = potential.replace(excluded, "") if excluded else potential
            named = set(re.findall(r"\breligion\s*=\s*religion:([\w.-]+)", allowed))
            groups = set(re.findall(r"\breligion\.group\s*=\s*religion_group:([\w.-]+)", allowed))
            excluded_named = set(re.findall(r"\breligion\s*=\s*religion:([\w.-]+)", excluded))
            if not (named or groups):
                continue
            age = first(r"(?m)^\s*age\s*=\s*([\w.-]+)", body)
            if age not in AGES:
                continue
            for religion, group in religions.items():
                if religion not in excluded_named and (religion in named or group in groups):
                    catalogue[religion][advance] = age
    return catalogue


def write_assets(catalogue):
    localization = ["l_english:"]
    for religion, advances in sorted(catalogue.items()):
        by_age = defaultdict(list)
        for advance, age in sorted(advances.items(), key=lambda item: (item[1], item[0])):
            by_age[age].append(advance)
        for row_index, age in enumerate(sorted(by_age)):
            number = AGES.index(age) + 1
            names = [f"[ShowAdvanceName('{advance}')]" for advance in by_age[age]]
            if len(names) > 2:
                rendered = ", ".join(names[:-1]) + ", and " + names[-1]
            else:
                rendered = " and ".join(names)
            key = f"HCA_RELIGION_{religion.upper()}_AGE_{number}"
            localization.append(f' {key}: "• @hca_age_{number}! {rendered}"')
    LOCALIZATION.parent.mkdir(parents=True, exist_ok=True)
    LOCALIZATION.write_text("\n".join(localization) + "\n", encoding="utf-8-sig")


def write_gui(game, catalogue):
    source = (game / "in_game/gui/shared/religion_tooltips.gui").read_text(encoding="utf-8-sig")
    marker = '''\t\t\tTooltipFlavorTextBlock = {
\t\t\t\tblockoverride "text" {
\t\t\t\t\ttext = "[Religion.GetFlavorText]"'''
    if source.count(marker) != 1:
        raise ValueError("Religion tooltip insertion point changed")
    sections = []
    for religion, advances in sorted(catalogue.items()):
        ages = sorted(set(advances.values()))
        rows = []
        for row_index, age in enumerate(ages):
            number = AGES.index(age) + 1
            background = "\n\t\t\t\t\t\tbackground = { using = tooltip_table_field_texture }" if row_index % 2 else ""
            rows.append(f'''\t\t\t\t\ttext_multi = {{
\t\t\t\t\t\tlayoutpolicy_horizontal = expanding
\t\t\t\t\t\tminimumsize = {{ -1 40 }}
\t\t\t\t\t\tautoresize = yes
\t\t\t\t\t\tmargin = {{ 10 4 }}
\t\t\t\t\t\talign = left|nobaseline
\t\t\t\t\t\ttext = "HCA_RELIGION_{religion.upper()}_AGE_{number}"{background}
\t\t\t\t\t}}''')
        sections.append(f'''\t\t\tTooltipListBase = {{
\t\t\t\tvisible = "[EqualTo_string(Religion.GetNameWithNoTooltip, Localize('{religion}'))]"
\t\t\t\tblockoverride "block_title" {{ text = "POSSIBLE_ADVANCES_FOR_FORMABLE" }}
\t\t\t\tvbox = {{
\t\t\t\t\tignoreinvisible = yes
\t\t\t\t\tlayoutpolicy_horizontal = expanding
''' + "\n".join(rows) + '''
\t\t\t\t}
\t\t\t}''')
    insertion = "\n".join(sections) + "\n\n"
    GUI.parent.mkdir(parents=True, exist_ok=True)
    source = source.replace(marker, insertion + marker)
    GUI.write_text(wrap_religion_body(source), encoding="utf-8-sig")


def wrap_religion_body(source):
    """Keep the title fixed and scroll the complete religion tooltip body."""
    marker = '\t\tblockoverride "tooltip_content" {'
    start = source.index(marker)
    opening = source.index("{", start)
    depth = 1
    end = opening + 1
    while depth:
        if source[end] == "{":
            depth += 1
        elif source[end] == "}":
            depth -= 1
        end += 1
    body = source[opening + 1:end - 1]
    wrapped = (
        marker + '\n\t\t\tTooltipScrolledContentSection = {'
        '\n\t\t\t\tblockoverride "block_scrollarea" { maximumsize = { -1 520 } }'
        '\n\t\t\t\tblockoverride "scrollarea_content" {'
        '\n\t\t\t\t\tTooltipContentSection = {'
        '\n\t\t\t\t\t\tset_parent_dimension_to_minimum = height'
        + body +
        '\n\t\t\t\t\t}'
        '\n\t\t\t\t}'
        '\n\t\t\t}'
        '\n\t\t}'
    )
    return source[:start] + wrapped + source[end:]
