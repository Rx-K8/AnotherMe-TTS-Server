from pathlib import Path
from typing import BinaryIO
from uuid import UUID

import aiofiles
import aiofiles.os

from app.storage.base import AudioMetadata, AudioStorage, MetadataRepository
from app.types import PathLike


class LocalFileStorage(AudioStorage):
    """ローカルファイルシステムへの音声保存"""

    def __init__(self, base_dir: PathLike, metadata_repo: MetadataRepository):
        """
        Args:
            base_dir: ベースディレクトリ
            metadata_repo: メタデータリポジトリ
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_repo = metadata_repo

    def _get_file_path(self, audio_id: UUID) -> Path:
        """音声IDからファイルパスを生成"""
        id_str = str(audio_id)
        return self.base_dir / id_str

    async def save(self, file: BinaryIO, metadata: AudioMetadata) -> str:
        """音声ファイルを保存"""
        file_path = self._get_file_path(metadata.id)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        content: bytes = file.read()

        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)

        await self.metadata_repo.save_metadata(metadata)

        return str(file_path)

    async def load(self, audio_id: UUID) -> bytes:
        """音声ファイルを読み込む"""
        file_path = self._get_file_path(audio_id)

        if not await aiofiles.os.path.exists(file_path):
            raise FileNotFoundError(f"オーディオファイルが見つかりません: {audio_id}")

        async with aiofiles.open(file_path, "rb") as f:
            content = await f.read()
            return content

    async def delete(self, audio_id: UUID) -> bool:
        """音声ファイルを削除"""
        file_path = self._get_file_path(audio_id)

        try:
            if await aiofiles.ospath.exists(file_path):
                await aiofiles.os.remove(file_path)
                await self.metadata_repo.delete_metadata(audio_id)
                return True
        except OSError:
            # ベストエフォートに従ってエラーをパス
            pass

        return False

    async def exists(self, audio_id: UUID) -> bool:
        """音声ファイルの存在を確認"""
        file_path = self._get_file_path(audio_id)
        return await aiofiles.os.path.exists(file_path)

    async def get_metadata(self, audio_id: UUID) -> AudioMetadata | None:
        """メタデータを取得"""
        return await self.metadata_repo.get_metadata(audio_id)
