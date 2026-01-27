from io import BytesIO
from typing import BinaryIO
from uuid import UUID, uuid4

from app.reference_audio.validator import AudioValidator
from app.storage.base import AudioMetadata, AudioStorage


class ReferenceAudioService:
    """リファレンス音声の管理サービス"""

    def __init__(self, storage: AudioStorage, validator: AudioValidator) -> None:
        self.storage = storage
        self.validator = validator

    async def upload(
        self, file: BinaryIO, filename: str, content_type: str
    ) -> AudioMetadata:
        """リファレンス音声をアップロード

        Args:
            file: 音声ファイルのバイナリストリーム
            filename: ファイル名
            content_type: MIMEタイプ

        Retaruns:
            AudioMetadata: アップロードされた音声のメタデータ

        Raises:
            ValueError: バリデーションエラー
        """
        content = file.read()
        file_obj = BytesIO(content)

        validation_result = await self.validator.validate(
            file_obj, filename, content_type
        )

        if not validation_result.is_valid:
            raise ValueError(
                f"オーディオ検証エラー: {', '.join(validation_result.errors)}"
            )

        audio_id = uuid4()
        metadata = AudioMetadata(
            id=audio_id,
            filename=filename,
            content_type=content_type,
            size_bytes=len(content),
            sample_rate=validation_result.sample_rate,
            duration_seconds=validation_result.duration_seconds,
        )

        file_obj.seek(0)
        await self.storage.save(file_obj, metadata)

        return metadata

    async def get(self, audio_id: UUID) -> tuple[bytes, AudioMetadata]:
        """リファレンス音声を取得

        Args:
            audio_id: 音声ID

        Returns:
            音声データとメタデータ

        Raises:
            FileNotFoundError: 音声が見つからない
        """
        audio_data = await self.storage.load(audio_id)
        metadata = await self.storage.get_metadata(audio_id)

        if metadata is None:
            raise FileNotFoundError(
                f"音声のメタデータが見つかりませんでした。: {audio_id}"
            )

        return audio_data, metadata

    async def delete(self, audio_id: UUID) -> bool:
        """リファレンス音声を削除

        Args:
            audio_id: 音声ID

        Returns:
            削除が成功したかどうか
        """
        return await self.storage.delete(audio_id)

    async def list_all(self) -> list[AudioMetadata]:
        """
        すべてのリファレンス音声のメタデータを取得

        Returns:
            list[AudioMetadata]: メタデータのリスト
        """
        # ストレージがlist機能を持っている場合
        if hasattr(self.storage, "metadata_repo"):
            return await self.storage.metadata_repo.list_metadata()

        raise NotImplementedError("List operation not supported by this storage")
