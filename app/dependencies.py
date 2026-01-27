"""FastAPI依存性注入の定義"""

from app.service import TTSService
from app.tts.base import TTSProvider
from app.tts.qwen3 import Qwen3TTSProvider

# 参照音声設定（ボイスクローン用）
REF_AUDIO_PATH = "assets/ondokusan.mp3"
REF_TEXT = "ここに読み上げたいテキストを貼り付けて下さい。"


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
            cls._tts_provider = Qwen3TTSProvider(
                ref_audio_path=REF_AUDIO_PATH,
                ref_text=REF_TEXT,
            )
        return cls._tts_provider

    @classmethod
    def get_tts_service(cls) -> TTSService:
        """TTSServiceのシングルトンインスタンスを取得"""
        if cls._tts_service is None:
            cls._tts_service = TTSService(cls.get_tts_provider())
        return cls._tts_service

    @classmethod
    def initialize(cls) -> None:
        """依存性を初期化"""
        cls._tts_provider = Qwen3TTSProvider(
            ref_audio_path=REF_AUDIO_PATH,
            ref_text=REF_TEXT,
        )

    @classmethod
    def reset(cls) -> None:
        """依存性をリセット"""
        cls._tts_provider = None
        cls._tts_service = None


def get_tts_service() -> TTSService:
    """TTSServiceを取得（FastAPI Depends用）"""
    return TTSDependencies.get_tts_service()
