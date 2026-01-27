"""TTS プロバイダーモジュール"""

from app.tts.base import TTSProvider
from app.tts.cosyvoice import CosyVoiceTTSProvider

__all__ = ["TTSProvider", "CosyVoiceTTSProvider"]
