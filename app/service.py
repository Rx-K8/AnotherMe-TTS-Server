"""TTS サービス層"""

from collections.abc import AsyncIterator

from app.schema import SynthesisParams
from app.tts.base import TTSProvider


class TTSService:
    """音声合成サービス"""

    def __init__(self, tts_provider: TTSProvider):
        self.tts_provider = tts_provider

    async def synthesize(self, params: SynthesisParams) -> bytes:
        """テキストを音声に合成"""
        return await self.tts_provider.synthesize(params)

    async def synthesize_stream(self, params: SynthesisParams) -> AsyncIterator[bytes]:
        """テキストを音声にストリーミング合成"""
        async for chunk in self.tts_provider.synthesize_stream(params):
            yield chunk
