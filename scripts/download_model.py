"""Explicitly download Google's public MediaPipe Face Landmarker task model."""

from __future__ import annotations

import hashlib
import os
import sys
import tempfile
import urllib.request
from pathlib import Path

MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
EXPECTED_SHA256 = "64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff"
ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "models" / "face_landmarker.task"
MAX_BYTES = 80 * 1024 * 1024


def download() -> Path:
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(MODEL_URL, headers={"User-Agent": "ShetShetNakitaAko/0.1"})
    temporary_path: Path | None = None
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            if response.status != 200:
                raise RuntimeError(f"Model server returned HTTP {response.status}")
            with tempfile.NamedTemporaryFile(dir=DESTINATION.parent, prefix=".model-", delete=False) as out:
                temporary_path = Path(out.name)
                digest = hashlib.sha256()
                total = 0
                while chunk := response.read(1024 * 1024):
                    total += len(chunk)
                    if total > MAX_BYTES:
                        raise RuntimeError("Model download exceeded the 80 MB safety limit")
                    digest.update(chunk)
                    out.write(chunk)
        if total < 1024 * 1024:
            raise RuntimeError("Downloaded model is unexpectedly small; the file was not installed")
        if digest.hexdigest() != EXPECTED_SHA256:
            raise RuntimeError("Model SHA-256 did not match the pinned official model file")
        os.replace(temporary_path, DESTINATION)
        print(f"Saved {DESTINATION} ({total:,} bytes; SHA-256 {digest.hexdigest()})")
        print("Source: official Google MediaPipe model storage over HTTPS.")
        return DESTINATION
    finally:
        if temporary_path and temporary_path.exists():
            temporary_path.unlink()


if __name__ == "__main__":
    try:
        download()
    except Exception as exc:
        print(f"Could not download the model: {exc}", file=sys.stderr)
        raise SystemExit(1)
