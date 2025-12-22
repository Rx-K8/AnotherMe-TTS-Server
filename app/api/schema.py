"""APIリクエスト・レスポンスのスキーマ定義"""

from typing import Literal

from pydantic import BaseModel, Field


class TTSRequest(BaseModel):
    """音声合成APIのリクエスト定義"""

    input: str = Field(..., description="音声合成するテキスト")
    response_format: Literal["wav", "mp3", "pcm"] = Field(
        default="pcm", description="応答する音声データのフォーマット"
    )
    speed: float = Field(default=1.0, description="音声の再生速度")


class TTSResponse(BaseModel):
    """音声合成APIのレスポンス定義"""

    audio_data: str = Field(..., description="Base64エンコードされた音声データ")
    format: str = Field(..., description="音声データのフォーマット")
    sample_rate: int = Field(default=22050, description="サンプルレート")


class TTSErrorResponse(BaseModel):
    """音声合成APIのエラーレスポンス定義"""

    error: str = Field(..., description="エラーメッセージ")
    detail: str | None = Field(default=None, description="詳細なエラー情報")
