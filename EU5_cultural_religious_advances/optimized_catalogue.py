"""Render the prebuilt culture catalogue as six lightweight age rows.

The original GUI prototype instantiated thousands of widgets on first hover.
Only the six possible age rows are now widgets; their names are prebuilt text.
"""

from pathlib import Path
from collections import defaultdict
import re


MOD = Path(__file__).resolve().parent
GUI = MOD / "in_game/gui/culture_lateral_view.gui"
CUSTOM = MOD / "in_game/common/customizable_localization/hca_possible_advances.txt"
LOCALIZATION = MOD / "main_menu/localization/english/hca_possible_advances_l_english.yml"
AGE_ICONS = MOD / "main_menu/gui/shared/hca_age_font_icons.gui"
MARKER = 'blockoverride "culture_list_tooltip_content_extra" {'
AGES = (
    "age_1_traditions", "age_2_renaissance", "age_3_discovery",
    "age_4_reformation", "age_5_absolutism", "age_6_revolutions",
)


def find_override(source):
    start = source.index(MARKER)
    brace = source.index("{", start)
    level = 1
    end = brace + 1
    while level:
        if source[end] == "{":
            level += 1
        elif source[end] == "}":
            level -= 1
        end += 1
    return start, end, source[brace + 1:end - 1]


def read_prototype():
    source = GUI.read_text(encoding="utf-8-sig")
    _, _, old = find_override(source)
    heading = re.compile(
        r"visible = \"\[EqualTo_string\(Culture.GetNameWithNoTooltip, "
        r"Localize\('([^']+)'\)\)\]\""
    )
    matches = list(heading.finditer(old))
    if len(matches) < 100:
        raise ValueError("Expected the prebuilt GUI catalogue before migration")
    catalogue = {}
    row = re.compile(
        r'texture = "gfx/interface/advance/([^\"]+)"\s*\}\s*'
        r'text_single = \{[^\n]*?text = "([^\"]+)"'
    )
    for index, match in enumerate(matches):
        body = old[match.end():matches[index + 1].start() if index + 1 < len(matches) else len(old)]
        entries = [(advance, icon) for icon, advance in row.findall(body)]
        if not entries:
            raise ValueError(f"No advances found for {match.group(1)}")
        catalogue[match.group(1)] = entries
    return catalogue


def loc_key(culture):
    return "HCA_POSSIBLE_ADVANCES_" + re.sub(r"[^A-Za-z0-9_]", "_", culture).upper()


def write_assets(catalogue):
    for output in (CUSTOM, LOCALIZATION):
        output.parent.mkdir(parents=True, exist_ok=True)

    age_entries = [dict() for _ in AGES]
    stripe_entries = [set() for _ in AGES]
    localization = ["l_english:"]
    for culture, entries in sorted(catalogue.items()):
        by_age = defaultdict(list)
        for advance, age in entries:
            by_age[age].append(advance)
        for row_index, age in enumerate(sorted(by_age)):
            number = AGES.index(age) + 1
            advances = [f"[ShowAdvanceName('{advance}')]" for advance in by_age[age]]
            if len(advances) > 2:
                names = ", ".join(advances[:-1]) + ", and " + advances[-1]
            else:
                names = " and ".join(advances)
            key = f"{loc_key(culture)}_AGE_{number}"
            age_entries[number - 1][culture] = key
            localization.append(f' {key}: "• @hca_age_{number}! {names}"')
            if row_index % 2 == 1:
                stripe_entries[number - 1].add(culture)
    localization.extend([
        ' HCA_EMPTY: ""',
        ' HCA_STRIPED: "yes"',
        ' HCA_UNSTRIPED: "no"',
    ])
    custom = []
    for number in range(1, 7):
        custom.extend([f"hca_age_{number}_advances = {{", "\ttype = culture"])
        for culture, key in sorted(age_entries[number - 1].items()):
            custom.extend([
                "\ttext = {",
                f"\t\ttrigger = {{ this = culture:{culture} }}",
                f"\t\tlocalization_key = {key}",
                "\t}",
            ])
        custom.extend([
            "\ttext = { fallback = yes localization_key = HCA_EMPTY }",
            "}",
            f"hca_age_{number}_striped = {{",
            "\ttype = culture",
        ])
        for culture in sorted(stripe_entries[number - 1]):
            custom.extend([
                "\ttext = {",
                f"\t\ttrigger = {{ this = culture:{culture} }}",
                "\t\tlocalization_key = HCA_STRIPED",
                "\t}",
            ])
        custom.extend([
            "\ttext = { fallback = yes localization_key = HCA_UNSTRIPED }",
            "}",
        ])
    CUSTOM.write_text("\n".join(custom) + "\n", encoding="utf-8-sig")
    LOCALIZATION.write_text("\n".join(localization) + "\n", encoding="utf-8-sig")


def write_age_icons():
    AGE_ICONS.parent.mkdir(parents=True, exist_ok=True)
    icons = []
    for number, age in enumerate(AGES, 1):
        icons.append(f'''texticon = {{
    icon = hca_age_{number}
    iconsize = {{
        texture = "gfx/interface/icons/age/{age}.dds"
        size = {{ 32 32 }}
        offset = {{ 0 5 }}
        fontsize = 20
    }}
}}''')
    AGE_ICONS.write_text("\n\n".join(icons) + "\n", encoding="utf-8-sig")


def compact_gui():
    source = GUI.read_text(encoding="utf-8-sig")
    start, end, _ = find_override(source)
    rows = []
    for number in range(1, 7):
        rows.append(f'''                                            text_multi = {{
                                                layoutpolicy_horizontal = expanding
                                                minimumsize = {{ -1 40 }}
                                                autoresize = yes
                                                margin = {{ 10 4 }}
                                                align = left|nobaseline
                                                visible = "[Not(StringIsEmpty(Culture.Custom('hca_age_{number}_advances')))]"
                                                background = {{
                                                    using = tooltip_table_field_texture
                                                    visible = "[EqualTo_string(Culture.Custom('hca_age_{number}_striped'), Localize('HCA_STRIPED'))]"
                                                }}
                                                text = "[Culture.Custom('hca_age_{number}_advances')]"
                                            }}''')
    replacement = '''blockoverride "culture_list_tooltip_content_extra" {
                                        TooltipListBase = {
                                            blockoverride "block_title" { text = "POSSIBLE_ADVANCES_FOR_FORMABLE" }
                                            vbox = {
                                                ignoreinvisible = yes
                                                layoutpolicy_horizontal = expanding
''' + "\n".join(rows) + '''
                                            }
                                        }
                                    }'''
    GUI.write_text(source[:start] + replacement + source[end:], encoding="utf-8-sig")


if __name__ == "__main__":
    catalogue = read_prototype()
    write_assets(catalogue)
    write_age_icons()
    compact_gui()
    print(f"Compacted {len(catalogue)} cultures into one tooltip widget; "
          f"registered {sum(map(len, catalogue.values()))} advance rows")
