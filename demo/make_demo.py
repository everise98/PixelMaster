"""
PixelMaster demo recorder.
Records live screen + annotates with zoom/caption in post-processing.
Run from PixelRevive root:  venv/Scripts/python demo/make_demo.py
"""
import sys, os, time, math, threading, subprocess
sys.stdout.reconfigure(encoding='utf-8')

import cv2
import numpy as np
import pyautogui
import pygetwindow as gw
from PIL import ImageGrab, Image, ImageDraw, ImageFont

pyautogui.FAILSAFE = False
pyautogui.PAUSE    = 0.0

# ── Config ────────────────────────────────────────────────────────────────────
FPS      = 24
WIN_W    = 1100
WIN_H    = 740
WIN_X    = 80
WIN_Y    = 40
OUT_PATH = os.path.join(os.path.dirname(__file__), 'PixelMaster_demo.mp4')
SET5     = os.path.join(os.path.dirname(__file__), 'set5')
VENV_PY  = os.path.join(os.path.dirname(__file__), '..', 'venv', 'Scripts', 'python.exe')
APP_PY   = os.path.join(os.path.dirname(__file__), '..', 'main.py')

WIN_BBOX = (WIN_X, WIN_Y, WIN_X + WIN_W, WIN_Y + WIN_H)

# ── Shared state ──────────────────────────────────────────────────────────────
raw_frames  = []   # list of (timestamp, np.ndarray RGB)
click_log   = []   # list of (timestamp, wx, wy, caption, sub)  — window-relative coords
caption_log = []   # list of (timestamp, duration, caption, sub)
stop_flag   = threading.Event()


# ── Capture thread ────────────────────────────────────────────────────────────
def _capture():
    while not stop_flag.is_set():
        t0 = time.perf_counter()
        img = ImageGrab.grab(bbox=WIN_BBOX)
        raw_frames.append((t0, np.array(img.convert('RGB'))))
        elapsed = time.perf_counter() - t0
        time.sleep(max(0, 1/FPS - elapsed))


# ── Action helpers ────────────────────────────────────────────────────────────
def now():
    return time.perf_counter()


def move_click(wx, wy, caption='', sub='', zoom=True, double=False):
    """Click at window-relative (wx, wy), log for post-processing."""
    ax, ay = WIN_X + wx, WIN_Y + wy
    pyautogui.moveTo(ax, ay, duration=0.3)
    time.sleep(0.08)
    t = now()
    if zoom:
        click_log.append((t, wx, wy, caption, sub))
    if double:
        pyautogui.doubleClick()
    else:
        pyautogui.click()
    time.sleep(0.12)


def caption_hold(duration, caption, sub=''):
    """Log a caption to appear for given duration."""
    caption_log.append((now(), duration, caption, sub))
    time.sleep(duration)


def open_file_dialog(path):
    """Type a file path into an open-file dialog and confirm."""
    time.sleep(0.7)
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.05)
    pyautogui.typewrite(path.replace('\\', '/'), interval=0.015)
    time.sleep(0.2)
    pyautogui.press('enter')
    time.sleep(1.0)


def wait_window(substr, timeout=25):
    t0 = time.time()
    while time.time() - t0 < timeout:
        for w in gw.getAllWindows():
            if substr.lower() in w.title.lower():
                return w
        time.sleep(0.25)
    return None


# ── Post-processing ───────────────────────────────────────────────────────────
def load_fonts():
    try:
        return (ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 18),
                ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',  12))
    except:
        f = ImageFont.load_default()
        return f, f


def apply_caption(arr, caption, sub, alpha=1.0, font_b=None, font_s=None):
    h, w = arr.shape[:2]
    img = Image.fromarray(arr)
    overlay = Image.new('RGBA', (w, 52), (20, 40, 24, int(210 * alpha)))
    img.paste(Image.fromarray(np.array(overlay)[:, :, :3]),
              (0, h - 52),
              mask=Image.fromarray(np.full((52, w), int(210 * alpha), dtype=np.uint8)))
    draw = ImageDraw.Draw(img)
    draw.text((16, h - 52 + 8),  caption, fill=(147, 241, 165), font=font_b)
    if sub:
        draw.text((16, h - 52 + 30), sub,  fill=(180, 210, 185), font=font_s)
    return np.array(img.convert('RGB'))


