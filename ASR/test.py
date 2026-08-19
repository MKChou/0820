"""ASR：按下 Enter 開始錄音，再按 Enter 停止，然後轉成文字。"""

from __future__ import annotations

import base64
from pathlib import Path

import numpy as np
import requests
import sounddevice as sd
from scipy.io.wavfile import write as write_wav

ASR_URL = "http://140.116.245.149:5002/proxy"
ASR_LANG = "Chinese & Taiwanese"
ASR_TOKEN = "2025@ME@asr"
SAMPLE_RATE = 16000

HERE = Path(__file__).resolve().parent
WAV_PATH = HERE / "recording.wav"


def record_until_enter() -> Path:
    chunks: list[np.ndarray] = []

    def callback(indata, frames, time, status):
        if status:
            print(status)
        chunks.append(indata.copy())

    input("按下 Enter 開始錄音…")
    print("錄音中，再說一次 Enter 停止。")
    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16",
        callback=callback,
    ):
        input()

    if not chunks:
        raise RuntimeError("沒有錄到聲音，請再試一次。")

    audio = np.concatenate(chunks, axis=0)
    write_wav(str(WAV_PATH), SAMPLE_RATE, audio)
    print(f"已存檔：{WAV_PATH}")
    return WAV_PATH


def speech_to_text(wav_path: Path) -> str:
    audio_b64 = base64.b64encode(wav_path.read_bytes()).decode()
    response = requests.post(
        ASR_URL,
        data={
            "lang": ASR_LANG,
            "token": ASR_TOKEN,
            "audio": audio_b64,
        },
        timeout=30,
    )
    response.raise_for_status()
    return str(response.json().get("sentence") or "").strip()


def main() -> None:
    wav_path = record_until_enter()
    print("正在語音轉文字…")
    text = speech_to_text(wav_path)
    if text:
        print("辨識結果：", text)
    else:
        print("沒有辨識到文字。")


if __name__ == "__main__":
    main()
