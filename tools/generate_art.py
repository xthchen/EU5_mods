#!/usr/bin/env python3
"""Generate the original DDS map-mode icon and launcher thumbnail."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
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

    # Rural house, colored like the rural-settlement map overlay.
    rural = (44, 210, 145, 255)
    draw.polygon([(92, 292), (180, 208), (268, 292)], fill=rural)
    draw.rounded_rectangle((116, 282, 244, 386), radius=8, fill=rural)
    draw.rectangle((170, 326, 202, 386), fill=(17, 31, 43, 255))

    # Town skyline, colored like the town map overlay.
    town = (255, 184, 56, 255)
    draw.rectangle((270, 236, 320, 386), fill=town)
    draw.rectangle((326, 188, 382, 386), fill=town)
    draw.rectangle((388, 264, 430, 386), fill=town)
    draw.polygon([(326, 188), (354, 142), (382, 188)], fill=town)
    for x, y in [(284, 270), (284, 316), (342, 228), (342, 278), (400, 298), (400, 338)]:
        draw.rectangle((x, y, x + 18, y + 22), fill=(17, 31, 43, 255))

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
    title = "LARGE SETTLEMENTS"
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
