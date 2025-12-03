"""音声フォーマット変換ユーティリティ"""

import io
import wave
from abc import ABC, abstractmethod


class AudioFormatConverter(ABC):
    """音声フォーマット変換の抽象基底クラス (OCP対応)"""

    @abstractmethod
    def convert(self, pcm_data: bytes, sample_rate: int, channels: int = 1) -> bytes:
        """PCMデータを特定のフォーマットに変換する"""
        pass


class PCMConverter(AudioFormatConverter):
    """PCMフォーマット（変換なし）"""

    def convert(self, pcm_data: bytes, sample_rate: int, channels: int = 1) -> bytes:
        return pcm_data


class WAVConverter(AudioFormatConverter):
    """WAVフォーマットへの変換"""

    def convert(self, pcm_data: bytes, sample_rate: int, channels: int = 1) -> bytes:
        """PCMデータをWAVフォーマットに変換"""
        sample_width = 2  # 16-bit

        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(sample_width)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(pcm_data)

        return buffer.getvalue()


class AudioConverterFactory:
    """音声コンバーターのファクトリークラス"""

    _converters: dict[str, type[AudioFormatConverter]] = {
        "pcm": PCMConverter,
        "wav": WAVConverter,
    }

    @classmethod
    def get_converter(cls, format_type: str) -> AudioFormatConverter:
        """指定されたフォーマットのコンバーターを取得"""
        converter_class = cls._converters.get(format_type.lower())
        if converter_class is None:
            raise ValueError(
                f"Unsupported format: {format_type}. "
                f"Supported formats: {list(cls._converters.keys())}"
            )
        return converter_class()

    @classmethod
    def register_converter(
        cls, format_type: str, converter_class: type[AudioFormatConverter]
    ) -> None:
        """新しいコンバーターを登録 (OCP: 拡張のために開放)"""
        cls._converters[format_type.lower()] = converter_class

    @classmethod
    def supported_formats(cls) -> list[str]:
        """サポートされているフォーマットの一覧を取得"""
        return list(cls._converters.keys())
