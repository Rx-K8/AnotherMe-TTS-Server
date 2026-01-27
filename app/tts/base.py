"""TTSプロバイダーの基底クラス"""

from abc import ABC, abstractmethod

from app.schema import SynthesisParams


class TTSProvider(ABC):
    """音声合成プロバイダーの抽象基底クラス"""

    @abstractmethod
    async def synthesize(self, params: SynthesisParams) -> bytes:
        """指定されたテキスト、速度で音声を合成し、バイト列として返す"""
        pass
