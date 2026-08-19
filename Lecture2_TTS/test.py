"""TTS: type text in the terminal, press Enter, then generate and play audio."""

from __future__ import annotations

import os
import platform
import subprocess
from pathlib import Path
from shutil import which

from gtts import gTTS

HERE = Path(__file__).resolve().parent
MP3_PATH = HERE / "output.mp3"


def play_audio(path: Path) -> None:
    path = path.resolve()
    system = platform.system()
    if system == "Windows":
        os.startfile(path)  # type: ignore[attr-defined]
        return
    if system == "Darwin":
        subprocess.run(
            ["afplay", str(path)],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return
    for cmd in ("mpg123", "ffplay", "xdg-open"):
        if which(cmd):
            args = [cmd, str(path)]
            if cmd == "mpg123":
                args = [cmd, "-q", str(path)]
            elif cmd == "ffplay":
                args = [cmd, "-nodisp", "-autoexit", "-loglevel", "quiet", str(path)]
            subprocess.run(
                args,
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return


def main() -> None:
    text = input("Enter text: ").strip()
    if not text:
        return
    try:
        gTTS(text=text, lang="zh-tw").save(str(MP3_PATH))
        play_audio(MP3_PATH)
    except Exception:
        print("Failed.")


if __name__ == "__main__":
    main()
