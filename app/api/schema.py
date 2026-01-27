"""APIリクエスト・レスポンスのスキーマ定義"""

from pydantic import BaseModel, Field


class TTSRequest(BaseModel):
    """音声合成APIのリクエスト定義"""

    input: str = Field(..., description="音声合成するテキスト")
    speed: float = Field(default=1.0, description="音声の再生速度")


class TTSResponse(BaseModel):
    """音声合成APIのレスポンス定義"""

    audio_data: str = Field(..., description="Base64エンコードされた音声データ")


class TTSErrorResponse(BaseModel):
    """音声合成APIのエラーレスポンス定義"""

    error: str = Field(..., description="エラーメッセージ")
    detail: str | None = Field(default=None, description="詳細なエラー情報")
