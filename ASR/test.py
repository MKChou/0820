"""ASR：按下 Enter 開始錄音，再按 Enter 停止，然後轉成文字。"""

from __future__ import annotations

import base64
import shutil
import subprocess
from pathlib import Path

import numpy as np
import requests
import sounddevice as sd
from scipy.io.wavfile import write as write_wav
from scipy.signal import resample

ASR_URL = "http://140.116.245.149:5002/proxy"
ASR_LANG = "Chinese & Taiwanese"
ASR_TOKEN = "2025@ME@asr"
SAMPLE_RATE = 16000

HERE = Path(__file__).resolve().parent
WAV_PATH = HERE / "recording.wav"


def to_16k_mono(audio: np.ndarray, rate: int) -> np.ndarray:
    """學校 ASR 要 16 kHz、單聲道、16-bit。樹莓派麥克風常只能錄 44.1k/48k。"""
    if audio.ndim == 2:
        audio = audio[:, 0]
    samples = audio.astype(np.float32)
    if rate != SAMPLE_RATE and len(samples) > 0:
        n = int(round(len(samples) * SAMPLE_RATE / float(rate)))
        samples = resample(samples, max(n, 1))
    return np.clip(samples, -32768, 32767).astype(np.int16)


def record_with_sounddevice() -> None:
    info = sd.query_devices(kind="input")
    print(f"使用麥克風：{info['name']}")
    default_rate = int(round(float(info["default_samplerate"])))
    rates: list[int] = []
    for rate in (SAMPLE_RATE, default_rate, 48000, 44100, 32000, 8000):
        if rate > 0 and rate not in rates:
            rates.append(rate)

    chunks: list[np.ndarray] = []

    def callback(indata, frames, time, status):
        if status:
            print(status)
        chunks.append(indata.copy())

    stream = None
    used_rate = None
    last_error: Exception | None = None
    for channels in (1, 2):
        for rate in rates:
            try:
                stream = sd.InputStream(
                    samplerate=rate,
                    channels=channels,
                    dtype="int16",
                    callback=callback,
                )
                stream.start()
                used_rate = rate
                print(f"錄音取樣率：{rate} Hz（{channels} 聲道）")
                break
            except Exception as exc:
                last_error = exc
                if stream is not None:
                    stream.close()
                    stream = None
        if stream is not None:
            break

    if stream is None or used_rate is None:
        raise last_error or RuntimeError("找不到可用的麥克風取樣率")

    try:
        input()
    finally:
        stream.stop()
        stream.close()

    if not chunks:
        raise RuntimeError("沒有錄到聲音，請再試一次。")

    audio = to_16k_mono(np.concatenate(chunks, axis=0), used_rate)
    write_wav(str(WAV_PATH), SAMPLE_RATE, audio)


def record_with_arecord() -> None:
    """樹莓派 ALSA 的 plughw 可自動轉成 16 kHz。"""
    if shutil.which("arecord") is None:
        raise RuntimeError("系統沒有 arecord")

    devices = ["default", "plughw:1,0", "plughw:2,0", "plughw:0,0"]
    last_error: Exception | None = None
    for device in devices:
        cmd = [
            "arecord",
            "-D",
            device,
            "-f",
            "S16_LE",
            "-r",
            str(SAMPLE_RATE),
            "-c",
            "1",
            "-q",
            str(WAV_PATH),
        ]
        proc = subprocess.Popen(cmd, stderr=subprocess.PIPE)
        # 若裝置不對，arecord 會很快結束
        try:
            proc.wait(timeout=0.4)
        except subprocess.TimeoutExpired:
            print(f"使用 arecord 裝置：{device}")
            input()
            proc.terminate()
            proc.wait(timeout=5)
            if WAV_PATH.exists() and WAV_PATH.stat().st_size > 44:
                return
            last_error = RuntimeError("arecord 沒有錄到檔案")
            continue
        stderr = (proc.stderr.read() if proc.stderr else b"").decode(errors="ignore")
        last_error = RuntimeError(stderr.strip() or f"arecord 無法使用 {device}")
    raise last_error or RuntimeError("arecord 錄音失敗")


def record_until_enter() -> Path:
    input("按下 Enter 開始錄音…")
    print("錄音中，再說一次 Enter 停止。")
    try:
        record_with_sounddevice()
    except Exception as exc:
        print(f"sounddevice 錄音失敗（{exc}），改用 arecord…")
        record_with_arecord()
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
