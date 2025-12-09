"""FastAPI依存性注入の定義"""

from app.service import TTSService
from app.tts.base import TTSProvider
from app.tts.cosyvoice import CosyVoiceTTSProvider


class TTSDependencies:
    """
    TTS関連の依存性を管理するコンテナ

    依存性の注入を一元管理し、テスト時のモック置換を容易にする
    """

    _tts_provider: TTSProvider | None = None
    _tts_service: TTSService | None = None

    @classmethod
    def get_tts_provider(cls) -> TTSProvider:
        """TTSProviderのシングルトンインスタンスを取得"""
        if cls._tts_provider is None:
            cls._tts_provider = CosyVoiceTTSProvider(
                prompt_voice_path="asset/ondokusan.mp3",
                prompt_text="ここに読み上げたいテキストを貼り付けて下さい。",
            )
        return cls._tts_provider

    @classmethod
    def get_tts_service(cls) -> TTSService:
        """TTSServiceのシングルトンインスタンスを取得"""
        if cls._tts_service is None:
            cls._tts_service = TTSService(cls.get_tts_provider())
        return cls._tts_service

    @classmethod
    def set_tts_provider(cls, provider: TTSProvider) -> None:
        """TTSProviderを設定（テスト用）"""
        cls._tts_provider = provider
        cls._tts_service = None

    @classmethod
    def reset(cls) -> None:
        """依存性をリセット（テスト用）"""
        cls._tts_provider = None
        cls._tts_service = None


def get_tts_service() -> TTSService:
    """TTSServiceを取得（FastAPI Depends用）"""
    return TTSDependencies.get_tts_service()
