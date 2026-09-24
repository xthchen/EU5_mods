"""Compose unchanged EU5 Culture, Religion, and Advances icons."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


MOD = Path(__file__).resolve().parents[1]
GAME_ICONS = Path(
    "/Volumes/KEYCHAIN/Europa Universalis V/game/main_menu/gfx/interface/icons"
)
SOURCE = MOD / "art_source/show_cultural_religious_advances_workshop_source.png"
THUMBNAIL = MOD / ".metadata/thumbnail.png"
TITLE_FONT = Path("/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf")


def game_icon(path: Path, size: tuple[int, int]) -> Image.Image:
    icon = Image.open(path).convert("RGBA")
    icon = icon.crop(icon.getchannel("A").getbbox())
    return icon.resize(size, Image.Resampling.LANCZOS)


canvas = Image.open(SOURCE).convert("RGB")
if canvas.size != (1254, 1254):
    raise ValueError(f"Unexpected source size: {canvas.size}")

# Clear the old symbols and lettering without touching the existing gold trim.
draw = ImageDraw.Draw(canvas)
draw.rectangle((47, 48, 1206, 811), fill="black")
draw.rectangle((135, 866, 1118, 1103), fill="black")

culture = game_icon(GAME_ICONS / "flat_icons/culture/culture.dds", (505, 386))
religion = game_icon(GAME_ICONS / "location_icons/main_religion.dds", (350, 350))
advances = game_icon(GAME_ICONS / "map_modes/advances.dds", (450, 555))
canvas.paste(religion, (452, 95), religion)
canvas.paste(culture, (74, 344), culture)
canvas.paste(advances, (748, 245), advances)

titles = ("SHOW CULTURAL AND", "RELIGIOUS ADVANCES")
font_size = 86
while font_size > 60:
    font = ImageFont.truetype(str(TITLE_FONT), font_size)
    if max(draw.textbbox((0, 0), title, font=font)[2] for title in titles) <= 965:
        break
    font_size -= 1
for title, middle in zip(titles, (935, 1035)):
    draw.text(
        (627, middle), title, font=font, anchor="mm",
        fill=(255, 250, 232), stroke_width=2, stroke_fill=(177, 128, 55),
    )

canvas.save(SOURCE)
canvas.resize((512, 512), Image.Resampling.LANCZOS).save(THUMBNAIL)
