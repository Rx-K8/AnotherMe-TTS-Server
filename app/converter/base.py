"""音声フォーマット変換の基底クラス"""

from abc import ABC, abstractmethod


class AudioFormatConverter(ABC):
    """音声フォーマット変換の抽象基底クラス (OCP対応)"""

    @abstractmethod
    def convert(self, pcm_data: bytes, sample_rate: int, channels: int = 1) -> bytes:
        """PCMデータを特定のフォーマットに変換する

        Args:
            pcm_data: 16-bit PCMデータ
            sample_rate: サンプリングレート (Hz)
            channels: チャンネル数 (1: モノラル, 2: ステレオ)

        Returns:
            変換後の音声データ
        """
        pass
