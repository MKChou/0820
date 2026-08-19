"""ASR: press Enter to start recording, press Enter again to stop, then transcribe."""

from __future__ import annotations

import base64
import os
import shutil
import subprocess
from contextlib import contextmanager
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


@contextmanager
def quiet_stderr():
    devnull = os.open(os.devnull, os.O_WRONLY)
    saved = os.dup(2)
    os.dup2(devnull, 2)
    try:
        yield
    finally:
        os.dup2(saved, 2)
        os.close(saved)
        os.close(devnull)


def to_16k_mono(audio: np.ndarray, rate: int) -> np.ndarray:
    if audio.ndim == 2:
        audio = audio[:, 0]
    samples = audio.astype(np.float32)
    if rate != SAMPLE_RATE and len(samples) > 0:
        n = int(round(len(samples) * SAMPLE_RATE / float(rate)))
        samples = resample(samples, max(n, 1))
    return np.clip(samples, -32768, 32767).astype(np.int16)


def record_with_sounddevice() -> None:
    with quiet_stderr():
        info = sd.query_devices(kind="input")
    default_rate = int(round(float(info["default_samplerate"])))
    rates: list[int] = []
    for rate in (default_rate, 48000, 44100, SAMPLE_RATE, 32000, 8000):
        if rate > 0 and rate not in rates:
            rates.append(rate)

    chunks: list[np.ndarray] = []

    def callback(indata, frames, time, status):
        chunks.append(indata.copy())

    stream = None
    used_rate = None
    last_error: Exception | None = None
    for channels in (1, 2):
        for rate in rates:
            try:
                with quiet_stderr():
                    stream = sd.InputStream(
                        samplerate=rate,
                        channels=channels,
                        dtype="int16",
                        callback=callback,
                    )
                    stream.start()
                used_rate = rate
                break
            except Exception as exc:
                last_error = exc
                if stream is not None:
                    with quiet_stderr():
                        stream.close()
                    stream = None
        if stream is not None:
            break

    if stream is None or used_rate is None:
        raise last_error or RuntimeError("No usable microphone")

    try:
        input()
    finally:
        with quiet_stderr():
            stream.stop()
            stream.close()

    if not chunks:
        raise RuntimeError("No audio captured")

    audio = to_16k_mono(np.concatenate(chunks, axis=0), used_rate)
    write_wav(str(WAV_PATH), SAMPLE_RATE, audio)


def record_with_arecord() -> None:
    if shutil.which("arecord") is None:
        raise RuntimeError("arecord not found")

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
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            proc.wait(timeout=0.4)
        except subprocess.TimeoutExpired:
            input()
            proc.terminate()
            proc.wait(timeout=5)
            if WAV_PATH.exists() and WAV_PATH.stat().st_size > 44:
                return
            last_error = RuntimeError("arecord produced no file")
            continue
        last_error = RuntimeError(f"arecord cannot use {device}")
    raise last_error or RuntimeError("arecord failed")


def record_until_enter() -> Path:
    input("Press Enter to start recording...")
    print("Recording. Press Enter to stop.")
    try:
        record_with_sounddevice()
    except Exception:
        record_with_arecord()
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
    try:
        wav_path = record_until_enter()
        text = speech_to_text(wav_path)
    except Exception:
        print("Failed.")
        return
    print(text or "No text recognized.")


if __name__ == "__main__":
    main()
