from PIL import Image
import numpy as np
import cv2
import os
import sys

SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png"}

METHODS = {
    "multiscale":      "Multi-scale  (Recommended)",
    "lanczos":         "Lanczos",
    "hd_enhance":      "HD Enhance",
    "bicubic":         "Bicubic (Smooth)",
    "realesrgan_plus": "Real-ESRGAN Plus  (AI)",
    "realesrgan_gen":  "Real-ESRGAN General  (AI)",
}

# ONNX model file names (bundled inside the exe via assets/models/)
_ONNX_FILES = {
    "realesrgan_plus": "RealESRGAN_x4plus.onnx",
    "realesrgan_gen":  "realesr-general-x4v3.onnx",
}


def _models_dir() -> str:
    """Returns the models directory — works both from source and frozen exe."""
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    return os.path.join(base, "assets", "models")


# ── colour-safe helpers ───────────────────────────────────────────────────────

def _luminance_sharpen(img_bgr: np.ndarray, radius: float, strength: float) -> np.ndarray:
    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    l = lab[:, :, 0]
    blur = cv2.GaussianBlur(l, (0, 0), radius)
    lab[:, :, 0] = np.clip(l + strength * (l - blur), 0, 255)
    return cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2BGR)


def _clahe_luminance(img_bgr: np.ndarray, clip: float) -> np.ndarray:
    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clip, tileGridSize=(8, 8))
    return cv2.cvtColor(cv2.merge([clahe.apply(l), a, b]), cv2.COLOR_LAB2BGR)


def _bilateral_denoise(img_bgr: np.ndarray, d: int, sc: float, ss: float) -> np.ndarray:
    return cv2.bilateralFilter(img_bgr, d=d, sigmaColor=sc, sigmaSpace=ss)


def _multi_scale_sharpen(img_bgr: np.ndarray) -> np.ndarray:
    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    l = lab[:, :, 0]
    fine   = cv2.GaussianBlur(l, (0, 0), 0.8)
    medium = cv2.GaussianBlur(l, (0, 0), 2.0)
    l = np.clip(l + 0.35 * (l - fine), 0, 255)
    l = np.clip(l + 0.20 * (l - medium), 0, 255)
    lab[:, :, 0] = l
    return cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2BGR)


# ── multi-pass resize ─────────────────────────────────────────────────────────

def _resize_multipass(img: np.ndarray, scale: int, interp: int) -> np.ndarray:
    h, w = img.shape[:2]
    if scale == 8:
        mid = cv2.resize(img, (w * 4, h * 4), interpolation=interp)
        return cv2.resize(mid, (w * 8, h * 8), interpolation=interp)
    elif scale == 16:
        mid = cv2.resize(img, (w * 4, h * 4), interpolation=interp)
        return cv2.resize(mid, (w * 16, h * 16), interpolation=interp)
    return cv2.resize(img, (w * scale, h * scale), interpolation=interp)


# ── PIL ↔ cv2 ─────────────────────────────────────────────────────────────────

def _pil_to_cv2(img: Image.Image):
    arr = np.array(img)
    if img.mode == "RGB":
        return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR), False
    elif img.mode == "RGBA":
        return cv2.cvtColor(arr, cv2.COLOR_RGBA2BGRA), True
    return cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR), False


def _cv2_to_pil(arr: np.ndarray, has_alpha: bool) -> Image.Image:
    if has_alpha:
        return Image.fromarray(cv2.cvtColor(arr, cv2.COLOR_BGRA2RGBA))
    return Image.fromarray(cv2.cvtColor(arr, cv2.COLOR_BGR2RGB))


# ── ONNX Real-ESRGAN ──────────────────────────────────────────────────────────

def _run_onnx_esrgan(img_bgr: np.ndarray, model_key: str, scale: int) -> np.ndarray:
    import onnxruntime as ort

    model_path = os.path.join(_models_dir(), _ONNX_FILES[model_key])
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found: {model_path}")

    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
    inp = np.transpose(img_rgb, (2, 0, 1))[np.newaxis]

    sess = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
    out = sess.run(None, {sess.get_inputs()[0].name: inp})[0]
    out = np.clip(out[0].transpose(1, 2, 0) * 255, 0, 255).astype(np.uint8)
    result = cv2.cvtColor(out, cv2.COLOR_RGB2BGR)

    # Model always outputs 4×; resize if a different scale was requested
    if scale != 4:
        h, w = result.shape[:2]
        factor = scale / 4
        result = cv2.resize(result, (int(w * factor), int(h * factor)),
                            interpolation=cv2.INTER_LANCZOS4)
    return result


# ── main entry point ──────────────────────────────────────────────────────────

def upscale_image(
    input_path: str,
    output_path: str,
    scale: int = 4,
    method: str = "multiscale",
    jpeg_quality: int = 95,
) -> tuple[bool, str]:
    try:
        pil_img = Image.open(input_path)
        has_alpha = pil_img.mode in ("RGBA", "LA", "PA") or (
            pil_img.mode == "P" and "transparency" in pil_img.info
        )
        pil_img = pil_img.convert("RGBA" if has_alpha else "RGB")
        img_cv, has_alpha = _pil_to_cv2(pil_img)

        # ── algorithms ───────────────────────────────────────────────────────
        if method == "multiscale":
            out = _resize_multipass(img_cv, scale, cv2.INTER_LANCZOS4)
            if not has_alpha:
                out = _multi_scale_sharpen(out)
                out = _clahe_luminance(out, clip=1.5)

        elif method == "lanczos":
            out = _resize_multipass(img_cv, scale, cv2.INTER_LANCZOS4)
            if not has_alpha:
                out = _luminance_sharpen(out, radius=0.9, strength=0.28)

        elif method == "hd_enhance":
            src = _bilateral_denoise(img_cv, d=5, sc=20, ss=20) if not has_alpha else img_cv
            out = _resize_multipass(src, scale, cv2.INTER_LANCZOS4)
            if not has_alpha:
                out = _luminance_sharpen(out, radius=1.2, strength=0.38)
                out = _clahe_luminance(out, clip=1.2)

        elif method == "bicubic":
            out = _resize_multipass(img_cv, scale, cv2.INTER_CUBIC)

        elif method in ("realesrgan_plus", "realesrgan_gen"):
            src = cv2.cvtColor(np.array(pil_img.convert("RGB")), cv2.COLOR_RGB2BGR)
            out = _run_onnx_esrgan(src, method, scale)
            has_alpha = False

        else:
            out = _resize_multipass(img_cv, scale, cv2.INTER_LANCZOS4)

        result = _cv2_to_pil(out, has_alpha)

        # ── save ─────────────────────────────────────────────────────────────
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        ext = os.path.splitext(output_path)[1].lower()
        if ext in (".jpg", ".jpeg"):
            if result.mode == "RGBA":
                result = result.convert("RGB")
            result.save(output_path, "JPEG", quality=jpeg_quality, optimize=True)
        else:
            result.save(output_path, "PNG", optimize=True)

        return True, output_path

    except Exception as exc:
        return False, str(exc)


def get_image_info(path: str) -> tuple[int, int, str]:
    with Image.open(path) as img:
        return img.width, img.height, img.mode
