from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import BinaryIO, Protocol
from uuid import UUID


@dataclass
class AudioMetadata:
    """音声ファイルのメタデータ(Immutable)"""

    id: UUID
    filename: str
    content_type: str
    size_bytes: int
    sample_rate: int
    duration_seconds: float | None = None
    created_at: datetime = datetime.now()

    @property
    def extension(self) -> str:
        """ファイル拡張子を取得"""
        return Path(self.filename).suffix.lower()


class AudioStorage(Protocol):
    """音声ファイルストレージのProtocol"""

    async def save(self, file: BinaryIO, meatadata: AudioMetadata) -> str:
        """音声ファイルを保存

        Args:
            file: 保存する音声ファイルのバイナリストリ
            metadata: メタデータ

        Returns:
            保存先のパス/URI
        """
        ...

    async def load(self, audio: UUID) -> bytes:
        """音声ファイルを読み込み

        Args:
            audio: 音声ID

        Returns:
            音声データ
        """
        ...

    async def delete(self, audio_id: UUID) -> bool:
        """音声ファイルを削除

        Args:
            audio_id: 音声ID

        Returns:
            削除成功したかどうか
        """
        ...

    async def get_metadata(self, auido_id: UUID) -> AudioMetadata | None:
        """音声ファイルのメタデータを取得

        Args:
            audio_id: 音声ID

        Returns:
            メタデータ、存在しない場合はNone
        """
        ...


class MetadataRepository(Protocol):
    """メタデータ永続化のProtocol"""

    async def save_metadata(self, metadata: AudioMetadata) -> None:
        """メタデータを保存"""
        ...

    async def get_metadata(self, audio_id: UUID) -> AudioMetadata | None:
        """メタデータを取得"""
        ...

    async def list_metadata(self) -> list[AudioMetadata]:
        """すべてのメタデータを取得"""
        ...

    async def delete_metadata(self, audio_id: UUID) -> bool:
        """メタデータを削除"""
        ...
