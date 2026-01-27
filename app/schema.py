"""内部で使用するスキーマ定義"""

from typing import Literal

from pydantic import BaseModel, Field


class SynthesisParams(BaseModel):
    """
    音声合成の内部パラメータ
    TTSProviderが扱う純粋なパラメータ定義
    """

    text: str = Field(..., description="音声合成するテキスト")
    format: Literal["wav", "mp3", "pcm"] = Field(
        ..., description="応答する音声データのフォーマット"
    )
    speed: float = Field(default=1.0, description="音声の再生速度")
