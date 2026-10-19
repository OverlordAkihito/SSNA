"""Non-blocking playback for the filter-off cue on Windows."""

from __future__ import annotations

import ctypes
import logging
import os
from pathlib import Path
from queue import Queue
from threading import Lock, Thread

logger = logging.getLogger(__name__)


class _MciMp3Session:
    """Small Windows MCI wrapper for one local MP3 file."""

    _alias = "shet_shet_filter_cue"

    def __init__(self, path: Path):
        if os.name != "nt":
            raise OSError("Windows MP3 playback is only available on Windows.")
        if '"' in str(path):
            raise ValueError("The audio asset path cannot contain a quote character.")
        self.path = path
        self._opened = False
        self._winmm = ctypes.WinDLL("winmm")
        self._send = self._winmm.mciSendStringW
        self._send.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint, ctypes.c_void_p]
        self._send.restype = ctypes.c_uint
        self._get_error = self._winmm.mciGetErrorStringW
        self._get_error.argtypes = [ctypes.c_uint, ctypes.POINTER(ctypes.c_wchar), ctypes.c_uint]
        self._get_error.restype = ctypes.c_int

    def _command(self, command: str) -> None:
        error = self._send(command, None, 0, None)
        if not error:
            return
        message = ctypes.create_unicode_buffer(256)
        if not self._get_error(error, message, len(message)):
            detail = message.value or f"MCI error {error}"
        else:
            detail = f"MCI error {error}"
        raise OSError(detail)

    def open(self) -> None:
        self._command(f'open "{self.path}" type mpegvideo alias {self._alias}')
        self._opened = True

    def stop(self) -> None:
        if self._opened:
            self._command(f"stop {self._alias}")

    def play(self) -> None:
        if not self._opened:
            raise RuntimeError("The MP3 cue is not open.")
        # MCI playback is asynchronous unless the `wait` flag is specified.
        self._command(f"play {self._alias} from 0")

    def close(self) -> None:
        if not self._opened:
            return
        try:
            self.stop()
        finally:
            try:
                self._command(f"close {self._alias}")
            finally:
                self._opened = False


class Mp3CuePlayer:
    """Queue short, non-blocking playback requests on one reusable worker."""

    def __init__(self, path: Path, *, session_factory=None):
        self.path = Path(path)
        self._session_factory = session_factory or _MciMp3Session
        self._requests: Queue[bool | None] = Queue()
        self._lock = Lock()
        self._thread: Thread | None = None
        self._closed = False

    def play(self) -> bool:
        if not self.path.is_file():
            logger.warning("Filter-off sound is missing or unreadable: %s", self.path)
            return False
        if not os.access(self.path, os.R_OK):
            logger.warning("Filter-off sound is not readable: %s", self.path)
            return False
        with self._lock:
            if self._closed:
                logger.debug("Ignored filter-off sound request after audio player shutdown.")
                return False
            if self._thread is None:
                self._thread = Thread(target=self._run, name="filter-off-audio", daemon=True)
                self._thread.start()
            self._requests.put(True)
        return True

    def _run(self) -> None:
        session = None
        try:
            while True:
                request = self._requests.get()
                if request is None:
                    break
                try:
                    if session is None:
                        session = self._session_factory(self.path)
                        session.open()
                    else:
                        session.stop()
                    session.play()
                except Exception:
                    logger.exception("Could not play filter-off MP3: %s", self.path)
                    if session is not None:
                        try:
                            session.close()
                        except Exception:
                            logger.exception("Could not release the filter-off audio session")
                        session = None
        finally:
            if session is not None:
                try:
                    session.close()
                except Exception:
                    logger.exception("Could not release the filter-off audio session")

    def close(self) -> None:
        with self._lock:
            if self._closed:
                return
            self._closed = True
            thread = self._thread
            if thread is not None:
                self._requests.put(None)
        if thread is not None:
            thread.join(timeout=2.0)
            if thread.is_alive():
                logger.warning("Audio worker did not stop within two seconds.")
