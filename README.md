# Large Settlements Map Mode

An additive, UI-only mod for Europa Universalis V 1.3 that adds **Large Settlements** to the Population map-mode category.

- Rural settlements above 30,000 population are green.
- Towns above 30,000 population are amber.
- Only locations owned by the viewing player's country are highlighted.
- Local RGO markers and raw-material labels are overlaid at close and medium zoom.
- Cities, non-qualifying owned locations, foreign locations, and unowned land are dimmed.
- The comparison is strict: a population of exactly 30,000 is not highlighted.

## Install

Copy this entire folder to:

```text
Documents/Paradox Interactive/Europa Universalis V/mod/large_settlements_map_mode/
```

Then restart the launcher, add **Large Settlements Map Mode** to the active playset, and enable it. In game, open the map-mode selector and look in the **Population** category. You can pin the new mode or assign it a hotkey from the map-mode UI.

The mod is save-safe and changes no gameplay data. It does not replace the vanilla `map_modes.txt`, which keeps compatibility with other additive map-mode mods.

## Development

The icon and launcher thumbnail are original generated assets. Regenerate them with Pillow:

```sh
python3 tools/generate_art.py
```

Run the dependency-free static checks with:

```sh
python3 tools/validate_mod.py
```

EU5 script and localization files must remain UTF-8 with BOM.
