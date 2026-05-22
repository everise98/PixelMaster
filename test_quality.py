"""
Quality comparison test — runs all upscaling methods on Hwajilguji.png
Outputs: test_results/ folder with each method saved side-by-side
"""
import os, time
import cv2
import numpy as np
from PIL import Image

SRC = r"C:\Users\AWEARLAB\Desktop\Hwajilguji.png"
OUT = r"C:\Users\AWEARLAB\Desktop\test_results"
SCALE = 4
os.makedirs(OUT, exist_ok=True)

img_pil = Image.open(SRC).convert("RGB")
print(f"Source: {img_pil.size[0]}x{img_pil.size[1]}")


# ── helper ────────────────────────────────────────────────────────────────────
def save(arr_or_pil, name):
    path = os.path.join(OUT, f"{name}.png")
    if isinstance(arr_or_pil, np.ndarray):
        Image.fromarray(cv2.cvtColor(arr_or_pil, cv2.COLOR_BGR2RGB)).save(path)
    else:
        arr_or_pil.save(path)
    print(f"  saved: {name}.png")
    return path


def bgr(pil_img):
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)


def pil(bgr_img):
    return Image.fromarray(cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB))


def luminance_sharpen(img, radius, strength):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    l = lab[:, :, 0]
    blur = cv2.GaussianBlur(l, (0, 0), radius)
    lab[:, :, 0] = np.clip(l + strength * (l - blur), 0, 255)
    return cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2BGR)


def clahe_lum(img, clip):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    return cv2.cvtColor(
        cv2.merge([cv2.createCLAHE(clipLimit=clip, tileGridSize=(8,8)).apply(l), a, b]),
        cv2.COLOR_LAB2BGR
    )


src = bgr(img_pil)
h, w = src.shape[:2]
new_w, new_h = w * SCALE, h * SCALE


# ── Method 1: Lanczos (current) ───────────────────────────────────────────────
t0 = time.time()
m1 = cv2.resize(src, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
m1 = luminance_sharpen(m1, 0.9, 0.28)
print(f"[1] Lanczos          {time.time()-t0:.1f}s")
save(m1, "1_lanczos")


# ── Method 2: HD Enhance (current) ───────────────────────────────────────────
t0 = time.time()
m2 = cv2.bilateralFilter(src, d=5, sigmaColor=20, sigmaSpace=20)
m2 = cv2.resize(m2, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
m2 = luminance_sharpen(m2, 1.2, 0.38)
m2 = clahe_lum(m2, 1.2)
print(f"[2] HD Enhance       {time.time()-t0:.1f}s")
save(m2, "2_hd_enhance")


# ── Method 3: Bicubic ─────────────────────────────────────────────────────────
t0 = time.time()
m3 = cv2.resize(src, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
print(f"[3] Bicubic          {time.time()-t0:.1f}s")
save(m3, "3_bicubic")


# ── Method 4: Lanczos + stronger multi-scale sharpen ─────────────────────────
t0 = time.time()
m4 = cv2.resize(src, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
lab = cv2.cvtColor(m4, cv2.COLOR_BGR2LAB).astype(np.float32)
l = lab[:, :, 0]
fine   = cv2.GaussianBlur(l, (0,0), 0.8)
medium = cv2.GaussianBlur(l, (0,0), 2.0)
l = np.clip(l + 0.35*(l - fine) + 0.20*(l - medium), 0, 255)
lab[:, :, 0] = l
m4 = cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2BGR)
m4 = clahe_lum(m4, 1.5)
print(f"[4] Multi-scale      {time.time()-t0:.1f}s")
save(m4, "4_multiscale")


# ── torchvision compat patch (functional_tensor removed in 0.16+) ─────────────
try:
    import torchvision.transforms.functional_tensor
except ImportError:
    import types, sys, torchvision.transforms.functional as _F
    _mod = types.ModuleType("torchvision.transforms.functional_tensor")
    for _a in dir(_F):
        setattr(_mod, _a, getattr(_F, _a))
    sys.modules["torchvision.transforms.functional_tensor"] = _mod


# ── Method 5: Real-ESRGAN ────────────────────────────────────────────────────
try:
    import torch
    from realesrgan import RealESRGANer
    from basicsr.archs.rrdbnet_arch import RRDBNet

    model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64,
                    num_block=23, num_grow_ch=32, scale=4)
    upsampler = RealESRGANer(
        scale=4,
        model_path="https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth",
        model=model,
        tile=256, tile_pad=10, pre_pad=0,
        half=False,
        device=torch.device("cpu"),
    )
    t0 = time.time()
    out_bgr, _ = upsampler.enhance(src, outscale=4)
    print(f"[5] Real-ESRGAN      {time.time()-t0:.1f}s")
    save(out_bgr, "5_realesrgan")
except Exception as e:
    print(f"[5] Real-ESRGAN FAILED: {e}")


# ── Method 6: Real-ESRGAN General (v3) ───────────────────────────────────────
try:
    from realesrgan.archs.srvgg_arch import SRVGGNetCompact
    model6 = SRVGGNetCompact(num_in_ch=3, num_out_ch=3, num_feat=64,
                              num_conv=32, upscale=4, act_type='prelu')
    upsampler6 = RealESRGANer(
        scale=4,
        model_path="https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-general-x4v3.pth",
        model=model6,
        tile=256, tile_pad=10, pre_pad=0,
        half=False,
        device=torch.device("cpu"),
    )
    t0 = time.time()
    out6, _ = upsampler6.enhance(src, outscale=4)
    print(f"[6] ESRGAN-General   {time.time()-t0:.1f}s")
    save(out6, "6_realesrgan_general")
except Exception as e:
    print(f"[6] ESRGAN-General FAILED: {e}")


# ── composite comparison ──────────────────────────────────────────────────────
results = {}
for fname in sorted(os.listdir(OUT)):
    if fname.endswith('.png') and fname != 'comparison.png':
        results[fname] = Image.open(os.path.join(OUT, fname))

if results:
    rw, rh = list(results.values())[0].size
    cols = len(results)
    label_h = 30
    comp = Image.new("RGB", (rw * cols, rh + label_h), (20, 20, 30))
    from PIL import ImageDraw, ImageFont
    d = ImageDraw.Draw(comp)
    for i, (name, img) in enumerate(results.items()):
        comp.paste(img.convert("RGB"), (i * rw, label_h))
        d.text((i * rw + 6, 6), name.replace('.png',''), fill=(200,200,200))
    comp.save(os.path.join(OUT, "comparison.png"))
    print(f"\nComparison saved → {OUT}\\comparison.png")

print("\nDone. Open test_results folder on Desktop.")
import subprocess
subprocess.Popen(["explorer", OUT])
