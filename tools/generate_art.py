#!/usr/bin/env python3
"""Generate the original DDS map-mode icon and launcher thumbnail."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "tools/assets"
SCALE = 4


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def build_icon() -> Image.Image:
    size = 128 * SCALE
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Circular cartographic badge.
    draw.ellipse((18, 18, size - 18, size - 18), fill=(17, 31, 43, 255), outline=(238, 191, 76, 255), width=18)
    draw.arc((42, 42, size - 42, size - 42), 196, 340, fill=(66, 108, 126, 255), width=8)
    draw.arc((42, 42, size - 42, size - 42), 20, 164, fill=(66, 108, 126, 255), width=8)

    # Use EU5's canonical location-rank symbols rather than custom buildings.
    rank_icon_size = 168
    rural_icon = Image.open(ASSETS / "rural_settlement.png").convert("RGBA")
    town_icon = Image.open(ASSETS / "town.png").convert("RGBA")
    rural_icon = rural_icon.resize((rank_icon_size, rank_icon_size), Image.Resampling.LANCZOS)
    town_icon = town_icon.resize((rank_icon_size, rank_icon_size), Image.Resampling.LANCZOS)
    image.alpha_composite(rural_icon, (84, 206))
    image.alpha_composite(town_icon, (260, 206))

    # Threshold ribbon.
    draw.rounded_rectangle((106, 390, 406, 466), radius=28, fill=(238, 241, 238, 255), outline=(17, 31, 43, 255), width=8)
    label_font = font(50, bold=True)
    label = "30K+"
    box = draw.textbbox((0, 0), label, font=label_font)
    draw.text(((size - (box[2] - box[0])) / 2, 396), label, font=label_font, fill=(17, 31, 43, 255))

    return image.resize((128, 128), Image.Resampling.LANCZOS)


def build_thumbnail(icon: Image.Image) -> Image.Image:
    image = Image.new("RGB", (512, 512), (12, 24, 34))
    draw = ImageDraw.Draw(image)
    icon_large = icon.resize((300, 300), Image.Resampling.LANCZOS)
    image.paste(icon_large, (106, 32), icon_large)

    title_font = font(42, bold=True)
    subtitle_font = font(24)
    title = "POTENTIAL CITIES"
    subtitle = "MAP MODE  •  30,000+"
    for text, y, face, color in [
        (title, 344, title_font, (245, 239, 220)),
        (subtitle, 410, subtitle_font, (119, 207, 181)),
    ]:
        box = draw.textbbox((0, 0), text, font=face)
        draw.text(((512 - (box[2] - box[0])) / 2, y), text, font=face, fill=color)
    return image


def main() -> None:
    icon = build_icon()
    icon_path = ROOT / "main_menu/gfx/interface/icons/map_modes/large_settlements.dds"
    icon.save(icon_path)

    thumbnail = build_thumbnail(icon)
    thumbnail.save(ROOT / ".metadata/thumbnail.png", optimize=True)


if __name__ == "__main__":
    main()
