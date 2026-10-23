"""Create technical reference sheets from installed TFR icons and saved photos.

No artwork is generated or restyled. The sheets are research inputs for imagegen.
Run with the bundled Pillow-enabled Python; the parent path can be overridden.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "docs/artwork/ideology"
DEFAULT_PARENT = Path(r"C:\Program Files (x86)\Steam\steamapps\workshop\content\394360\3350890356")
STYLE_FILES = [
    "conservative_baltic.png", "market_liberal_baltic.png", "social_liberal_baltic.png",
    "christian_democracy.png", "neoliberalism.png", "centrist.png",
    "social_democracy_ARG.png", "social_democracy_TUR.png", "social_democrat_group.png",
    "ultra_conservatism_ENG.png", "neoliberalism_UKR.png", "christian_conservatism.png",
]
LEADERS = [
    "mart_helme", "martin_helme", "juri_ratas", "tanel_kiik", "mihhail_kolvart",
    "helir_valdor_seeder", "urmas_reinsalu", "kaja_kallas", "kristen_michal",
    "indrek_saar", "lauri_laanemets", "kristina_kallas", "margus_tsahkna", "lavly_perling",
]


def font(size: int):
    for path in (Path("C:/Windows/Fonts/arial.ttf"), Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")):
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def centered(draw, xy, label, size=19, fill=(235, 237, 242)):
    draw.text(xy, label, font=font(size), fill=fill, anchor="mt")


def style_sheet(parent: Path):
    out = ART / "references"
    out.mkdir(parents=True, exist_ok=True)
    columns, cell_w, cell_h, top = 4, 270, 316, 60
    sheet = Image.new("RGB", (columns * cell_w, ((len(STYLE_FILES) + columns - 1) // columns) * cell_h + top), (31, 34, 42))
    draw = ImageDraw.Draw(sheet)
    centered(draw, (sheet.width // 2, 12), "TFR ideology references: 3x nearest-neighbor and native size", 23)
    report = []
    for i, name in enumerate(STYLE_FILES):
        path = parent / "gfx/interface/ideologies" / name
        with Image.open(path) as raw:
            im = raw.convert("RGBA")
        x, y = (i % columns) * cell_w, top + (i // columns) * cell_h
        enlarged = im.resize((im.width * 3, im.height * 3), Image.Resampling.NEAREST)
        sheet.paste(enlarged, (x + (cell_w - enlarged.width) // 2, y), enlarged)
        sheet.paste(im, (x + (cell_w - im.width) // 2, y + 210), im)
        label = name.removesuffix(".png")
        if len(label) > 24:
            label = label.replace("_", "\n", 1)
        centered(draw, (x + cell_w // 2, y + 280), label, 16)
        report.append({"texture": f"gfx/interface/ideologies/{name}", "width": im.width, "height": im.height, "mode": im.mode})
    sheet.save(out / "tfr_ideology_style_sheet.png")
    (out / "tfr_ideology_dimensions.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def leader_sheets():
    out = ART / "references"
    sources = {r["person"]: r for r in json.loads((ROOT / "docs/artwork/ministers/sources.json").read_text(encoding="utf-8-sig"))}
    labels = {person: sources[person]["name"] for person in LEADERS}
    for group, members in (("a", LEADERS[:7]), ("b", LEADERS[7:])):
        columns, cell_w, cell_h, top = 4, 300, 378, 56
        sheet = Image.new("RGB", (columns * cell_w, 2 * cell_h + top), (31, 34, 42))
        draw = ImageDraw.Draw(sheet)
        centered(draw, (sheet.width // 2, 12), f"Estonia party leader likeness references {group.upper()}", 23)
        for i, person in enumerate(members):
            entry = sources[person]
            with Image.open(ROOT / entry["reference_path"]) as raw:
                im = ImageOps.exif_transpose(raw).convert("RGB")
            # Fit the full photo. No portrait crop or creative edits.
            im.thumbnail((280, 325), Image.Resampling.LANCZOS)
            x, y = (i % columns) * cell_w, top + (i // columns) * cell_h
            sheet.paste(im, (x + (cell_w - im.width) // 2, y))
            centered(draw, (x + cell_w // 2, y + 333), labels[person], 20)
        sheet.save(out / f"estonia_party_leaders_{group}.jpg", quality=95)
    used = {entry["person"] for entry in json.loads((ART / "manifest.json").read_text(encoding="utf-8-sig"))["icons"]}
    records = [{k: sources[p].get(k) for k in ("person", "name", "reference_path", "source_page_url", "direct_image_url", "author", "license", "license_url", "date")} for p in LEADERS if p in used]
    (ART / "leader_reference_sources.json").write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent", type=Path, default=DEFAULT_PARENT)
    args = parser.parse_args()
    style_sheet(args.parent)
    leader_sheets()
    print("Prepared TFR style and leader likeness reference sheets in docs/artwork/ideology/references/.")


if __name__ == "__main__":
    main()
