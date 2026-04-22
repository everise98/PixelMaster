"""Generate assets/icon.ico — solid purple #7c3aed background, white P."""
import os
from PIL import Image, ImageDraw, ImageFont

os.makedirs("assets", exist_ok=True)

PURPLE = (124, 58, 237, 255)   # #7c3aed
WHITE  = (255, 255, 255, 255)
SIZES  = [16, 32, 48, 64, 128, 256]


def make_frame(size: int) -> Image.Image:
    img  = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    pad    = max(1, int(size * 0.04))
    radius = int(size * 0.20)

    # Solid purple rounded rectangle
    draw.rounded_rectangle(
        [pad, pad, size - pad - 1, size - pad - 1],
        radius=radius,
        fill=PURPLE,
    )

    # White "P" centred
    font_size = max(int(size * 0.60), 8)
    font = None
    for name in ("segoeuib.ttf", "arialbd.ttf", "arial.ttf"):
        try:
            font = ImageFont.truetype(name, font_size)
            break
        except Exception:
            pass
    if font is None:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), "P", font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (size - tw) / 2 - bbox[0]
    ty = (size - th) / 2 - bbox[1] - size * 0.03

    draw.text((tx, ty), "P", font=font, fill=WHITE)
    return img


frames = [make_frame(s) for s in SIZES]
frames[0].save(
    "assets/icon.ico",
    format="ICO",
    sizes=[(s, s) for s in SIZES],
    append_images=frames[1:],
)
print("icon saved → assets/icon.ico")
