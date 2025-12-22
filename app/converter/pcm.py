"""PCMフォーマット変換"""

from .base import AudioFormatConverter


class PCMConverter(AudioFormatConverter):
    """PCMフォーマット（変換なし）"""

    def convert(self, pcm_data: bytes, sample_rate: int, channels: int = 1) -> bytes:
        """PCMデータをそのまま返す

        Args:
            pcm_data: 16-bit PCMデータ
            sample_rate: サンプリングレート (Hz)
            channels: チャンネル数

        Returns:
            入力と同じPCMデータ
        """
        return pcm_data
