"""Technically export saved imagegen ideology masters to TFR's 66x68 PNG size.

Only transparent-margin trimming, proportional resizing and transparent padding
are performed. The portrait, symbols, colors and composition remain generated
artwork. Run --check to verify existing runtime exports without writing.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "docs/artwork/ideology"
MANIFEST = ART / "manifest.json"
SIZE = (66, 68)


def load_manifest():
    data = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
    return data["icons"]


def export_image(path: Path) -> Image.Image:
    with Image.open(path) as source:
        source = source.convert("RGBA")
        alpha = source.getchannel("A")
        bbox = alpha.getbbox()
        if bbox is None:
            raise ValueError(f"Empty master: {path.relative_to(ROOT)}")
        if alpha.getextrema()[0] == 255:
            raise ValueError(f"Master has no transparent background: {path.relative_to(ROOT)}")
        # Trimming the transparent outer canvas changes no visible artwork.
        trimmed = source.crop(bbox)
        available = (SIZE[0] - 2, SIZE[1] - 2)
        factor = min(available[0] / trimmed.width, available[1] / trimmed.height)
        target = (max(1, round(trimmed.width * factor)), max(1, round(trimmed.height * factor)))
        resized = trimmed.resize(target, Image.Resampling.LANCZOS)
        result = Image.new("RGBA", SIZE, (0, 0, 0, 0))
        result.paste(resized, ((SIZE[0] - target[0]) // 2, (SIZE[1] - target[1]) // 2))
        return result


def check_image(path: Path, expected: Image.Image):
    with Image.open(path) as raw:
        if raw.size != SIZE or raw.mode != "RGBA":
            raise ValueError(f"Expected 66x68 RGBA: {path.relative_to(ROOT)}")
        im = raw.convert("RGBA")
        if im.tobytes() != expected.tobytes():
            raise ValueError(f"Export is stale: {path.relative_to(ROOT)}")
        if any(im.getpixel(corner)[3] for corner in ((0, 0), (65, 0), (0, 67), (65, 67))):
            raise ValueError(f"Nontransparent outside corner: {path.relative_to(ROOT)}")
        alpha = im.getchannel("A")
        if alpha.getbbox() is None or alpha.getextrema()[1] < 250:
            raise ValueError(f"Missing artwork: {path.relative_to(ROOT)}")


def get_font(size):
    for candidate in (Path("C:/Windows/Fonts/arial.ttf"), Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")):
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def contact_sheet(records, scale):
    columns, cell_width, top = 4, max(244, SIZE[0] * scale + 34), 50
    cell_height = SIZE[1] * scale + 70
    rows = (len(records) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * cell_width, top + rows * cell_height), (31, 34, 42))
    draw = ImageDraw.Draw(sheet)
    draw.text((20, 12), f"TFR Estonia party ideology icons - {scale}x game size", font=get_font(22), fill=(240, 241, 245))
    for index, entry in enumerate(records):
        x, y = (index % columns) * cell_width, top + (index // columns) * cell_height
        with Image.open(ROOT / entry["icon"]) as raw:
            im = raw.convert("RGBA")
        enlarged = im.resize((SIZE[0] * scale, SIZE[1] * scale), Image.Resampling.NEAREST)
        sheet.paste(enlarged, (x + (cell_width - enlarged.width) // 2, y), enlarged)
        draw.text((x + cell_width // 2, y + SIZE[1] * scale + 8), entry["party"], font=get_font(18), fill=(240, 241, 245), anchor="mt")
        draw.text((x + cell_width // 2, y + SIZE[1] * scale + 32), entry["leader"], font=get_font(16), fill=(194, 200, 214), anchor="mt")
    sheet.save(ART / f"contact_sheet_{scale}x.png")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    records = load_manifest()
    seen = set()
    for entry in records:
        if entry["id"] in seen:
            raise ValueError(f"Duplicate icon ID: {entry['id']}")
        seen.add(entry["id"])
        expected = export_image(ROOT / entry["master"])
        path = ROOT / entry["icon"]
        if not args.check:
            path.parent.mkdir(parents=True, exist_ok=True)
            expected.save(path, format="PNG", optimize=True)
        check_image(path, expected)
    if not args.check:
        for scale in (1, 4):
            contact_sheet(records, scale)
    print(f"Verified {len(records)} 66x68 RGBA ideology icons against their imagegen masters.")


if __name__ == "__main__":
    main()
