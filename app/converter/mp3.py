import io

import numpy as np
import torch
import torchaudio

from .base import AudioFormatConverter


class MP3Converter(AudioFormatConverter):
    """MP3フォーマットへの変換

    Note:
        MP3は完全な音声データが必要なため、ストリーミングには不向きです。
        ストリーミングが必要な場合はPCMまたはWAVを使用してください。
    """

    def __init__(self, bitrate: str = "128k"):
        """
        Args:
            bitrate: MP3のビットレート (例: "128k", "192k", "320k")
        """
        # bitrateから数値を抽出 (例: "128k" -> 128000)
        self.bitrate = int(bitrate.lower().replace("k", "")) * 1000

    def convert(self, pcm_data: bytes, sample_rate: int, channels: int = 1) -> bytes:
        """PCMデータをMP3フォーマットに変換

        Args:
            pcm_data: 16-bit PCMデータ
            sample_rate: サンプリングレート (Hz)
            channels: チャンネル数

        Returns:
            MP3フォーマットの音声データ
        """
        audio_np = np.frombuffer(pcm_data, dtype=np.int16)

        audio_np = audio_np.astype(np.float32) / 32768.0

        audio_tensor = torch.from_numpy(audio_np).reshape(channels, -1)

        mp3_buffer = io.BytesIO()
        torchaudio.save(mp3_buffer, audio_tensor, sample_rate, format="mp3")

        mp3_buffer.seek(0)
        return mp3_buffer.getvalue()
