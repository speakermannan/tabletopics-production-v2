from __future__ import annotations

# app/recorder.py

import os
import queue
from dataclasses import dataclass
from typing import Optional

import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write as wav_write


@dataclass
class RecorderConfig:
    samplerate: int = 16000
    channels: int = 1
    dtype: str = "int16"


class AudioRecorder:
    def __init__(self, config: Optional[RecorderConfig] = None) -> None:
        self.config = config or RecorderConfig()
        self._q: "queue.Queue[np.ndarray]" = queue.Queue()
        self._stream: Optional[sd.InputStream] = None
        self._is_recording: bool = False

    @property
    def is_recording(self) -> bool:
        return self._is_recording

    def _callback(self, indata, frames, time, status) -> None:
        self._q.put(indata.copy())

    def start(self) -> None:
        if self._is_recording:
            return

        self._q = queue.Queue()
        self._stream = sd.InputStream(
            samplerate=self.config.samplerate,
            channels=self.config.channels,
            dtype=self.config.dtype,
            callback=self._callback,
        )
        self._stream.start()
        self._is_recording = True

    def stop(self, save_path: str) -> str:
        """
        IMPORTANT: abort() avoids blocking/hangs on some Windows audio drivers.
        """
        if not self._is_recording or self._stream is None:
            raise RuntimeError("Recorder is not running.")

        stream = self._stream

        try:
            if hasattr(stream, "abort"):
                stream.abort()
            else:
                stream.stop()
        finally:
            try:
                stream.close()
            except Exception:
                pass

            self._stream = None
            self._is_recording = False

        chunks = []
        while not self._q.empty():
            chunks.append(self._q.get())

        if not chunks:
            raise RuntimeError("No audio captured. Check microphone permissions/device.")

        audio = np.concatenate(chunks, axis=0)

        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        wav_write(save_path, self.config.samplerate, audio)
        return save_path