def zoom_overlay(base, cx, cy, peak=2.0, radius=110):
    """Return base frame with a circular zoom lens at (cx, cy)."""
    h, w = base.shape[:2]
    cx = max(radius, min(w - radius, cx))
    cy = max(radius, min(h - radius, cy))

    hw = max(1, int(radius / peak))
    hh = max(1, int(radius / peak))
    x1, x2 = max(0, cx - hw), min(w, cx + hw)
    y1, y2 = max(0, cy - hh), min(h, cy + hh)
    crop = base[y1:y2, x1:x2]
    if crop.size == 0:
        return base.copy()
    zoomed = cv2.resize(crop, (radius * 2, radius * 2), interpolation=cv2.INTER_LINEAR)

    out = base.copy()
    # feathered circle mask
    mask = np.zeros((h, w), dtype=np.float32)
    cv2.circle(mask, (cx, cy), radius, 1.0, -1)
    mask = cv2.GaussianBlur(mask, (31, 31), 0)

    zpad = np.zeros_like(base)
    zpad[cy-radius:cy+radius, cx-radius:cx+radius] = zoomed
    m3 = mask[:, :, None]
    out = (base * (1 - m3) + zpad * m3).clip(0, 255).astype(np.uint8)

    # ring border
    cv2.circle(out, (cx, cy), radius, (147, 241, 165), 2)
    return out


def build_video(raw_frames, click_log, caption_log):
    if not raw_frames:
        print("No frames!"); return

    font_b, font_s = load_fonts()

    h, w = raw_frames[0][1].shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(OUT_PATH, fourcc, FPS, (w, h))

    t_start = raw_frames[0][0]

    # Build per-frame timestamp index
    ts = [f[0] - t_start for f, _ in [(r, 0) for r in raw_frames]]  # fix
    ts = [r[0] - t_start for r in raw_frames]

    print(f"Post-processing {len(raw_frames)} frames ({len(raw_frames)/FPS:.1f}s)...")

    for i, (t_abs, frame) in enumerate(raw_frames):
        t = t_abs - t_start
        out = frame.copy()

        # ── zoom at click events ──────────────────────────────────────────
        for (tc, wx, wy, cap, sub) in click_log:
            tc_rel = tc - t_start
            dt = abs(t - tc_rel)
            if dt < 0.55:
                ease = math.sin(min(dt / 0.55, 1.0) * math.pi)
                if ease > 0.05:
                    peak = 1.0 + 1.6 * ease
                    out = zoom_overlay(out, wx, wy, peak=peak, radius=115)

        # ── caption overlay ───────────────────────────────────────────────
        active_cap = ''
        active_sub = ''
        for (tc, dur, cap, sub) in caption_log:
            tc_rel = tc - t_start
            if tc_rel <= t <= tc_rel + dur:
                # fade in/out
                dt_in  = t - tc_rel
                dt_out = (tc_rel + dur) - t
                alpha  = min(dt_in / 0.3, dt_out / 0.3, 1.0)
                active_cap = cap
                active_sub = sub
                out = apply_caption(out, cap, sub, alpha=alpha,
                                    font_b=font_b, font_s=font_s)
                break

        # ── cursor dot ───────────────────────────────────────────────────
        mx, my = pyautogui.position()
        cx_cur = mx - WIN_X
        cy_cur = my - WIN_Y
        if 0 <= cx_cur < w and 0 <= cy_cur < h:
            cv2.circle(out, (cx_cur, cy_cur), 8,  (255, 255, 255), -1)
            cv2.circle(out, (cx_cur, cy_cur), 8,  (147, 241, 165),  2)
            cv2.circle(out, (cx_cur, cy_cur), 2,  (147, 241, 165), -1)

        writer.write(cv2.cvtColor(out, cv2.COLOR_RGB2BGR))

        if i % FPS == 0:
            print(f"  {i//FPS}s / {len(raw_frames)//FPS}s", end='\r')

    writer.release()
    size_mb = os.path.getsize(OUT_PATH) / 1e6
    print(f"\nSaved: {OUT_PATH}  ({size_mb:.1f} MB, {len(raw_frames)/FPS:.0f}s)")


