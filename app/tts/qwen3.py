"""Qwen3-TTS Voice Clone プロバイダー実装

Voice Cloneモード専用: 参照音声から声をクローンして音声合成を行う
https://github.com/QwenLM/Qwen3-TTS
"""

import io
from typing import Any

import soundfile as sf  # type: ignore[import-untyped]
import torch
from qwen_tts import Qwen3TTSModel

from app.schema import SynthesisParams
from app.tts.base import TTSProvider


class Qwen3TTSProvider(TTSProvider):
    """Qwen3-TTS Voice Clone プロバイダー

    Qwen3-TTS-12Hz-1.7B-Base モデルを使用したVoice Clone専用の音声合成。
    参照音声（ref_audio）とそのテキスト（ref_text）から声をクローンし、
    任意のテキストをその声で合成する。
    """

    def __init__(self, ref_audio_path: str, ref_text: str) -> None:
        """Voice Cloneプロバイダーを初期化

        Args:
            ref_audio_path: 参照音声ファイルのパス（3秒程度推奨）
            ref_text: 参照音声のテキスト書き起こし
        """
        self.model = Qwen3TTSModel.from_pretrained(
            "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
            device_map="cuda:0",
            dtype=torch.bfloat16,
        )

        # Voice Cloneプロンプトをキャッシュ（毎回再計算を回避）
        self._voice_clone_prompt: Any = self.model.create_voice_clone_prompt(
            ref_audio=ref_audio_path,
            ref_text=ref_text,
        )

    async def synthesize(self, params: SynthesisParams) -> bytes:
        """テキストを音声に合成してWAVバイト列を返す"""
        wavs, sr = self.model.generate_voice_clone(
            text=params.text,
            language="Japanese",
            voice_clone_prompt=self._voice_clone_prompt,
        )

        audio_data = wavs[0] if isinstance(wavs, list) else wavs

        buffer = io.BytesIO()
        sf.write(buffer, audio_data, sr, format="WAV")
        return buffer.getvalue()
