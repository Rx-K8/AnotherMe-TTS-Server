"""WAVフォーマット変換"""

import io

import numpy as np
import torch
import torchaudio

from .base import AudioFormatConverter


class WAVConverter(AudioFormatConverter):
    """WAVフォーマットへの変換"""

    def convert(self, pcm_data: bytes, sample_rate: int, channels: int = 1) -> bytes:
        """PCMデータをWAVフォーマットに変換

        Args:
            pcm_data: 16-bit PCMデータ
            sample_rate: サンプリングレート (Hz)
            channels: チャンネル数

        Returns:
            WAVフォーマットの音声データ
        """
        # PCMバイトデータをnumpy配列に変換
        audio_np = np.frombuffer(pcm_data, dtype=np.int16)

        # float32に正規化 (-1.0 ~ 1.0)
        audio_np = audio_np.astype(np.float32) / 32768.0

        # torch tensorに変換 (channels, samples)
        audio_tensor = torch.from_numpy(audio_np).reshape(channels, -1)

        # WAV形式で保存
        wav_buffer = io.BytesIO()
        torchaudio.save(
            wav_buffer,
            audio_tensor,
            sample_rate,
            format="wav",
            encoding="PCM_S",
            bits_per_sample=16,
        )

        wav_buffer.seek(0)
        return wav_buffer.getvalue()
