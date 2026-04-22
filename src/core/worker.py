import os
import threading
import tempfile
import shutil
from PyQt6.QtCore import QThread, pyqtSignal
from .upscaler import upscale_image


class UpscaleWorker(QThread):
    image_started  = pyqtSignal(str)
    preview_ready  = pyqtSignal(str, str, str)    # input, temp_output, uid
    image_done     = pyqtSignal(str, bool, str)   # input, success, msg/path
    progress       = pyqtSignal(int)
    all_done       = pyqtSignal(int, int, int)    # saved, errored, skipped

    def __init__(
        self,
        tasks: list[str],
        scale: int,
        method: str,
        output_suffix: str,
        output_folder: str,
        jpeg_quality: int = 95,
    ):
        super().__init__()
        self.tasks = tasks
        self.scale = scale
        self.method = method
        self.output_suffix = output_suffix
        self.output_folder = output_folder
        self.jpeg_quality = jpeg_quality
        self._cancelled = False
        self._events: dict[str, threading.Event] = {}
        self._decisions: dict[str, bool] = {}

    def cancel(self):
        self._cancelled = True

    def confirm(self, uid: str, save: bool):
        """Called from the main thread to resume the worker."""
        self._decisions[uid] = save
        if uid in self._events:
            self._events[uid].set()

    def run(self):
        total = len(self.tasks)
        saved = errored = skipped = 0

        for i, input_path in enumerate(self.tasks):
            if self._cancelled:
                break

            self.image_started.emit(input_path)

            name, ext = os.path.splitext(os.path.basename(input_path))
            output_name = f"{name}{self.output_suffix}{ext}"
            folder = self.output_folder or os.path.dirname(input_path)
            final_path = os.path.join(folder, output_name)

            # ── process into a temp file ──────────────────────────────────
            try:
                tmp_fd, tmp_path = tempfile.mkstemp(suffix=ext.lower())
                os.close(tmp_fd)
            except Exception as exc:
                self.image_done.emit(input_path, False, str(exc))
                self.progress.emit(int((i + 1) / total * 100))
                errored += 1
                continue

            ok, msg = upscale_image(
                input_path, tmp_path, self.scale, self.method, self.jpeg_quality
            )

            if not ok:
                _silent_remove(tmp_path)
                self.image_done.emit(input_path, False, msg)
                self.progress.emit(int((i + 1) / total * 100))
                errored += 1
                continue

            # ── ask the user (blocks worker thread, not UI) ───────────────
            uid = f"uid_{i}_{abs(hash(input_path))}"
            event = threading.Event()
            self._events[uid] = event
            self.preview_ready.emit(input_path, tmp_path, uid)
            event.wait()

            if self._decisions.get(uid, False):
                try:
                    os.makedirs(os.path.dirname(final_path) or ".", exist_ok=True)
                    if os.path.exists(final_path):
                        os.unlink(final_path)
                    shutil.move(tmp_path, final_path)
                    self.image_done.emit(input_path, True, final_path)
                    saved += 1
                except Exception as exc:
                    _silent_remove(tmp_path)
                    self.image_done.emit(input_path, False, str(exc))
                    errored += 1
            else:
                _silent_remove(tmp_path)
                self.image_done.emit(input_path, False, "Skipped")
                skipped += 1

            self.progress.emit(int((i + 1) / total * 100))

        self.all_done.emit(saved, errored, skipped)


def _silent_remove(path: str):
    try:
        if os.path.exists(path):
            os.unlink(path)
    except Exception:
        pass
