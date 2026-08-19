"""TTS：在終端機輸入文字，Enter 後產生語音並播放。"""

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
        subprocess.run(["afplay", str(path)], check=False)
        return
    for cmd in ("mpg123", "ffplay", "xdg-open"):
        if which(cmd):
            if cmd == "ffplay":
                subprocess.run([cmd, "-nodisp", "-autoexit", str(path)], check=False)
            else:
                subprocess.run([cmd, str(path)], check=False)
            return
    print(f"找不到播放程式，請手動開啟：{path}")


def main() -> None:
    text = input("請輸入要轉換的文字：").strip()
    if not text:
        print("沒有輸入文字。")
        return

    print("正在轉換成語音…")
    gTTS(text=text, lang="zh-tw").save(str(MP3_PATH))
    print(f"已存檔：{MP3_PATH}")
    play_audio(MP3_PATH)


if __name__ == "__main__":
    main()
