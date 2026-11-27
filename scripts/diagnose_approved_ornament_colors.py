import json
from collections import Counter
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps
import sys

ROOT = Path(".")
sys.path.insert(0, str(ROOT / "src"))
import render_quran_review_previews as renderer

reference_path = ROOT / "references/approved_quran_design.png"
renderer.APPROVED_DESIGN_REFERENCE = reference_path
with Image.open(reference_path) as src:
    reference = ImageOps.fit(src.convert("RGB"), (1080, 1920),
                             method=Image.Resampling.LANCZOS)

samples = [
    ("left_bracket", (138, 448, 270, 665)),
    ("divider", (298, 650, 784, 730)),
]
panels = []
report = {"reference": str(reference_path), "sha256_note": "read from checked-out test branch"}
for name, box in samples:
    original = reference.crop(box)
    extracted = renderer._gold_reference_crop(reference, box)
    original_big = original.resize((original.width * 3, original.height * 3))
    extracted_bg = Image.new("RGB", extracted.size, (30, 36, 44))
    extracted_bg.paste(extracted, mask=extracted.getchannel("A"))
    extracted_big = extracted_bg.resize((extracted.width * 3, extracted.height * 3))
    panel = Image.new("RGB", (original_big.width + extracted_big.width + 48,
                              max(original_big.height, extracted_big.height) + 70),
                      (245, 245, 245))
    panel.paste(original_big, (12, 54))
    panel.paste(extracted_big, (original_big.width + 36, 54))
    d = ImageDraw.Draw(panel)
    d.text((12, 12), f"{name}: source crop", fill=(0, 0, 0))
    d.text((original_big.width + 36, 12), f"{name}: extracted on dark", fill=(0, 0, 0))
    panels.append(panel)
    pixels = [p for p in extracted.getdata() if p[3] > 32]
    report[name] = {
        "source_rgb_top_colors": Counter(original.getdata()).most_common(12),
        "extracted_rgba_top_colors": Counter(pixels).most_common(12),
        "nontransparent_pixels": len(pixels),
        "source_box": box,
    }

width = max(p.width for p in panels)
height = sum(p.height for p in panels) + 20 * (len(panels) + 1)
sheet = Image.new("RGB", (width, height), (225, 225, 225))
y = 20
for panel in panels:
    sheet.paste(panel, (0, y))
    y += panel.height + 20
sheet.save("quran-ornament-color-diagnostic.png")
Path("quran-ornament-color-diagnostic.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2, default=list) + "\n",
    encoding="utf-8"
)
print(json.dumps({"diagnostic_image": "quran-ornament-color-diagnostic.png",
                  "samples": list(report)}, ensure_ascii=False))