# ── Demo script ───────────────────────────────────────────────────────────────
def run_demo():
    global stop_flag

    print("Launching PixelMaster...")
    proc = subprocess.Popen([VENV_PY, APP_PY])
    time.sleep(4.0)

    win = wait_window("Pixel Master")
    if not win:
        print("Window not found — aborting"); proc.terminate(); return

    win.moveTo(WIN_X, WIN_Y)
    win.resizeTo(WIN_W, WIN_H)
    win.activate()
    time.sleep(0.8)

    # start capture
    cap_thread = threading.Thread(target=_capture, daemon=True)
    cap_thread.start()
    time.sleep(0.5)

    # ── 1. Intro ──────────────────────────────────────────────────────────
    caption_hold(2.5, "PixelMaster  v1.1.1",
                 "AI-powered image processing")

    # ── 2. Upscaler tab ───────────────────────────────────────────────────
    caption_hold(0.6, "Feature 1 — AI Upscaler",
                 "Real-ESRGAN x4 super-resolution")

    # Open images via drop zone "Browse Files" button (~center of drop zone)
    move_click(560, 240, "Add images to queue", "Click Browse Files", zoom=True)
    open_file_dialog(os.path.abspath(os.path.join(SET5, 'butterfly.png')))
    caption_hold(0.8, "butterfly.png  (128x128 LR input)", "Set5 benchmark")

    # Add remaining images one by one
    for fname, label in [
        ('baby.png',  'baby.png  (72x72)'),
        ('bird.png',  'bird.png  (64x64)'),
        ('head.png',  'head.png  (70x70)'),
        ('woman.png', 'woman.png  (57x86)'),
    ]:
        move_click(560, 240, f"Adding {fname}", zoom=False)
        open_file_dialog(os.path.abspath(os.path.join(SET5, fname)))
        caption_hold(0.4, label, "")

    caption_hold(1.2, "5 images queued", "Set5 benchmark  ·  Ready to upscale")

    # Start processing  (bottom-right action button)
    move_click(890, 685, "Start Processing!", "Real-ESRGAN General x4", zoom=True)
    caption_hold(7.0, "Processing with Real-ESRGAN...",
                 "ONNX runtime — runs on CPU")
    caption_hold(2.0, "Upscaling complete!  x4 resolution",
                 "butterfly: 128x128 -> 512x512")

    # ── 3. Mosaic tab ─────────────────────────────────────────────────────
    move_click(373, 37, "Mosaic Tool", "", zoom=True)
    time.sleep(0.6)
    caption_hold(1.0, "Feature 2 — Mosaic / Blur Tool",
                 "Freehand Brush  ·  Box  ·  Circle selection")

    move_click(122, 168, "Open Image", "", zoom=True)
    open_file_dialog(os.path.abspath(os.path.join(SET5, 'head_HR.png')))
    caption_hold(1.0, "head_HR.png loaded", "280 x 280")

    # Paint brush strokes on canvas
    cx = WIN_X + 620; cy0 = WIN_Y + 360
    pyautogui.moveTo(cx - 70, cy0 - 30)
    pyautogui.mouseDown()
    for step in range(30):
        pyautogui.moveTo(
            cx + int(60 * math.sin(step * 0.4)),
            cy0 + int(40 * math.cos(step * 0.3)),
            duration=0.04
        )
    pyautogui.mouseUp()
    time.sleep(0.3)
    caption_hold(0.8, "Painting selection area...", "Brush mode")

    # Apply pixelate
    move_click(122, 495, "Apply Pixelate Effect!", "", zoom=True)
    time.sleep(0.4)
    caption_hold(1.5, "Mosaic applied!", "Pixelate effect  ·  Strength 15")

    # Switch to Box mode and demo
    move_click(155, 250, "Box Selection Mode", "Drag to create rectangle", zoom=True)
    time.sleep(0.4)
    caption_hold(0.5, "Box selection mode", "")
    # drag a box
    sx = WIN_X + 540; sy = WIN_Y + 310
    pyautogui.moveTo(sx, sy)
    pyautogui.mouseDown()
    pyautogui.moveTo(sx + 120, sy + 90, duration=0.4)
    pyautogui.mouseUp()
    caption_hold(0.5, "Box selected", "")

    # Apply blur
    move_click(248, 415, "Gaussian Blur", "", zoom=True)
    time.sleep(0.3)
    move_click(122, 495, "Apply Blur!", "", zoom=True)
    time.sleep(0.3)
    caption_hold(1.5, "Blur applied!", "Save result as new file")

    # ── 4. BG Remover tab ─────────────────────────────────────────────────
    move_click(500, 37, "BG Remover", "", zoom=True)
    time.sleep(0.6)
    caption_hold(1.0, "Feature 3 — AI Background Remover",
                 "Powered by rembg / u2net model")

    move_click(122, 168, "Open Image", "", zoom=True)
    open_file_dialog(os.path.abspath(os.path.join(SET5, 'butterfly_HR.png')))
    caption_hold(1.2, "butterfly_HR.png loaded", "512 x 512")

    move_click(122, 216, "Remove Background!", "AI segmentation with u2net", zoom=True)
    caption_hold(4.5, "Removing background...", "u2net model  ·  one-time 176MB download")
    caption_hold(2.0, "Background removed!",
                 "Transparent PNG ready  ·  Click Save as PNG")

    # ── 5. Outro ──────────────────────────────────────────────────────────
    caption_hold(2.5, "PixelMaster  v1.1.1",
                 "github.com/everise98/PixelMaster")

    # stop
    stop_flag.set()
    cap_thread.join(timeout=3)
    proc.terminate()
    time.sleep(0.3)

    build_video(raw_frames, click_log, caption_log)


if __name__ == '__main__':
    run_demo()
