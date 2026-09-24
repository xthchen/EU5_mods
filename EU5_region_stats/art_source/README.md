# Map-mode icon sources

The three `eap_region_*.png` files are flattened 128×128 source composites for
the runtime DDS icons.

Each composite uses `vanilla_map_modes/region.png` as the full-size base. The
matching statistic icon is resized to 66×66 pixels and placed at `(60, 60)`:

- `population.png` → `eap_region_population.png`
- `location_wealth.png` → `eap_region_wealth.png`
- `development.png` → `eap_region_development.png`

The inputs are the vanilla EU5 map-mode artwork published on the Europa
Universalis V Wiki. Location Wealth uses the `potential_tax_base` map-mode
asset. Runtime files are 128×128 DXT5 DDS textures with eight mip levels.

`workshop_thumbnail.svg` is the editable 512×512 source for the workshop
thumbnail. It uses the vanilla Region artwork as its centerpiece and places a
high-contrast `STATS` plate in the lower-right corner. Its rendered PNG is
stored at `.metadata/thumbnail.png`.
