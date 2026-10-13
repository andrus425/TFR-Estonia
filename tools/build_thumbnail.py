"""Rebuild the original geometric Estonia development-build thumbnail.

Requires Pillow. The artwork contains drawn geometry and Pillow's bundled font;
no photographs, portraits, or parent-mod artwork are included.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]


def main():
    image = Image.new("RGB", (1200, 800), "#101923")
    draw = ImageDraw.Draw(image)
    # Original layout with Estonia's three horizontal national-color bands.
    draw.rectangle((0, 0, 1199, 159), fill="#4891D9")
    draw.rectangle((0, 160, 1199, 319), fill="#080B10")
    draw.rectangle((0, 320, 1199, 479), fill="#FFFFFF")
    draw.rectangle((65, 542, 75, 724), fill="#4891D9")
    draw.text((108, 535), "TFR ESTONIA", fill="#FFFFFF", font=ImageFont.load_default(size=76))
    draw.text((113, 630), "A COUNTRY EXPANSION FOR THE FIRE RISES", fill="#BFCFE0", font=ImageFont.load_default(size=25))
    draw.rounded_rectangle((110, 692, 490, 748), radius=8, fill="#243F5D")
    draw.text((131, 702), "DEVELOPMENT BUILD", fill="#FFFFFF", font=ImageFont.load_default(size=29))
    image.save(ROOT / "thumbnail.png", optimize=True)
    print("Created thumbnail.png from original geometric artwork.")


if __name__ == "__main__":
    main()
